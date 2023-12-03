
import pygame
import torch

from abc import ABC, abstractclassmethod
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

from pygame.locals import K_SPACE, K_UP, KEYDOWN

from .ai import BEST_MODEL_PATH
from .ai.model import FF
from .entities import Flappy, Pipes, Floor, FlappyMode
from .utils import GameConfig


class PlayerAction(Enum):
    NOTHING = auto()
    JUMP = auto()

class PlayerState(Enum):
    DEAD = auto()
    ALIVE = auto()

class Player(ABC):
    def __init__(self, config:GameConfig):
        self.config = config
        self.action = PlayerAction.NOTHING
        self.state = PlayerState.ALIVE
        self.flappy = Flappy(config)
        self.score = 0

    @abstractclassmethod
    def process_event(self, event) -> None:
        ...

    def make_a_play(self, pipes:Pipes) -> None:
        if self.action is PlayerAction.JUMP:
            self.flappy.flap()
        self.action = PlayerAction.NOTHING

    def check_colision(self, pipes:Pipes, floor:Floor) -> bool:
        return self.flappy.collided(pipes, floor)

    def check_crossed_pipe(self, pipes:Pipes) -> bool:
        return self.flappy.crossed(pipes)

    def crash(self) -> None:
        if self.state is PlayerState.ALIVE:
            self.flappy.set_mode(FlappyMode.CRASH)
            self.state = PlayerState.DEAD
    
    def scored(self) -> None:
        self.score += 1

    def reset(self) -> None:
        self.__init__(self.config)

    def tick(self):
        self.flappy.tick()

class HumanPlayer(Player):
    def __init__(self, config:GameConfig):
        super().__init__(config)
        self.player_state = PlayerAction.NOTHING

    def process_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        
        self.action = PlayerAction.JUMP if m_left or space_or_up or screen_tap else PlayerAction.NOTHING

class FFPlayer(Player):
    ### Feed Forward Neural Network Player
    def __init__(self, config:GameConfig, chromosome:Optional[torch.Tensor]=None):
        super().__init__(config)
        self.player_state = PlayerAction.NOTHING
        self.nn = FF(chromosome)

    def process_event(self, event) -> None:
        # AI won't use any keyboard events to play, so we just return
        return
    
    def make_a_play(self, pipes:Pipes) -> None:
        # Overload the make_a_play method, since the ai need to decide once per frame if it should jump or not
        _normalize = lambda values, reference: [v - reference for v in values]
        pipes_x = _normalize([p.x+p.w/2 for p in pipes.lower], self.flappy.x)
        pp_idx = [idx for idx,val in enumerate(pipes_x) if val>0] # index of the next pipe
        if len(pp_idx) > 0:
            pp_idx = pp_idx[0]
            nn_input = torch.tensor([
                self.flappy.y,          # Flappy Y coord 
                pipes.lower[pp_idx].x,  # Bottom pipe X coord
                pipes.lower[pp_idx].y,  # Bottom pipe Y coord
                pipes.upper[pp_idx].x,  # Top pipe X coord
                pipes.upper[pp_idx].y   # Top pipe Y coord
            ], dtype=torch.float32)
        else:
            nn_input = torch.tensor([
                self.flappy.y,          # Flappy Y coord 
                self.config.window.viewport_width,  # Bottom pipe X coord
                self.config.window.viewport_height,  # Bottom pipe Y coord
                self.config.window.viewport_width,  # Top pipe X coord
                0   # Top pipe Y coord
            ], dtype=torch.float32)
        activation = self.nn(nn_input).item()
        self.action = PlayerAction.JUMP if activation > 0.5 else PlayerAction.NOTHING
        return super().make_a_play(pipes)

    def export_chromosome(self) -> torch.Tensor:
        return self.nn.to_chromosome()

    def load_chromosome(self, chromosome:torch.Tensor) -> None:
        self.nn.load_chromosome(chromosome)

    def save(self) -> None:
        torch.save(self.nn.state_dict(), BEST_MODEL_PATH)

    def load_best(self) -> bool:
        if BEST_MODEL_PATH.exists():
            self.nn.load_state_dict(torch.load(BEST_MODEL_PATH))
        else:
            from tkinter import messagebox, Tk
            Tk().wm_withdraw() #to hide the main window
            messagebox.showinfo('Warning', 'No previous model was found, starting training from scratch')
            return False
        return True

    def get_last_state(self) -> dict[str, Any]:
        return {
            'wb': {key: value.detach().numpy().copy() for key, value in self.nn.chromosome2dict(self.nn.to_chromosome()).items()},
            'last_activations': self.nn.last_activations}

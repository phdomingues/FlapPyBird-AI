from enum import Enum, auto
import pygame

from abc import ABC, abstractclassmethod

from pygame.locals import K_SPACE, K_UP, KEYDOWN
from utils import GameConfig

from .entities import Score, Flappy, Pipes, Floor, FlappyMode
from .utils import GameConfig

class PlayerAction(Enum):
    NOTHING = auto()
    JUMP = auto()

class PlayerState(Enum):
    DEAD = auto()
    ALIVE = auto()

class Player(ABC):
    def __init__(self, config:GameConfig):
        self.action = PlayerAction.NOTHING
        self.state = PlayerState.ALIVE
        self.flappy = Flappy(config)
        self.score = 0

    @abstractclassmethod
    def process_event(self, event) -> None:
        ...

    def make_a_play(self) -> None:
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

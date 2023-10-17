from enum import Enum, auto
import pygame

from abc import ABC, abstractclassmethod

from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT
from utils import GameConfig

from .entities import Score, Flappy, Pipes, Floor, FlappyMode
from .utils import GameConfig

class PlayerAction(Enum):
    NOTHING = auto()
    JUMP = auto()

class Player(ABC):
    def __init__(self, config:GameConfig):
        self.score = Score(config)
        self.flappy = Flappy(config)

    @abstractclassmethod
    def make_a_play(self) -> PlayerAction:
        ...
    
    @abstractclassmethod
    def process_event(self, event) -> None:
        ...
    
    def check_colision(self, pipes:Pipes, floor:Floor) -> bool:
        return self.flappy.collided(pipes, floor)

    def check_crossed_pipe(self, pipes:Pipes) -> bool:
        return self.flappy.crossed(pipes)

    def crash(self) -> None:
        self.flappy.set_mode(FlappyMode.CRASH)

    def tick(self):
        self.score.tick()
        self.flappy.tick()

class HumanPlayer(Player):
    def __init__(self, config:GameConfig):
        super().__init__(config)
        self.player_state = PlayerAction.NOTHING

    def make_a_play(self):
        return

    def process_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        
        if m_left or space_or_up or screen_tap:
            self.flappy.flap()
    

class FlappyFactory:
    class FlappyType(Enum):
        PLAYER = auto()

    def create(flappy_type:FlappyType, config:GameConfig) -> Flappy:
        flappy_creator = {
            FlappyFactory.FlappyType.PLAYER: FlappyFactory._create_player
        }
        return flappy_creator[flappy_type](config)
    
    def _create_player(config:GameConfig):
        return FlappyPlayer(config)
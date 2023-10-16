from enum import Enum, auto
import pygame

from abc import ABC, abstractclassmethod

from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT
from utils import GameConfig

from .entities import Score
from .utils import GameConfig

class PlayerAction(Enum):
    NOTHING = auto()
    JUMP = auto()

class Flappy(ABC):
    def __init__(self):
        self.score = Score(self.config)

    @abstractclassmethod
    def make_a_play(self) -> PlayerAction:
        ...
    
    @abstractclassmethod
    def process_event(self) -> None:
        ...

class FlappyPlayer(Flappy):
    def __init__(self, config: GameConfig):
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
        
        self.player_state = PlayerAction.JUMP if m_left or space_or_up or screen_tap else PlayerAction.NOTHING
    

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
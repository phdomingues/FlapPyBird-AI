import os

import pygame

from ..flappy import Flappy
from .images import Images
from .sounds import Sounds
from .window import Window


class GameConfig:
    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        fps: int,
        window: Window,
        images: Images,
        sounds: Sounds,
        n_agents: int,
    ) -> None:
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.window = window
        self.images = images
        self.sounds = sounds
        self.n_agents = n_agents
        self.debug = os.environ.get("DEBUG", False)

    def tick(self) -> None:
        self.clock.tick(self.fps)

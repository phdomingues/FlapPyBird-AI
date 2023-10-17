import os

import pygame

from ..flappy import Flappy
from .images import Images
from .sounds import Sounds
from .window import Window


class TrainingConfig:
    def __init__(
        self,
        n_agents: int,

    ) -> None:
        self.n_agents = n_agents
        self.debug = os.environ.get("DEBUG", False)
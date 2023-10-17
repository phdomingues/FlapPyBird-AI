import asyncio
from enum import Enum, auto
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Flappy,
    FlappyMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window
from .player import Player, HumanPlayer


class Game:
    class GameMode(Enum):
        PLAY = auto()
        TRAIN = auto()

    def __init__(self, game_mode:GameMode):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.game_mode = game_mode
        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds()
        )

    async def start(self):
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            #self.score = Score(self.config)
            if self.game_mode is self.GameMode.PLAY:
                self.players = [HumanPlayer(self.config)]
            #elif self.game_mode is self.GameMode.TRAIN:
                #self.players = [Flappy(self.config) for _ in range(self.config.n_agents)]
            else:
                print("Error: Invalid game mode")
                exit(100)
            # await self.splash()
            await self.play()
            await self.game_over()

    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""
    
        self.player.set_mode(FlappyMode.SHM)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            for agent in self.agents:
                agent.tick()
            #self.player.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    async def play(self):
        for player in self.players:
            player.score.reset()
            player.flappy.set_mode(FlappyMode.NORMAL)

        while True:
            current_events = []
            for event in pygame.event.get():
                self.check_quit_event(event)
                current_events.append(event)

            for player in self.players:
                if player.check_colision(self.pipes, self.floor):
                    player.crash()
                for _, pipe in enumerate(self.pipes.upper):
                    if player.check_crossed_pipe(pipe):
                        player.score.add()
                for event in current_events:
                    player.process_event(event)
                

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            for player in self.players:
                player.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def train(self):
        return

    async def game_over(self):
        """crashes the player down and shows gameover image"""
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)

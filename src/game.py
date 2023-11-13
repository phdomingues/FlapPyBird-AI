import asyncio
from enum import Enum, auto
import sys

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    FlappyMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window
from .player import FFPlayer, HumanPlayer, PlayerState
from ai import N_TRAINING_AGENTS


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
            self.score = Score(self.config)
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            if self.game_mode is self.GameMode.PLAY:
                self.players = [HumanPlayer(self.config)]
            elif self.game_mode is self.GameMode.TRAIN:
                self.players = [FFPlayer(self.config) for _ in range(N_TRAINING_AGENTS)]
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
            player.flappy.set_mode(FlappyMode.NORMAL)

        while True:
            current_events = []
            scored = False
            death_count = 0

            for event in pygame.event.get():
                self.check_quit_event(event)
                current_events.append(event)

            for player in self.players:
                if player.state is PlayerState.DEAD:
                    death_count += 1
                    continue
                if player.check_colision(self.pipes, self.floor):
                    player.crash()
                for _, pipe in enumerate(self.pipes.upper):
                    # Check if crossed pipe or if other player already scored (this avoid the checking multiple times since all players have the same X coordinate)
                    if scored or player.check_crossed_pipe(pipe):
                        player.scored() # just set scored to True, its not cummulative
                        scored = True

                for event in current_events:
                    player.process_event(event)

                # Allow player to execute a single action (jump or not) depending on the events he processed
                player.make_a_play(self.pipes)
                
            if scored:
                self.score.add()
                scored = False
            
            if death_count == len(self.players):
                return
            else:
                death_count = 0
    
            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
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
                #if self.is_tap_event(event):
                #    if self.player.y + self.player.h >= self.floor.y - 1:
                #        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            for player in self.players:
                player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)

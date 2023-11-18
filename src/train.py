import asyncio
import sys

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    Pipes,
    FlappyMode,
    Score,
)
from .utils import GameConfig, Images, Sounds, Window
from .player import FFPlayer, PlayerState


class TrainGA:
    def __init__(self, population_size:int=10):
        # Game configs
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()
        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds()
        )
        # GA configs
        self.generation = 1
        self.population_size = population_size
        self.population = [FFPlayer(self.config) for _ in range(self.population_size)]

    async def start(self):
        while True:
            self.score = Score(self.config)
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.pipes = Pipes(self.config)

            # Score population (fitness function)
            await self.play()

            # Keep best individual

            # Select parents based on fitness

            # Crossover

            # Mutation

            # Reset game
            await self.reset()



    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    async def play(self):
        for individual in self.population:
            individual.flappy.set_mode(FlappyMode.NORMAL)

        while True:
            current_events = []
            scored = False
            death_count = 0

            for event in pygame.event.get():
                self.check_quit_event(event)
                current_events.append(event)

            for individual in self.population:
                if individual.state is PlayerState.DEAD:
                    death_count += 1
                    continue
                if individual.check_colision(self.pipes, self.floor):
                    individual.crash()
                for _, pipe in enumerate(self.pipes.upper):
                    # Check if crossed pipe or if other individual already scored (this avoid the checking multiple times since all individuals have the same X coordinate)
                    if scored or individual.check_crossed_pipe(pipe):
                        individual.scored() # just set scored to True, its not cummulative
                        scored = True

                for event in current_events:
                    individual.process_event(event)

                # Allow individual to execute a single action (jump or not)
                individual.make_a_play(self.pipes)
                
            if scored:
                self.score.add()
                scored = False
            
            if death_count == self.population_size:
                return
            else:
                death_count = 0
    
            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            for individual in self.population:
                individual.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def reset(self):
        self.pipes.stop()
        self.floor.stop()
        self.background.tick()
        self.floor.tick()
        self.pipes.tick()
        self.score.tick()
        for individual in self.population:
            individual.tick()
            individual.reset()
        self.config.tick()
        pygame.display.update()
        #await asyncio.sleep(0)
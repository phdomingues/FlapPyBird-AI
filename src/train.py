import asyncio
import sys

import numpy as np
import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT
import torch

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
    def __init__(self, population_size:int=100):
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

            # === Score population (fitness function)
            await self.play()
            scores = np.array([ind.score for ind in self.population])

            # === Track best individual
            best_individual = self.population[scores.argmax()]

            # === Select parents based on fitness
            # Normalize the scores
            scores_norm = scores/scores.sum()
            # Generate a accumulated sum of the normalized scores
            scores_norm = np.cumsum(scores_norm)
            # Elitism
            new_population = [FFPlayer(self.config, best_individual.export_chromosome())]
            # Randomly (uniform) select the parents
            while len(new_population) != len(self.population):
                # Get 2 parents randomly (save the indexes)
                parents = [self.population[np.argmax(scores_norm > np.random.uniform())] for _ in range(2)]
                # === Crossover
                new_chromosome = self.crossover(*parents)
                # === Mutation
                self.mutate(new_chromosome)
                new_population.append(FFPlayer(self.config, chromosome=new_chromosome))

            # === Kill old population
            for individual in self.population[::-1]:
                del individual
            # === Replace the population
            self.population = new_population

            # TODO: Save best model to file
            # TODO: Stop condition (time or max score)
            # TODO: Fix score display
            # TODO: Animate (matplotlib probably) the best network structure + activations
            # TODO: Create a control slider, to set tick speed

            # === Reset game
            await self.reset()

    def crossover(self, parent1:FFPlayer, parent2:FFPlayer) -> torch.Tensor:
        p1_chromosome = parent1.export_chromosome()
        p2_chromosome = parent2.export_chromosome()
        genes_division = np.random.randint(low=0, high=2, size=len(p1_chromosome)) # High is not inclusive so this is actually a random binary array
        son_chromosome = [p1_chromosome[gene].item() if selected_parent%2 else p2_chromosome[gene].item() for gene, selected_parent in enumerate(genes_division)]
        return torch.Tensor(son_chromosome).type(p1_chromosome.dtype)

    def mutate(self, chromosome:torch.Tensor, mutation_chance:float=0.1, mutation_std_dev:float=0.01):
        random_selection = np.random.uniform(size=len(chromosome))
        genes_to_mutate = random_selection < mutation_chance
        for mutate, gene in zip(genes_to_mutate, range(len(chromosome))):
            if mutate:
                # Mutation adds or subtracts a random value from a normal distribution (mean=0, std_dev=user_defined)
                chromosome[gene] += np.random.normal(0, mutation_std_dev)

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
                    if individual.check_crossed_pipe(pipe):
                        individual.scored() # just set scored to True, its not cummulative

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
                if individual.state == PlayerState.ALIVE:
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
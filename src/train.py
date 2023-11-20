import asyncio
from pathlib import Path
import sys
import time
import yaml

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
from .ai import AI_CONFIG_PATH


class TrainGA:
    def __init__(self):
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
        with AI_CONFIG_PATH.open('r') as f:
            self.ga_configs = yaml.safe_load(f)
        self.generation = 0
        self.population_size = self.ga_configs.get('population_size', 200)
        self.population = [FFPlayer(self.config) for _ in range(self.population_size)]
        if self.ga_configs.get('load_previous_best', True):
            for ind in self.population:
                success = ind.load_best()
                if not success:
                    break # just stop loading and keep the randomly initialized networks

    async def start(self):
        start = time.time()
        while True:
            self.generation+=1
            self.score = Score(self.config)
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.pipes = Pipes(self.config)

            # === Score population (fitness function)
            await self.play()
            scores = np.array([ind.score for ind in self.population])

            # === Track best individual
            self.best_individual = self.population[scores.argmax()]

            # === Select parents based on fitness
            # Normalize the scores
            scores_norm = scores/scores.sum()
            # Generate a accumulated sum of the normalized scores
            scores_norm = np.cumsum(scores_norm)
            # Elitism
            new_population = []
            if self.ga_configs.get('elitism', True):
                new_population.append(FFPlayer(self.config, self.best_individual.export_chromosome()))
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
            # TODO: Stop condition - check every N ticks to be more dynamic
            # TODO: Animate (matplotlib probably) the best network structure + activations
            # TODO: Create a control slider, to set tick speed
            # TODO: Increase dificulty

            # === Stop condition
            generation_condition = self.generation >= self.ga_configs.get('stop_condition', {}).get('generations', float('inf'))
            score_condition = self.best_individual.score >= self.ga_configs.get('stop_condition', {}).get('score', float('inf'))
            time_condition = time.time() - start > self.ga_configs.get('stop_condition', {}).get('time', float('inf'))
            if generation_condition or score_condition or time_condition:
                return

            # === Reset game
            await self.reset()

    def crossover(self, parent1:FFPlayer, parent2:FFPlayer) -> torch.Tensor:
        p1_chromosome = parent1.export_chromosome()
        p2_chromosome = parent2.export_chromosome()
        genes_division = np.random.randint(low=0, high=2, size=len(p1_chromosome)) # High is not inclusive so this is actually a random binary array
        son_chromosome = [p1_chromosome[gene].item() if selected_parent%2 else p2_chromosome[gene].item() for gene, selected_parent in enumerate(genes_division)]
        return torch.Tensor(son_chromosome).type(p1_chromosome.dtype)

    def mutate(self, chromosome:torch.Tensor):
        random_selection = np.random.uniform(size=len(chromosome))
        genes_to_mutate = random_selection < self.ga_configs.get('mutation_probability', 0.05)
        for mutate, gene in zip(genes_to_mutate, range(len(chromosome))):
            if mutate:
                # Mutation adds or subtracts a random value from a normal distribution (mean=0, std_dev=user_defined)
                chromosome[gene] += np.random.normal(0, self.ga_configs.get('mutation_standard_deviation', 0.3))

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            try:
                self.best_individual.save() # Save the best individual state dict in a file
            except AttributeError:
                pass
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
                    if individual.check_crossed_pipe(pipe):
                        individual.scored() # just set scored to True, its not cummulative
                        scored=True

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
        self.config.tick()
        pygame.display.update()
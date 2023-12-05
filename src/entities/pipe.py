import random
import time
from typing import List

from ..utils import GameConfig
from .entity import Entity


class Pipe(Entity):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vel_x = -5
        self.max_speed = -30
    
    def set_vel_x(self, vel_x):
        self.vel_x = max(self.max_speed, vel_x)

    def draw(self) -> None:
        self.x += self.vel_x
        super().draw()


class Pipes(Entity):
    upper: List[Pipe]
    lower: List[Pipe]

    def __init__(self, config: GameConfig, acceleration: bool=False) -> None:
        super().__init__(config)
        # Constants
        self.pipe_gap = 120
        self.max_vel_x = -10
        self.min_spawn_time = 700
        self.x_acceleration = -0.2 if acceleration else 0
        self.spawn_acceleration = -60 if acceleration else 0
        self.top = 0
        self.bottom = self.config.window.viewport_height
        # Variables
        self.pipe_vel_x = -5
        self._set_spawn_time(1500)
        self.last_spawn = -1
        self.upper = []
        self.lower = []
    
    def _set_pipe_vel_x(self, vel_x):
        self.pipe_vel_x = max(self.max_vel_x, vel_x) # max because speed is negative

    def _set_spawn_time(self, spawn_time):
        self.spawn_time = max(self.min_spawn_time, spawn_time)

    def _update_timings(self):
        self._set_pipe_vel_x(self.pipe_vel_x+self.x_acceleration)
        self._set_spawn_time(self.spawn_time+self.spawn_acceleration)
        

    def tick(self) -> None:
        if self.can_spawn_pipes():
            self.last_spawn = time.time()*1000
            self.spawn_new_pipes()
        self.remove_old_pipes()

        for up_pipe, low_pipe in zip(self.upper, self.lower):
            up_pipe.tick()
            low_pipe.tick()

    def stop(self) -> None:
        for pipe in self.upper + self.lower:
            pipe.vel_x = 0

    def can_spawn_pipes(self) -> bool:
        now_ms = time.time() * 1000
        return now_ms - self.last_spawn > self.spawn_time

    def spawn_new_pipes(self):
        # add new pipe when first pipe is about to touch left of screen
        upper, lower = self.make_random_pipes()
        self.upper.append(upper)
        self.lower.append(lower)
        # Update the speed
        self._update_timings()

    def remove_old_pipes(self):
        # remove first pipe if its out of the screen
        for pipe in self.upper:
            if pipe.x < -pipe.w:
                self.upper.remove(pipe)

        for pipe in self.lower:
            if pipe.x < -pipe.w:
                self.lower.remove(pipe)

    def make_random_pipes(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        base_y = self.config.window.viewport_height

        gap_y = random.randrange(0, int(base_y * 0.6 - self.pipe_gap))
        gap_y += int(base_y * 0.2)
        pipe_height = self.config.images.pipe[0].get_height()
        pipe_x = self.config.window.width + 10

        upper_pipe = Pipe(
            self.config,
            self.config.images.pipe[0],
            pipe_x,
            gap_y - pipe_height,
        )
        upper_pipe.set_vel_x(self.pipe_vel_x)

        lower_pipe = Pipe(
            self.config,
            self.config.images.pipe[1],
            pipe_x,
            gap_y + self.pipe_gap,
        )
        lower_pipe.set_vel_x(self.pipe_vel_x)

        return upper_pipe, lower_pipe

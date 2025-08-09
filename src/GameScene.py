from abc import ABC, abstractmethod
from typing import final

from src.Settings import Settings
import pygame


class GameScene(ABC):
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, settings: Settings):
        self.surface: pygame.Surface = surface
        self.clock: pygame.time.Clock = clock
        self.settings: Settings = settings
        self.delta_time: float = 0.0

    @final
    def tick(self):
        self.delta_time = self.clock.tick(self.settings.max_fps)
        return self.delta_time

    @abstractmethod
    def game_loop(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self):
        pass
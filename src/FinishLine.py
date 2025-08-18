import os, pygame

from src import config
from src.StartLine import StartLine
from src.Vector2 import Vector2


class FinishLine(StartLine):

    def __init__(self, pos: Vector2):
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'finish.png')).convert_alpha()
        super().__init__(pos, sprite)

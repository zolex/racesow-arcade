import os, pygame

from src.Camera import Camera
from src import config
from src.GameObject import GameObject
from src.SimpleRect import SimpleRect
from src.StartLine import StartLine
from src.Vector2 import Vector2


class FinishLine(StartLine):

    def __init__(self, pos: Vector2):
        super().__init__(pos)
        self.sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'finish.png')).convert_alpha()

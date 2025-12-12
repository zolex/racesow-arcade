import os, pygame

from src import config
from src.Item.StartLine import StartLine


class FinishLine(StartLine):

    def __init__(self, x, y):
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'finish.png')).convert_alpha()
        super().__init__(x, y, sprite)

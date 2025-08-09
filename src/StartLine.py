import os, pygame

from src.Camera import Camera
from src import config
from src.GameObject import GameObject
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2


class StartLine(GameObject):

    def __init__(self, pos: Vector2, sprite: pygame.Surface = None, scale: float = 1.0):
        self.scale = scale
        self.sprite = sprite if sprite is not None else pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'start.png')).convert_alpha()
        if scale != 1:
            self.sprite = pygame.transform.scale(self.sprite, (self.sprite.get_width() * scale, self.sprite.get_height() * scale))
        super().__init__(SimpleRect(pos, self.sprite.get_width(), self.sprite.get_height()))

        self.bbox = (self.pos.x, self.pos.y, self.pos.x + self.shape.w, self.pos.y + self.shape.w)

    def draw_back(self, surface: pygame.Surface, camera: Camera):
        view_pos = camera.to_view_space(self.pos)
        back = self.sprite.subsurface((0, 0, 10 * self.scale, 128 * self.scale)).copy()
        surface.blit(back, (view_pos.x, view_pos.y, 30, self.shape.h))

    def draw_front(self, surface: pygame.Surface, camera: Camera):
        view_pos = camera.to_view_space(self.pos)
        back = self.sprite.subsurface((10 * self.scale, 0 * self.scale, 55 * self.scale, 128 * self.scale)).copy()
        surface.blit(back, (view_pos.x + 10 * self.scale, view_pos.y, 55 * self.scale, self.shape.h))

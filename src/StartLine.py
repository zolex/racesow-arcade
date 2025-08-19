import os, pygame

from src import config

class StartLine(pygame.Rect):

    def __init__(self, x, y, sprite: pygame.Surface = None, scale: float = 1.0):
        self.scale = scale
        self.sprite = sprite if sprite is not None else pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'start.png')).convert_alpha()
        if scale != 1:
            self.sprite = pygame.transform.scale(self.sprite, (self.sprite.get_width() * scale, self.sprite.get_height() * scale))
        super().__init__(x, y, self.sprite.get_width(), self.sprite.get_height())

        self.bbox = (self.x, self.y, self.x + self.w, self.y + self.w)

    def draw_back(self, surface: pygame.Surface, camera):
        view_pos = camera.to_view_space(self)
        back = self.sprite.subsurface((0, 0, 10 * self.scale, 128 * self.scale)).copy()
        surface.blit(back, (view_pos.x, view_pos.y, 30, self.h))

    def draw_front(self, surface: pygame.Surface, camera):
        view_pos = camera.to_view_space(self)
        back = self.sprite.subsurface((10 * self.scale, 0 * self.scale, 55 * self.scale, 128 * self.scale)).copy()
        surface.blit(back, (view_pos.x + 10 * self.scale, view_pos.y, 55 * self.scale, self.h))

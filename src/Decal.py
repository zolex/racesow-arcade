import pygame, os
from src.Vector2 import Vector2
from src import config

def pre_load_decals():
    for decal in ['dash1', 'dash2', 'rocket', 'plasma']:
        Decal.types[decal] = pygame.image.load(os.path.join(config.assets_folder, 'graphics', f'decal_{decal}.png')).convert_alpha()

class Decal(Vector2):

    types = {}

    def __init__(self, type: str, duration, x, y, center: bool = False, fade_out=False):
        super(Decal, self).__init__(x, y)
        self.duration = duration
        self.center = center
        self.fade_out = fade_out
        self.sprite = Decal.types[type]
        self.start_time = pygame.time.get_ticks()

    def draw(self, surface, camera):
        view_pos = camera.to_view_space(Vector2(self.x, self.y))
        if self.center:
            pos = (view_pos.x - self.sprite.get_width() / 2, view_pos.y - self.sprite.get_height() / 2)
        else:
            pos = (view_pos.x, view_pos.y)

        if self.fade_out:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.start_time
            progress = min(1.0, elapsed_time / self.duration)
            alpha = 255 - int(255 * progress)
            self.sprite.set_alpha(alpha)

        surface.blit(self.sprite, pos)

    def is_expired(self):
        return self.start_time + self.duration < pygame.time.get_ticks()
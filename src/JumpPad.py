import os, pygame

from src import config
from src.Vector2 import Vector2

class JumpPad(pygame.Rect):

    WIDTH = 64
    HEIGHT = 21

    def __init__(self, x, y, vel: Vector2 = Vector2(0, -0.7), scale: float = 1.0):
        super().__init__(x, y, self.WIDTH * scale, self.HEIGHT * scale)
        self.jumped_at = float("-inf")
        self.vel = vel
        self.x += self.w // 2 + (32 * scale)
        self.y += self.h
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'jumppad.png')).convert_alpha()
        new_size = (sprite.get_width() / 2 * scale, sprite.get_height() / 2 * scale)
        self.sprite = pygame.transform.smoothscale(sprite, new_size)
        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'jumppad.mp3'))

    def draw(self, surface: pygame.Surface, camera):

        view_pos = camera.to_view_space(self)
        surface.blit(self.sprite, (view_pos.x, view_pos.y, self.w, self.h))

    def jump(self, player):
        if self.jumped_at + 1000 < pygame.time.get_ticks():
            player.action_states.on_event('jump')
            player.released_jump = True
            self.jumped_at = pygame.time.get_ticks()
            self.sound.play()
            player.vel.x += self.vel.x
            player.vel.y = -self.vel.y

import os, pygame

from src.Camera import Camera
from src import config
from src.GameObject import GameObject
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2


class JumpPad(GameObject):

    WIDTH = 64
    HEIGHT = 21

    def __init__(self, pos: Vector2, vel: Vector2 = Vector2(0, -0.7)):
        super().__init__(SimpleRect(pos, self.WIDTH, self.HEIGHT))
        self.jumped_at = float("-inf")
        self.vel = vel
        self.pos.x += self.shape.w // 2 + 32
        self.pos.y += self.shape.h
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'jumppad.png')).convert_alpha()
        new_size = (sprite.get_width() / 2, sprite.get_height() / 2)
        self.sprite = pygame.transform.smoothscale(sprite, new_size)
        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'jumppad.mp3'))

    def draw(self, surface: pygame.Surface, camera: Camera):

        view_pos = camera.to_view_space(self.pos)
        surface.blit(self.sprite, (view_pos.x, view_pos.y, self.shape.w, self.shape.h))

    def jump(self, player):
        if self.jumped_at + 1000 < pygame.time.get_ticks():
            self.jumped_at = pygame.time.get_ticks()
            self.sound.play()
            player.vel.x += self.vel.x
            player.vel.y = -self.vel.y

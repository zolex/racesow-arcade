import os, pygame

from src.Camera import Camera
from src import config
from src.GameObject import GameObject
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2


class Portal(GameObject):

    WIDTH = 64
    HEIGHT = 64
    FRAME_TIME = 25
    FRAMES_ENTRY = [
        (0 * WIDTH, 2 * HEIGHT, WIDTH, HEIGHT),
        (3 * WIDTH, 1 * HEIGHT, WIDTH, HEIGHT),
        (2 * WIDTH, 1 * HEIGHT, WIDTH, HEIGHT),
        (1 * WIDTH, 1 * HEIGHT, WIDTH, HEIGHT),
        (0 * WIDTH, 1 * HEIGHT, WIDTH, HEIGHT),
        (3 * WIDTH, 0 * HEIGHT, WIDTH, HEIGHT),
        (2 * WIDTH, 0 * HEIGHT, WIDTH, HEIGHT),
        (1 * WIDTH, 0 * HEIGHT, WIDTH, HEIGHT),
        (0 * WIDTH, 0 * HEIGHT, WIDTH, HEIGHT),
    ]

    FRAMES_EXIT = [
        (0 * WIDTH, 5 * HEIGHT, WIDTH, HEIGHT),
        (3 * WIDTH, 4 * HEIGHT, WIDTH, HEIGHT),
        (2 * WIDTH, 4 * HEIGHT, WIDTH, HEIGHT),
        (1 * WIDTH, 4 * HEIGHT, WIDTH, HEIGHT),
        (0 * WIDTH, 4 * HEIGHT, WIDTH, HEIGHT),
        (3 * WIDTH, 3 * HEIGHT, WIDTH, HEIGHT),
        (2 * WIDTH, 3 * HEIGHT, WIDTH, HEIGHT),
        (1 * WIDTH, 3 * HEIGHT, WIDTH, HEIGHT),
        (0 * WIDTH, 3 * HEIGHT, WIDTH, HEIGHT),
    ]

    def __init__(self, entry: Vector2, exit: Vector2):
        super().__init__(SimpleRect(entry, self.WIDTH, self.HEIGHT))
        self.exit = exit
        self.exit.x += self.shape.w // 2 + 12
        self.exit.y += self.shape.h
        self.pos.x += self.shape.w // 2 + 12
        self.pos.y += self.shape.h
        self.current_frame = 0
        self.anim_timer = 0
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'portal.png')).convert_alpha()
        new_size = (sprite.get_width() / 2, sprite.get_height() / 2)
        self.sprite = pygame.transform.smoothscale(sprite, new_size)
        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'teleport.mp3'))
        self.sound.set_volume(1)

        self.bbox = (min(self.pos.x, self.exit.x), min(self.pos.y, self.exit.y), max(self.pos.x, self.exit.x), max(self.pos.y, self.exit.y))

    def animate(self):
        self.anim_timer += config.delta_time
        if self.anim_timer > self.FRAME_TIME:
            self.anim_timer = 0
            self.current_frame += 1
            if self.current_frame == len(self.FRAMES_ENTRY) - 1:
                self.current_frame = 0

    def draw(self, surface: pygame.Surface, camera: Camera):
        self.animate()

        entry_sprite = self.sprite.subsurface(self.FRAMES_ENTRY[self.current_frame]).copy()
        entry_view_pos = camera.to_view_space(self.pos)
        surface.blit(entry_sprite, (entry_view_pos.x, entry_view_pos.y, self.shape.w, self.shape.h))

        exit_sprite = self.sprite.subsurface(self.FRAMES_EXIT[self.current_frame]).copy()
        exit_view_pos = camera.to_view_space(self.exit)
        surface.blit(exit_sprite, (exit_view_pos.x, exit_view_pos.y, self.shape.w, self.shape.h))

    def teleport(self, player):
        self.sound.play()
        player.pos.x = self.exit.x + 10
        player.pos.y = self.exit.y - 5
        if player.vel.x < 0.3:
            player.vel.x = 0.3
        if player.vel.y > 0:
            player.vel.y = 0
        player.camera.pos.x = self.exit.x - 30
        player.camera.pos.y = self.exit.y - player.height

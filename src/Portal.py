import os, pygame

from src.Camera import Camera
from src import config
from src.GameObject import GameObject
from src.Settings import Settings
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2


class Portal(GameObject):

    def __init__(self, entry: Vector2, exit: Vector2, settings: Settings):

        self.settings = settings
        SCALE = settings.get_scale()
        self.WIDTH = 64 * SCALE
        self.HEIGHT = 64 * SCALE
        self.FRAME_TIME = 25
        self.FRAMES_ENTRY = [
            (0 * self.WIDTH, 2 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (3 * self.WIDTH, 1 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (2 * self.WIDTH, 1 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (1 * self.WIDTH, 1 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (0 * self.WIDTH, 1 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (3 * self.WIDTH, 0 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (2 * self.WIDTH, 0 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (1 * self.WIDTH, 0 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (0 * self.WIDTH, 0 * self.HEIGHT, self.WIDTH, self.HEIGHT),
        ]

        self.FRAMES_EXIT = [
            (0 * self.WIDTH, 5 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (3 * self.WIDTH, 4 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (2 * self.WIDTH, 4 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (1 * self.WIDTH, 4 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (0 * self.WIDTH, 4 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (3 * self.WIDTH, 3 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (2 * self.WIDTH, 3 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (1 * self.WIDTH, 3 * self.HEIGHT, self.WIDTH, self.HEIGHT),
            (0 * self.WIDTH, 3 * self.HEIGHT, self.WIDTH, self.HEIGHT),
        ]


        super().__init__(SimpleRect(entry, self.WIDTH, self.HEIGHT))
        self.exit = exit
        self.exit.x += self.shape.w // 2 + 12
        self.exit.y += self.shape.h
        self.pos.x += self.shape.w // 2 + 12
        self.pos.y += self.shape.h
        self.current_frame = 0
        self.anim_timer = 0
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'portal.png')).convert_alpha()
        new_size = (sprite.get_width() / 2 * SCALE, sprite.get_height() / 2  * SCALE)
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
        player.vel.y = 0.001  # not 0 because it would cause the camera settling for the portal exit!
        scale = self.settings.get_scale()
        if player.vel.x < 0.3 * scale:
            player.vel.x = 0.3 * scale
        player.camera.stop_settling()
        player.camera.pos.x = self.exit.x - 30
        player.camera.pos.y = self.exit.y - self.settings.height // 2

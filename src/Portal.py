import os, pygame

from src import config
from src.Settings import Settings

class Portal(pygame.Rect):

    def __init__(self, x, y, flipped: bool, settings: Settings, exit = None):

        self.exit = exit
        self.settings = settings

        SCALE = settings.get_scale()
        self.WIDTH = 64 * SCALE
        self.HEIGHT = 64 * SCALE

        super().__init__(x + self.WIDTH, y + self.HEIGHT, self.WIDTH, self.HEIGHT)

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


        self.flipped = flipped
        self.current_frame = 0
        self.anim_timer = 0
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'portal.png')).convert_alpha()
        new_size = (sprite.get_width() / 2 * SCALE, sprite.get_height() / 2  * SCALE)
        self.sprite = pygame.transform.smoothscale(sprite, new_size)
        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'teleport.mp3'))
        self.sound.set_volume(1)

        self.bbox = (self.x, self.y, self.w, self.h)

    def animate(self):
        self.anim_timer += config.delta_time
        if self.anim_timer > self.FRAME_TIME:
            self.anim_timer = 0
            self.current_frame += 1
            if self.current_frame == len(self.FRAMES_ENTRY) - 1:
                self.current_frame = 0

    def draw(self, surface: pygame.Surface, camera):
        self.animate()

        if self.exit is not None:
            sprite = self.sprite.subsurface(self.FRAMES_ENTRY[self.current_frame]).copy()
        else:
            sprite = self.sprite.subsurface(self.FRAMES_EXIT[self.current_frame]).copy()
        entry_view_pos = camera.to_view_space(self)

        if self.flipped:
            sprite = pygame.transform.flip(sprite, True, False)

        surface.blit(sprite, (entry_view_pos.x, entry_view_pos.y, self.w, self.h))

    def teleport(self, player):

        if self.exit is None:
            return

        self.sound.play()
        player.x = self.exit.x + 10
        player.y = self.exit.y - 5
        player.vel.y = -0.0001  # not 0 because it would cause the camera settling for the portal exit!
        scale = self.settings.get_scale()

        if self.exit.flipped and player.direction == 1:
            player.direction = -1
            player.vel.x *= -1
            player.was_flipped = True
        elif not self.exit.flipped and player.direction == -1:
            player.direction = 1
            player.vel.x *= -1
            player.was_flipped = True

        if abs(player.vel.x) < 0.3 * scale:
            player.vel.x = 0.3 * scale * player.direction

        player.game.camera.stop_settling(player)
        player.game.camera.x = self.exit.x - 15 * scale * player.direction
        player.game.camera.y = self.exit.y - self.settings.resolution[1] // 2

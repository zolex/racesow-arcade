import os, pygame

from src import config
from src.Settings import Settings
from src.SpriteAnim import SpriteAnim
from src.SpriteSheet import SpriteSheet


class Portal(pygame.Rect):

    def __init__(self, x, y, flipped: bool, settings: Settings, exit = None):
        self.exit = exit
        self.settings = settings
        self.flipped = flipped
        scale = settings.get_scale()/2
        padding = (0, 32, 0, 30)
        type = 'entry' if self.exit is not None else 'exit'
        sprite_sheet = SpriteSheet(os.path.join(config.assets_folder, 'graphics', 'portals.png'), 128, 128, padding=padding, add_flipped=True, scale=scale)
        self.anim = SpriteAnim(sprite_sheet)
        if type == 'entry':
            self.anim.add('loop',[(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0)], fps=16)
        else:
            self.anim.add('loop', [(3, 0), (3, 1), (3, 2), (3, 3), (4, 0), (4, 1), (4, 2), (4, 3), (5, 0)], fps=16)

        self.anim.play('loop')
        frame, w, h = self.anim.get_frame()
        super().__init__(x + w + (padding[1] + padding[3]) * scale, y + h, w, h)

        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'teleport.mp3'))
        self.sound.set_volume(1)

    def draw(self, surface: pygame.Surface, camera):
        self.anim.update(config.delta_time, 1, -1)
        entry_view_pos = camera.to_view_space(self)
        frame, self.w, self.h = self.anim.get_frame(1 if self.flipped == False else -1)
        surface.blit(frame, (entry_view_pos.x, entry_view_pos.y, self.w, self.h))
        #pygame.draw.rect(surface, (0, 0, 0), (entry_view_pos.x, entry_view_pos.y, self.w, self.h), 1)

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

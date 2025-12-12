import os, pygame, math

from src import config
from src.World.Vector2 import Vector2

class JumpPad(pygame.Rect):

    WIDTH = 64
    HEIGHT = 21

    def __init__(self, x, y, vel: float = 0.7, rotation: float = 0.0, scale: float = 1.0, volume=1):
        super().__init__(x, y, self.WIDTH * scale, self.HEIGHT * scale)
        self.jumped_at = float("-inf")
        # store scalar velocity (strength) and rotation in degrees (0 = straight up)
        self.vel = vel
        self.rotation = rotation
        self.x += self.w // 2 + (32 * scale)
        self.y += self.h
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'jumppad.png')).convert_alpha()
        new_size = (sprite.get_width() / 2 * scale, sprite.get_height() / 2 * scale)
        self.sprite = pygame.transform.smoothscale(sprite, new_size)
        # Pre-rotate the sprite once during initialization (pygame uses CCW angles)
        self.rotated_sprite = pygame.transform.rotozoom(self.sprite, -float(self.rotation), 1.0)
        self.sound = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'jumppad.mp3'))
        self.sound.set_volume(volume)

    def draw(self, surface: pygame.Surface, camera):

        view_pos = camera.to_view_space(self)
        # Draw pre-rotated sprite centered on the pad's rect position on screen
        rect = self.rotated_sprite.get_rect(center=(view_pos.x + self.w / 2, view_pos.y + self.h / 2))
        surface.blit(self.rotated_sprite, rect.topleft)

    def jump(self, player):
        if self.jumped_at + 1000 < pygame.time.get_ticks():
            player.state.transition('Jump')
            player.released_jump = True
            self.jumped_at = pygame.time.get_ticks()
            self.sound.play()

            # Compute surface normal from rotation (0 deg = straight up). CCW-positive.
            rad = math.radians(-self.rotation)
            nx = math.sin(rad)
            ny = -math.cos(rad)
            # normalize just in case
            nlen = math.hypot(nx, ny)
            if nlen < 1e-6:
                # Fallback: default to straight up
                nx, ny = 0.0, -1.0
            else:
                nx /= nlen
                ny /= nlen

            vx, vy = player.vel.x, player.vel.y
            # Determine if the pad's push direction (its normal) goes against the player's velocity
            dot_to_normal = vx * nx + vy * ny
            min_push = max(0.0, float(self.vel))

            if dot_to_normal < 0.0:
                # Ignore player's velocity: use canonical entry=exit based solely on pad rotation
                vin_x, vin_y = 0.0, 1.0  # canonical incoming (falling straight down)
                dot_in = vin_x * nx + vin_y * ny
                rx = vin_x - 2.0 * dot_in * nx
                ry = vin_y - 2.0 * dot_in * ny
                # Normalize reflected direction and scale by strength
                rlen = math.hypot(rx, ry)
                if rlen < 1e-6:
                    # Fallback to using the normal if reflection is degenerate
                    rx, ry = nx, ny
                    rlen = 1.0
                player.vel.x = (rx / rlen) * min_push
                player.vel.y = (ry / rlen) * min_push
            else:
                # Use player's velocity with reflection and enforce a minimum push along the normal
                dot = vx * nx + vy * ny
                rx = vx - 2.0 * dot * nx
                ry = vy - 2.0 * dot * ny

                speed = math.hypot(rx, ry)
                if speed < 1e-6:
                    # If player was nearly stationary, launch along the normal with min_push
                    rx = nx * min_push
                    ry = ny * min_push
                else:
                    # Ensure outgoing normal component is at least min_push
                    normal_comp = rx * nx + ry * ny
                    if normal_comp < min_push:
                        add = (min_push - normal_comp)
                        rx += add * nx
                        ry += add * ny

                player.vel.x = rx
                player.vel.y = ry

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
        self.x += self.w / 2
        #self.y += self.h
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
            rad = math.radians(self.rotation)
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

            # Tangent (perpendicular) vector (right-handed): t = (ny, -nx)
            tx, ty = ny, -nx

            # Current velocity
            vx, vy = player.vel.x, player.vel.y

            # Decompose into normal and tangential components
            vn = vx * nx + vy * ny
            vt = vx * tx + vy * ty

            # Physics parameters: restitution for normal bounce, and tangential keep factor
            restitution = 0.6  # 0 = stick, 1 = perfect reflection
            tangential_keep = 0.9  # 1 = keep all tangential speed, <1 dampens slide

            # If player is moving into the pad (vn < 0), bounce with restitution
            if vn < 0.0:
                vn_out = -vn * restitution
            else:
                # Already moving away from the pad along the normal; keep it
                vn_out = vn

            # Ensure a minimum outward speed along the pad's normal based on pad strength
            min_push = max(0.0, float(self.vel))
            if vn_out < min_push:
                vn_out = min_push

            # Apply tangential damping to reduce sideways energy imparted by the pad
            vt_out = vt * tangential_keep

            # Recompose velocity from components
            rx = vn_out * nx + vt_out * tx
            ry = vn_out * ny + vt_out * ty

            # Handle nearly stationary total speed by forcing a launch strictly along normal
            if math.hypot(vx, vy) < 1e-6:
                rx = nx * min_push
                ry = ny * min_push

            player.vel.x = rx
            player.vel.y = ry

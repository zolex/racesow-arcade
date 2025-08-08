import pygame, os, math, random

from src.Decal import Decal
from src.Rectangle import Rectangle
from src.Triangle import Triangle
from src.Vector2 import Vector2
from src import config, sounds

def pre_load_projectiles():
    for projectile in ['rocket', 'plasma']:
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', f'projectile_{projectile}.png')).convert_alpha()
        Projectile.types[projectile] = pygame.transform.scale(sprite, (sprite.get_width() / 5, sprite.get_height() / 5))

class Projectile(Vector2):

    types = {}

    def __init__(self, type: str, duration, x, y, vel_x = 0, vel_y = 0, target_vel = 0, acc = 0, sound = None):
        super(Projectile, self).__init__(x, y)
        self.type = type
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.target_vel = target_vel
        self.acc = acc
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.sound = sound
        self.rotation = -math.degrees(math.atan2(vel_y, vel_x))
        self.sprite = pygame.transform.rotate(Projectile.types[type], self.rotation)

    def draw(self, surface, camera):
        view_pos = camera.to_view_space(Vector2(self.x, self.y))
        surface.blit(self.sprite, (view_pos.x, view_pos.y))

    def point_in_triangle(self, pt, t):
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

        b1 = sign(pt, t.p1, t.p2) < 0.0
        b2 = sign(pt, t.p2, t.p3) < 0.0
        b3 = sign(pt, t.p3, t.p1) < 0.0
        return (b1 == b2) and (b2 == b3)

    def volume_for_distance(self, distance):
        return min(1.1, max(0.05, 1.1 - (distance / 2674)))

    def get_distance(self, p1):
        dx = p1.x - self.x
        dy = p1.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def update(self, player, colliders):
        if self.start_time + self.duration < pygame.time.get_ticks():
            return True
        elif self.vel_x > 0 or self.vel_y > 0:
            self.x += self.vel_x * config.delta_time
            self.y += self.vel_y * config.delta_time
            if self.vel_x > self.target_vel:
                self.vel_x += self.acc * config.delta_time
            if self.vel_y > self.target_vel:
                self.vel_y += self.acc * config.delta_time
            if self.sound is not None:
                distance = self.get_distance(player.pos)
                self.sound.set_volume(self.volume_for_distance(distance))

            collider = self.check_collisions(colliders)
            if collider is not None:
                if self.type == 'rocket':
                    distance = self.get_distance(player.pos)
                    sounds.rocket.set_volume(self.volume_for_distance(distance))
                    sounds.rocket.play()
                    player.add_rocket_velocity(distance, math.atan2(player.pos.y - self.y, player.pos.x - self.x))
                    return Decal('rocket', 500, self.x, self.y, center=True, fade_out=True)

                elif self.type == 'plasma':
                    return Decal('plasma', 1000, self.x + random.randrange(-3, 3), self.y + random.randrange(-3, 3), center=False, fade_out=True)

        return False

    def check_collisions(self, collider_list):
        """Check collisions:
           - For Rectangle: usual AABB test
           - For Triangle: uses point_in_triangle function
           If collision is detected, returns the collider.
        """

        for collider in collider_list:
            if isinstance(collider.shape, Rectangle):
                if (collider.shape.pos.x < self.x < collider.shape.pos.x + collider.shape.w and
                        collider.shape.pos.y < self.y < collider.shape.pos.y + collider.shape.h):
                    if self.sound is not None:
                        self.sound.stop()
                    return collider
            elif isinstance(collider.shape, Triangle):
                # Assuming self.x and self.y represent the point to test
                class Pt:  # Minimal point object for compatibility
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                pt = Pt(self.x, self.y)
                if self.point_in_triangle(pt, collider.shape):
                    if self.sound is not None:
                        self.sound.stop()
                    return collider

        return None
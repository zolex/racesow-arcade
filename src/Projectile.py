import pygame, os, math, random

from src.Decal import Decal
from src.Rectangle import Rectangle
from src.Triangle import Triangle
from src.Vector2 import Vector2
from src import config, sounds

def pre_load_projectiles(SCALE:int = 1):
    for projectile in ['rocket', 'plasma']:
        sprite = pygame.image.load(os.path.join(config.assets_folder, 'graphics', f'projectile_{projectile}.png')).convert_alpha()
        Projectile.types[projectile] = pygame.transform.scale(sprite, (sprite.get_width() / 5 * SCALE, sprite.get_height() / 5 * SCALE))

class Projectile(Vector2):

    types = {}

    def __init__(self, type: str, duration: float, x: float, y: float, vel_x: float = 0.0, vel_y: float = 0.0, target_vel: float = 0.0, acc: float = 0.0, sound: pygame.mixer.Sound = None, collide_with: str|list[str] = ['static', 'ramp']):
        super(Projectile, self).__init__(x, y)
        self.type: str = type
        self.vel_x: float = vel_x
        self.vel_y: float = vel_y
        self.target_vel: float = target_vel
        self.acc: float = acc
        self.duration: float = duration
        self.start_time: int = pygame.time.get_ticks()
        self.sound: pygame.mixer.Sound = sound
        self.collide_with: list[str] = isinstance(collide_with, list) and collide_with or [collide_with]
        self.rotation: float = -math.degrees(math.atan2(vel_y, vel_x))
        self.sprite: pygame.Surface = pygame.transform.rotate(Projectile.types[type], self.rotation)

    def draw(self, surface, camera):
        view_pos = camera.to_view_space(self)
        surface.blit(self.sprite, (view_pos.x, view_pos.y))

        #pygame.draw.rect(surface, (0, 0, 0), (view_pos.x, view_pos.y, self.sprite.get_width(), self.sprite.get_height()), 1)

    def volume_for_distance(self, distance):
        return min(1.1, max(0.05, 1.1 - (distance / 2674)))

    def get_distance(self, p1):
        dx = p1.x - self.x
        dy = p1.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def update(self, map):
        if self.start_time + self.duration < pygame.time.get_ticks():
            return True
        elif self.vel_x != 0 or self.vel_y != 0:
            self.x += self.vel_x * config.delta_time
            self.y += self.vel_y * config.delta_time
            if self.vel_x > self.target_vel:
                self.vel_x += self.acc * config.delta_time
            if self.vel_y > self.target_vel:
                self.vel_y += self.acc * config.delta_time
            if self.sound is not None:
                distance = self.get_distance(map.game.player)
                self.sound.set_volume(self.volume_for_distance(distance))

            colliders = []
            for list in self.collide_with:
                if list == 'static':
                    colliders += map.static_colliders
                elif list == 'ramp':
                    colliders += map.ramp_colliders
                elif list == 'wall':
                    colliders += map.wall_colliders

            collider = self.check_collisions(colliders)
            if collider is not None:
                if self.type == 'rocket':
                    distance = self.get_distance(map.game.player)
                    sounds.rocket.set_volume(self.volume_for_distance(distance))
                    sounds.rocket.play()
                    offset_x = config.ROCKET_DOWN_OFFSET_X * map.game.settings.get_scale()
                    map.game.player.add_rocket_velocity(distance, math.atan2(map.game.player.y - self.y, map.game.player.x - self.x + offset_x))
                    return Decal('rocket', 500, self.x + offset_x, self.y, center=True, fade_out=True)

                elif self.type == 'plasma':
                    if collider.type == 'wall':
                        distance = self.get_distance(map.game.player)
                        map.game.player.add_plasma_velocity(distance, math.atan2(map.game.player.y - self.y, map.game.player.x - self.x))

                    return Decal('plasma', 1000, self.x, self.y, center=False, fade_out=True)

        return False

    def check_collisions(self, collider_list):
        for collider in collider_list:
            if isinstance(collider, Rectangle):
                if (collider.x < self.x < collider.x + collider.w and
                        collider.y < self.y < collider.y + collider.h):
                    if self.sound is not None:
                        self.sound.stop()
                    return collider
            elif isinstance(collider, Triangle):
                if collider.point_in_triangle(self):
                    return collider

        return None
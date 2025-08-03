import pygame, os
from src.Rectangle import Rectangle
from src.Triangle import Triangle
from src.Vector2 import Vector2
from src import config

class Decal(Vector2):

    I_SCALE = 0.15
    I_WIDTH = 128
    I_HEIGHT = 128
    I_WIDTH_S = I_WIDTH * I_SCALE
    I_HEIGHT_S = I_HEIGHT * I_SCALE
    items = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'items.png'))
    new_size = (items.get_width() * I_SCALE, items.get_height() * I_SCALE)
    sprite = pygame.transform.smoothscale(items, new_size)

    ITEM_ROCKET = (0 * I_SCALE, 0 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
    DECAL_ROCKET = (0 * I_SCALE, 128 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
    PROJECTILE_ROCKET = (0 * I_SCALE, 256 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
    PROJECTILE_ROCKET_DOWN = (128 * I_SCALE, 256 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)

    ITEM_PLASMA = (128 * I_SCALE, 0 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
    DECAL_PLASMA = (128 * I_SCALE, 128 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
    PROJECTILE_PLASMA = (128 * I_SCALE, 128 * I_SCALE, I_WIDTH_S, I_HEIGHT_S)

    def __init__(self, sprite, duration, x, y, vel_x = 0, vel_y = 0, target_vel = 0, acc = 0, sound = None):
        super(Decal, self).__init__(x, y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.target_vel = target_vel
        self.acc = acc
        self.sprite = sprite
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.sound = sound

    def point_in_triangle(self, pt, t):
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

        b1 = sign(pt, t.p1, t.p2) < 0.0
        b2 = sign(pt, t.p2, t.p3) < 0.0
        b3 = sign(pt, t.p3, t.p1) < 0.0
        return (b1 == b2) and (b2 == b3)

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
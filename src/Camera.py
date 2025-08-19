import pygame
from abc import abstractmethod, ABC

from numpy.f2py.auxfuncs import throw_error

from src.Settings import Settings
from src.Triangle import Triangle
from src.Vector2 import Vector2

class Camera(pygame.Rect, ABC):
    def __init__(self, settings: Settings):
        super(Camera, self).__init__(0, 0, settings.resolution[0], settings.resolution[1])

        self.settings = settings

    def calculate_offset(self):
        return self.w / 2 - 220 * self.settings.get_scale()

    def to_view_space(self, obj):
        if isinstance(obj, pygame.Rect):
            return Vector2(obj.x - self.x, obj.y - self.y)
        elif isinstance(obj, Triangle):
            return Vector2(obj.surface_pos.x - self.x, obj.surface_pos.y - self.y)
        elif isinstance(obj, Vector2):
            return Vector2(obj.x - self.x, obj.y - self.y)

    @abstractmethod
    def update(self, player):
        pass

    def stop_settling(self, player):
        pass

    def contains_rect(self, other):
        return not (other.x + other.w <= self.x or other.x >= self.x + self.w)

    def contains_triangle(self, triangle):
        if (self.x <= triangle.p1.x <= self.x + self.w or
                self.x <= triangle.p2.x <= self.x + self.w or
                self.x <= triangle.p3.x <= self.x + self.w):
            return True
        left_x = min(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        right_x = max(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        if left_x <= self.x and right_x >= self.x + self.w:
            return True
        camera_left = self.x
        camera_right = self.x + self.w
        edges = [(triangle.p1, triangle.p2), (triangle.p2, triangle.p3), (triangle.p3, triangle.p1)]
        for p1, p2 in edges:
            if p1.x == p2.x:
                continue
            if (p1.x <= camera_left <= p2.x) or (p2.x <= camera_left <= p1.x):
                return True
            if (p1.x <= camera_right <= p2.x) or (p2.x <= camera_right <= p1.x):
                return True
        return False

    def contains_point(self, point):
        return self.x <= point.x <= self.x + self.w
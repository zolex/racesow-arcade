from abc import abstractmethod, ABC

from src.Settings import Settings
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2

class Camera(SimpleRect, ABC):
    def __init__(self, settings: Settings, pos = Vector2()):
        super(Camera, self).__init__(pos, settings.resolution[0], settings.resolution[1])

        self.settings = settings

    def calculate_offset(self):
        return self.w / 2 - 220 * self.settings.get_scale()

    def to_view_space(self, pos):
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y)

    @abstractmethod
    def update(self, player):
        pass

    def stop_settling(self, player):
        pass

    def contains_rect(self, other):
        return not (other.pos.x + other.w <= self.pos.x or other.pos.x >= self.pos.x + self.w)

    def contains_triangle(self, triangle):
        if (self.pos.x <= triangle.p1.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p2.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p3.x <= self.pos.x + self.w):
            return True
        left_x = min(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        right_x = max(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        if left_x <= self.pos.x and right_x >= self.pos.x + self.w:
            return True
        camera_left = self.pos.x
        camera_right = self.pos.x + self.w
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
        return self.pos.x <= point.x <= self.pos.x + self.w
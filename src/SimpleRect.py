

class SimpleRect:
    def __init__(self, pos, width, height):
        self.pos = pos
        self.w = width
        self.h = height

    def contains(self, point):
        return (self.pos.x <= point[0] < self.pos.x + self.w and
                self.pos.y <= point[1] < self.pos.y + self.h)

    def intersects(self, other):
        return not (other.pos.x > self.pos.x + self.w or
                    other.pos.x + other.w < self.pos.x or
                    other.pos.y > self.pos.y + self.h or
                    other.pos.y + other.h < self.pos.y)

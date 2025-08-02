class Vector2():
    """Vector class for 2D positions and velocities"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __mul__(self, other):
        """Overload multiplication"""
        return Vector2(self.x * other, self.y * other)

    def __add__(self, other):
        """Overload Addition"""
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Overload Addition"""
        return Vector2(self.x - other.x, self.y - other.y)
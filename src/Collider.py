from src.GameObject import GameObject
from src.Rectangle import Rectangle
from src.Triangle import Triangle


class Collider(GameObject):
    """Class for static colliders"""
    def __init__(self, shape: Rectangle|Triangle, type: str):
        super(Collider, self).__init__(shape)
        self.type: str = type
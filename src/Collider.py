from src.GameObject import GameObject


class Collider(GameObject):
    """Class for static colliders"""
    def __init__(self, rect):
        super(Collider, self).__init__(rect)
from src.GameObject import GameObject


class Entity(GameObject):
    """Entity class for Gameobjects that possess velocity"""
    def __init__(self, vel, rect):
        super(Entity, self).__init__(rect)
        self.vel = vel
from src.Vector2 import Vector2
from src.Projectile import Projectile

class Item:
    """Item class for items that can be picked up"""
    def __init__(self, item_type: str, pos: Vector2, ammo = 0):
        self.item_type = item_type
        self.pos = pos
        self.sprite = Projectile.ITEM_ROCKET if item_type == 'rocket' else Projectile.ITEM_PLASMA
        self.ammo = ammo
        self.picked_up = False
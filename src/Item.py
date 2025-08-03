from src.Vector2 import Vector2
from src.Projectile import Projectile

class Item:
    """Item class for items that can be picked up"""
    def __init__(self, item_type: str, pos: Vector2, ammo: int = 0, stay: bool = False):
        self.item_type: str = item_type
        self.pos: Vector2 = pos
        self.sprite: str = Projectile.ITEM_ROCKET if item_type == 'rocket' else Projectile.ITEM_PLASMA
        self.ammo: int = ammo
        self.picked_up: bool = False
        self.stay: bool = stay
        self.respawn_at = None

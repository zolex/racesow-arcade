from src.Vector2 import Vector2
from src.Decal import Decal

class Item:
    """Item class for items that can be picked up"""
    def __init__(self, item_type: str, pos: Vector2, ammo = 0):
        self.item_type = item_type
        self.pos = pos
        self.sprite = Decal.ITEM_ROCKET if item_type == 'rocket' else Decal.ITEM_PLASMA
        self.ammo = ammo
        self.picked_up = False
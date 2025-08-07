import os, pygame
from src.Vector2 import Vector2
from src import config

class Item:

    ROCKET = 'rocket'
    PLASMA = 'plasma'

    item_rocket = None
    item_plasma = None

    """Item class for items that can be picked up"""
    def __init__(self, item_type: str, pos: Vector2, ammo: int = 0, stay: bool = False):
        self.item_type: str = item_type
        self.pos: Vector2 = pos
        self.ammo: int = ammo
        self.picked_up: bool = False
        self.stay: bool = stay
        self.respawn_at = None
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_dir = 1

        self.bbox = (self.pos.x, self.pos.y, self.pos.x + 16, self.pos.y + 16)

        Item.item_rocket = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'item_rocket.png')).convert_alpha()
        Item.item_plasma = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'item_plasma.png')).convert_alpha()

    def draw(self, surface, camera):
        if self.picked_up:
            return

        if self.anim_frame == 5:
            self.anim_dir = -1
            frame_time = 75
        elif self.anim_frame == 0:
            self.anim_dir = 1
            frame_time = 250
        else:
            frame_time = 50

        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += self.anim_dir

        view_pos = camera.to_view_space(Vector2(self.pos.x, self.pos.y))
        if self.item_type == self.ROCKET:
            surface.blit(Item.item_rocket, (view_pos.x, view_pos.y - self.anim_frame))
        elif self.item_type == self.PLASMA:
            surface.blit(Item.item_plasma, (view_pos.x, view_pos.y))
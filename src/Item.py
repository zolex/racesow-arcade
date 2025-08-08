import os, pygame
from src.Vector2 import Vector2
from src import config

def pre_load_items():
    for item in ['rocket', 'plasma']:
        Item.types[item] = pygame.image.load(os.path.join(config.assets_folder, 'graphics', f'item_{item}.png')).convert_alpha()

class Item:

    types = {}

    """Item class for items that can be picked up"""
    def __init__(self, type: str, pos: Vector2, ammo: int = 0, stay: bool = False):
        self.type = type
        self.pos: Vector2 = pos
        self.ammo: int = ammo
        self.picked_up: bool = False
        self.stay: bool = stay
        self.respawn_at = None
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_dir = 1

        print(type)
        self.sprite = Item.types[type]

        self.bbox = (self.pos.x, self.pos.y, self.pos.x + 16, self.pos.y + 16)

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
        surface.blit(self.sprite, (view_pos.x, view_pos.y - self.anim_frame))
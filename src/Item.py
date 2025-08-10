import os, pygame, random
from src.Vector2 import Vector2
from src import config

def pre_load_items(SCALE:int = 1):
    for item in ['rocket', 'plasma']:
        Item.types[item] = pygame.image.load(os.path.join(config.assets_folder, 'graphics', f'item_{item}.png')).convert_alpha()
        if SCALE != 1:
            Item.types[item] = pygame.transform.scale(Item.types[item], (Item.types[item].get_width() * SCALE, Item.types[item].get_height() * SCALE))

class Item:

    types = {}

    """Item class for items that can be picked up"""
    def __init__(self, type: str, pos: Vector2, width=16, height=16, ammo: int = 0, stay: bool = False):
        self.type = type
        self.pos: Vector2 = pos
        self.ammo: int = ammo
        self.picked_up: bool = False
        self.stay: bool = stay
        self.respawn_at = None
        self.anim_frame = 0
        self.anim_timer = random.randint(0, 250)
        self.anim_dir = 1
        self.width = width
        self.height = height

        self.sprite = Item.types[type]

        self.bbox = (self.pos.x, self.pos.y, self.pos.x + self.width, self.pos.y + self.height)

    def draw(self, surface, camera):
        if self.picked_up:
            return

        if self.anim_frame == 5:
            self.anim_dir = -1
            frame_time = random.randint(50, 100)
        elif self.anim_frame == 0:
            self.anim_dir = 1
            frame_time = random.randint(200, 275)
        else:
            frame_time = random.randint(33, 66)

        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += self.anim_dir

        view_pos = camera.to_view_space(Vector2(self.pos.x, self.pos.y))
        surface.blit(self.sprite, (view_pos.x, view_pos.y - self.anim_frame))
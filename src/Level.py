import os.path, math
import pygame, yaml, random

from src.JumpPad import JumpPad
from src.Portal import Portal
from src.Vector2 import Vector2
from src.Triangle import Triangle
from src.Rectangle import Rectangle
from src.Collider import Collider
from src.Item import Item
from src.Projectile import Projectile
from src.Camera import Camera
from src.Texture import Texture
from src.Player import Player
from src import config, sounds

class Level:
    def __init__(self, surface: pygame.surface, camera: Camera):

        self.map_folder = None
        self.map_name: str|None = None
        self.surface: pygame.surface = surface
        self.camera: Camera = camera

        self.player: Player|None = None
        self.background: pygame.image = None
        self.background_width: int|None = None
        self.background_height: int = config.SCREEN_HEIGHT
        self.sky: pygame.image = None
        self.overlay1: pygame.image = None
        self.overlay1_width: int|None = None
        self.overlay1_offset: int = 0
        self.overlay2: pygame.image = None
        self.overlay2_offset: int = 0

        self.static_colliders =  []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.dynamic_colliders = []
        self.decoration = []
        self.projectiles = []
        self.items = []
        self.last_decal_velocity: int = 0
        self.player_start: Vector2 = Vector2(70, 70)

        self.portals = []
        self.jump_pads = []


    def load(self, map_name: str, player: Player):

        self.player = player
        self.map_name = map_name

        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.dynamic_colliders = []
        self.projectiles = []
        self.items = []
        self.last_decal_velocity = 0

        self.map_folder = os.path.join(config.assets_folder, 'maps', self.map_name)

        map_file = os.path.join(self.map_folder, 'map.yaml')
        with open(map_file, 'r') as file:
            data = yaml.safe_load(file)

        spawnpoint = data.get('player_spawnpoint', None)
        if spawnpoint is not None:
            self.player_start = Vector2(spawnpoint['x'], spawnpoint['y'])

        items = data.get('items', None)
        if items is not None:
            for item in items:
                self.items.append(Item(item['type'], Vector2(item['x'], item['y'] + 12), item['ammo'], item['stay']))

        portals = data.get('portals', None)
        if portals is not None:
            for portal in portals:
                self.portals.append(Portal(Vector2(portal['entry_x'], portal['entry_y']), Vector2(portal['exit_x'], portal['exit_y'])))

        jump_pads = data.get('jump_pads', None)
        if jump_pads is not None:
            for jump_pad in jump_pads:
                self.jump_pads.append(JumpPad(Vector2(jump_pad['x'], jump_pad['y']), Vector2(jump_pad['vel_x'], jump_pad['vel_y'])))

        rectangles = data.get('rectangles', None)
        if rectangles is not None:
            for rect in rectangles:
                texture = None
                texture_path = rect.get('texture', None)
                if texture_path is not None:
                    texture = Texture(os.path.join(self.map_folder, rect['texture']), rect.get('texture_scale', 1), rect.get('texture_offset_x', 0), rect.get('texture_offset_y', 0), rect.get('texture_rotation', 0))
                collider = Collider(Rectangle(Vector2(rect['x'], rect['y']), int(rect['w']), int(rect['h']), texture))
                if rect['wall_type'] == 'static':
                    self.static_colliders.append(collider)
                elif rect['wall_type'] == 'wall':
                    self.wall_colliders.append(collider)
                elif rect['wall_type'] == 'deco':
                    self.decoration.append(collider)

        triangles = data.get('triangles', None)
        if triangles is not None:
            for triangle in triangles:
                texture = None
                texture_path = triangle.get('texture', None)
                if texture_path is not None:
                    texture = Texture(os.path.join(self.map_folder, triangle['texture']), triangle.get('texture_scale', 1), triangle.get('texture_offset_x', 0), triangle.get('texture_offset_y', 0), triangle.get('texture_rotation', 0))
                points = triangle.get('points', None)
                collider = Collider(Triangle(Vector2(points[0]['x'], points[0]['y']), Vector2(points[1]['x'], points[1]['y']), Vector2(points[2]['x'], points[2]['y']), texture))
                if triangle['wall_type'] == 'ramp':
                    self.ramp_colliders.append(collider)

        #for item in data.get('player_items', []):
        #    if item['type'] == 'plasma':
        #        player.has_plasma = True
        #        player.plasma_ammo = item['ammo']
        #        player.animation.select_plasma()
        #        player.active_weapon = 'plasma'
        #    if item['type'] == 'rocket':
        #        player.has_rocket = True
        #        player.rocket_ammo = item['ammo']
        #        player.animation.select_rocket()
        #        player.active_weapon = 'rocket'

        sky = data.get('sky', None)
        if sky is not None:
            sky_path = os.path.join(self.map_folder, sky)
            if os.path.isfile(sky_path):
                self.sky = pygame.image.load(sky_path).convert()
                width = config.SCREEN_WIDTH
                height = int(width * self.sky.get_height() / self.sky.get_width())
                self.sky = pygame.transform.scale(self.sky, (width, height))

        overlay1 = data.get('overlay1', None)
        if overlay1 is not None:
            overlay1_path = os.path.join(self.map_folder, overlay1)
            if os.path.isfile(overlay1_path):
                self.overlay1 = pygame.image.load(overlay1_path).convert_alpha()
                self.overlay1_width = config.SCREEN_WIDTH
                height = int(self.overlay1_width * self.overlay1.get_height() / self.overlay1.get_width())
                self.overlay1 = pygame.transform.scale(self.overlay1, (self.overlay1_width, height))

    def update(self, player: Player):
        for i in range(len(self.projectiles) - 1, -1, -1):
            projectile = self.projectiles[i].update(player, self.static_colliders + self.ramp_colliders)
            if projectile:
                del self.projectiles[i]
                if isinstance(projectile, Projectile):
                    self.projectiles.append(projectile)

    def draw(self):
        self.surface.fill(config.BACKGROUND_COLOR)
        self.draw_sky()
        self.draw_overlay1()
        self.draw_rects()
        self.draw_triangles()
        self.draw_portals()
        self.draw_jump_pads()
        self.draw_items()
        self.draw_decals()

    def draw_portals(self):
        for portal in self.portals:
            portal.draw(self.surface, self.camera)

    def draw_jump_pads(self):
        for jump_pad in self.jump_pads:
            jump_pad.draw(self.surface, self.camera)

    def draw_rect(self, collider: Collider):
        view_pos = self.camera.to_view_space(collider.shape.pos)
        if collider.shape.surface is not None:
            self.surface.blit(collider.shape.surface, (view_pos.x, view_pos.y))
        else:
            pygame.draw.rect(self.surface, (0, 0, 0, 128), (view_pos.x, view_pos.y, collider.shape.w, collider.shape.h))

    def draw_triangle(self, collider: Collider):
        if collider.shape.surface is not None:
            self.surface.blit(collider.shape.surface, (collider.shape.surface_pos.x - self.camera.pos.x, collider.shape.surface_pos.y - self.camera.pos.y))
        else:
            pygame.draw.polygon(self.surface, (160, 0, 44, 128), [
                (collider.shape.p1.x - self.camera.pos.x, collider.shape.p1.y - self.camera.pos.y),
                (collider.shape.p2.x - self.camera.pos.x, collider.shape.p2.y - self.camera.pos.y),
                (collider.shape.p3.x - self.camera.pos.x, collider.shape.p3.y - self.camera.pos.y)
            ])

    def draw_sky(self):
        if self.sky is not None:
            self.surface.blit(self.sky, (0, 0))

    def draw_overlay1(self):
        if self.overlay1 is not None:
            offset = -10 / self.background_width * self.camera.pos.x
            x = offset * self.overlay1_width + self.overlay1_offset
            if x < -self.overlay1_width:
                self.overlay1_offset += self.overlay1_width * 2
            self.surface.blit(self.overlay1, (x, -self.camera.pos.y * 0.5))

    def draw_rects(self):
        #num = 0
        for collider in self.static_colliders + self.wall_colliders + self.decoration:
            if self.camera.contains_rect(collider.shape):
        #        num += 1
                self.draw_rect(collider)

        #print("num rects rendered", num)

    def draw_triangles(self):
        #num = 0
        for collider in self.ramp_colliders:
            if self.camera.contains_triangle(collider.shape):
        #        num += 1
                self.draw_triangle(collider)

        #print("num tris rendered", num)

    def draw_items(self):
        #num = 0
        for item in self.items:
            if item.picked_up:
                continue
            view_pos = self.camera.to_view_space(item.pos)
            if self.camera.contains_point(item.pos):
        #        num += 1
                self.surface.blit(Projectile.sprite, (view_pos.x, view_pos.y), item.sprite)

        #print("num ITEMS rendered", num)

    def draw_decals(self):
        #num = 0
        for decal in self.projectiles:
            view_pos = self.camera.to_view_space(Vector2(decal.x, decal.y))
            self.surface.blit(Projectile.sprite, (view_pos.x, view_pos.y), decal.sprite)

        #print("num DECALS rendered", num)

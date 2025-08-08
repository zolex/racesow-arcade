import os.path, pygame, yaml
from pyqtree import Index as QuadTree

from src.FinishLine import FinishLine
from src.JumpPad import JumpPad
from src.Portal import Portal
from src.StartLine import StartLine
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
        self.sky: pygame.image = None
        self.overlay: pygame.image = None
        self.overlay_width: int | None = None
        self.overlay_offset: int = 0

        self.static_colliders =  []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.death_colliders = []
        self.dynamic_colliders = []
        self.decoration = []
        self.projectiles = []
        self.items = []
        self.last_decal_velocity: int = 0
        self.player_start: Vector2 = Vector2(70, 70)

        self.portals = []
        self.jump_pads = []

        self.tree: QuadTree|None = None
        self.filtered_objects = []

        self.start_line: StartLine|None = None
        self.finish_line: FinishLine | None = None
        self.timer: int = 0
        self.timer_start = None
        self.timer_stop = None

    def load(self, map_name: str, player: Player):

        self.player = player
        self.map_name = map_name

        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.death_colliders = []
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

        start_line = data.get('start_line', None)
        if start_line is not None:
            self.start_line = StartLine(Vector2(start_line['x'], start_line['y']))

        finish_line = data.get('finish_line', None)
        if finish_line is not None:
            self.finish_line = FinishLine(Vector2(finish_line['x'], finish_line['y']))

        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")

        items = data.get('items', None)
        if items is not None:
            for item in items:
                min_x = min(item['x'], min_x)
                max_x = max(item['x'], max_x)
                min_y = min(item['y'], min_y)
                max_y = max(item['y'], max_y)
                self.items.append(Item(item['type'], Vector2(item['x'], item['y'] + 12), item['ammo'], item['stay']))

        portals = data.get('portals', None)
        if portals is not None:
            for portal in portals:
                min_x = min(portal['entry_x'], portal['exit_x'], min_x)
                max_x = max(portal['entry_x'], portal['entry_x'], max_x)
                min_y = min(portal['entry_y'], portal['entry_y'], min_y)
                max_y = max(portal['entry_y'], portal['entry_y'], max_y)
                self.portals.append(Portal(Vector2(portal['entry_x'], portal['entry_y']), Vector2(portal['exit_x'], portal['exit_y'])))

        jump_pads = data.get('jump_pads', None)
        if jump_pads is not None:
            for jump_pad in jump_pads:
                min_x = min(jump_pad['x'], min_x)
                max_x = max(jump_pad['x'], max_x)
                min_y = min(jump_pad['y'], min_y)
                max_y = max(jump_pad['y'], max_y)
                self.jump_pads.append(JumpPad(Vector2(jump_pad['x'], jump_pad['y']), Vector2(jump_pad['vel_x'], jump_pad['vel_y'])))

        rectangles = data.get('rectangles', None)
        if rectangles is not None:
            for rect in rectangles:

                min_x = min(rect['x'], min_x)
                max_x = max(rect['x'] + rect['w'], max_x)
                min_y = min(rect['y'], min_y)
                max_y = max(rect['y'] + rect['h'], max_y)

                texture = None
                texture_path = rect.get('texture', None)
                if texture_path is not None:
                    texture = Texture(os.path.join(self.map_folder, rect['texture']), rect.get('texture_scale', 1), rect.get('texture_offset_x', 0), rect.get('texture_offset_y', 0), rect.get('texture_rotation', 0))
                collider = Collider(Rectangle(Vector2(rect['x'], rect['y']), int(rect['w']), int(rect['h']), texture), rect['wall_type'])
                if rect['wall_type'] == 'static':
                    self.static_colliders.append(collider)
                elif rect['wall_type'] == 'wall':
                    self.wall_colliders.append(collider)
                elif rect['wall_type'] == 'deco':
                    self.decoration.append(collider)
                elif rect['wall_type'] == 'death':
                    self.death_colliders.append(collider)

        triangles = data.get('triangles', None)
        if triangles is not None:
            for triangle in triangles:
                texture = None
                texture_path = triangle.get('texture', None)
                if texture_path is not None:
                    texture = Texture(os.path.join(self.map_folder, triangle['texture']), triangle.get('texture_scale', 1), triangle.get('texture_offset_x', 0), triangle.get('texture_offset_y', 0), triangle.get('texture_rotation', 0))
                points = triangle.get('points', None)
                for p in points:
                    min_x = min(p['x'], min_x)
                    max_x = max(p['x'], max_x)
                    min_y = min(p['y'], min_y)
                    max_y = max(p['y'], max_y)
                collider = Collider(Triangle(Vector2(points[0]['x'], points[0]['y']), Vector2(points[1]['x'], points[1]['y']), Vector2(points[2]['x'], points[2]['y']), texture), 'ramp')
                if triangle['wall_type'] == 'ramp':
                    self.ramp_colliders.append(collider)

        ####################################
        ### store everything in quadtree ###
        ####################################

        print("min_x:", min_x, "max_x:", max_x, "min_y:", min_y, "max_y:", max_y)
        self.tree = QuadTree(bbox=(min_x, min_y, max_x, max_y))

        for item in self.items:
            self.tree.insert(item, item.bbox)
        self.items = []

        for portal in self.portals:
            self.tree.insert(portal,portal.bbox)
        self.portals = []

        for jump_pad in self.jump_pads:
            self.tree.insert(jump_pad, jump_pad.bbox)
        self.jump_pads = []

        for collider in self.static_colliders + self.wall_colliders + self.decoration + self.death_colliders:
            self.tree.insert(collider, collider.shape.bbox)
        self.static_colliders = self.wall_colliders = self.decoration = self.death_colliders = []

        for collider in self.ramp_colliders:
            self.tree.insert(collider, collider.shape.bbox)
        self.ramp_colliders = []

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

        overlay = data.get('overlay', None)
        if overlay is not None:
            overlay1_path = os.path.join(self.map_folder, overlay)
            if os.path.isfile(overlay1_path):
                self.overlay = pygame.image.load(overlay1_path).convert_alpha()
                self.overlay_width = config.SCREEN_WIDTH
                height = int(self.overlay_width * self.overlay.get_height() / self.overlay.get_width())
                self.overlay = pygame.transform.scale(self.overlay, (self.overlay_width, height))

    #def draw_tree(self, surface: pygame.surface):
    #    all_bbox = self.tree.get_all_bbox()
    #    for bbox in all_bbox:
    #        rect_to_draw = (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])
    #        pygame.draw.rect(surface, (255, 0, 0), rect_to_draw, 1)

    def reset(self):
        self.projectiles = []
        for item in self.items:
            item.picked_up = False

    def start_timer(self):
        self.timer_start = pygame.time.get_ticks()

    def stop_timer(self):
        self.timer_stop = pygame.time.get_ticks()

    def update(self, player: Player):

        if self.timer_start is not None and self.timer_stop is None:
            self.timer = pygame.time.get_ticks() - self.timer_start

        # filter objects from quadtree in each frame
        self.static_colliders = []
        self.wall_colliders = []
        self.ramp_colliders = []
        self.death_colliders = []
        self.decoration = []
        self.items = []
        self.portals = []
        self.jump_pads = []

        boundary = (self.camera.pos.x, self.camera.pos.y, self.camera.pos.x + self.camera.w, self.camera.pos.y + self.camera.h)
        self.filtered_objects = self.tree.intersect(boundary)
        for object in self.filtered_objects:
            if isinstance(object, Collider):
                if object.type == 'static':
                    self.static_colliders.append(object)
                elif object.type == 'wall':
                    self.wall_colliders.append(object)
                elif object.type == 'ramp':
                    self.ramp_colliders.append(object)
                elif object.type == 'death':
                    self.death_colliders.append(object)
                elif object.type == 'deco':
                    self.decoration.append(object)
            elif isinstance(object, Item):
                self.items.append(object)
            elif isinstance(object, Portal):
                self.portals.append(object)
            elif isinstance(object, JumpPad):
                self.jump_pads.append(object)

        for i in range(len(self.projectiles) - 1, -1, -1):
            projectile = self.projectiles[i].update(player, self.static_colliders + self.ramp_colliders)
            if projectile:
                del self.projectiles[i]
                if isinstance(projectile, Projectile):
                    self.projectiles.append(projectile)

    def draw(self):
        self.surface.fill(config.BACKGROUND_COLOR)
        self.draw_sky()
        self.draw_overlay()

        for collider in self.static_colliders + self.wall_colliders + self.ramp_colliders + self.death_colliders + self.decoration:
            collider.shape.draw(self.surface, self.camera)

        for item in self.items:
            item.draw(self.surface, self.camera)

        for portal in self.portals:
            portal.draw(self.surface, self.camera)

        for jump_pad in self.jump_pads:
            jump_pad.draw(self.surface, self.camera)

        if self.start_line:
            self.start_line.draw_back(self.surface, self.camera)
        if self.finish_line:
            self.finish_line.draw_back(self.surface, self.camera)

        #print("num objects", len(self.filtered_objects))

        self.draw_decals()

    def draw_front(self):
        if self.start_line:
            self.start_line.draw_front(self.surface, self.camera)
        if self.finish_line:
            self.finish_line.draw_front(self.surface, self.camera)

    def draw_sky(self):
        if self.sky is not None:
            self.surface.blit(self.sky, (0, 0))

    def draw_overlay(self):
        if self.overlay is not None:
            offset = -1.05 / self.overlay_width * self.camera.pos.x
            x = config.SCREEN_WIDTH + offset * self.overlay_width + self.overlay_offset
            if x < -self.overlay_width:
                self.overlay_offset += self.overlay_width * 2
            self.surface.blit(self.overlay, (x, config.SCREEN_HEIGHT / 2.5 - self.camera.pos.y * 1.2))

    def draw_decals(self):
        for decal in self.projectiles:
            decal.draw(self.surface, self.camera)

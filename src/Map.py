import os.path, pygame, yaml, math
from pyqtree import Index as QuadTree
from src.Item.Decal import Decal
from src.Item.FinishLine import FinishLine
from src.Item.JumpPad import JumpPad
from src.Item.Portal import Portal
from src.Item.StartLine import StartLine
from src.World.Vector2 import Vector2
from src.World.Triangle import Triangle
from src.World.Rectangle import Rectangle
from src.Item.Item import Item
from src.Item.Projectile import Projectile
from src.World.Texture import Texture
from src.Player import Player
from src import config

class Map:
    def __init__(self, game):

        self.game = game
        self.map_folder = None
        self.map_name: str|None = None

        self.sky: pygame.image = None
        self.parallax_1: pygame.image = None
        self.parallax_1_width: int | None = None
        self.parallax_1_offset: int = 0
        self.parallax_2: pygame.image = None
        self.parallax_2_width: int | None = None
        self.parallax_2_offset: int = 0

        self.static_colliders =  []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.death_colliders = []
        self.dynamic_colliders = []
        self.decoration = []
        self.projectiles: list[Projectile] = []
        self.decals: list[Decal] = []
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

    def load(self, map_name: str):

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

        scale = self.game.settings.get_scale()
        volume = self.game.settings.get_volume()

        map_file = os.path.join(self.map_folder, 'map.yaml')
        with open(map_file, 'r') as file:
            data = yaml.safe_load(file)

        spawnpoint = data.get('player_spawnpoint', None)
        if spawnpoint is not None:
            self.player_start = Vector2(spawnpoint['x'] * scale, spawnpoint['y'] * scale)

        self.game.camera.pos = Vector2(self.player_start.x - 50, self.player_start.y - 200 * scale)

        start_line = data.get('start_line', None)
        if start_line is not None:
            self.start_line = StartLine(start_line['x'] * scale, start_line['y'] * scale, scale=scale)

        finish_line = data.get('finish_line', None)
        if finish_line is not None:
            self.finish_line = FinishLine(finish_line['x'] * scale, finish_line['y'] * scale)

        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")

        items = data.get('items', None)
        if items is not None:
            for item in items:
                min_x = min(item['x'] * scale, min_x)
                max_x = max(item['x'] * scale, max_x)
                min_y = min(item['y'] * scale, min_y)
                max_y = max(item['y'] * scale, max_y)
                self.items.append(Item(item['type'], item['x'] * scale, item['y'] * scale + 12 * scale, 16 * scale, 16 * scale, item['ammo'], item['stay']))

        portals = data.get('portals', None)
        if portals is not None:
            for portal in portals:
                exit = Portal(portal['exit_x'] * scale, portal['exit_y'] * scale, portal['exit_flipped'], screen_width=self.game.settings.resolution[0], scale=scale, volume=volume)
                self.portals.append(Portal(portal['entry_x'] * scale, portal['entry_y'] * scale, portal['entry_flipped'], exit=exit, screen_width=self.game.settings.resolution[0], scale=scale, volume=volume))
                self.portals.append(exit)

        jump_pads = data.get('jump_pads', None)
        if jump_pads is not None:
            for jump_pad in jump_pads:
                min_x = min(jump_pad['x'] * scale, min_x)
                max_x = max(jump_pad['x'] * scale, max_x)
                min_y = min(jump_pad['y'] * scale, min_y)
                max_y = max(jump_pad['y'] * scale, max_y)
                rotation = float(jump_pad.get('rotation', 0.0))
                vel = float(jump_pad.get('vel', 0.7))
                self.jump_pads.append(JumpPad(jump_pad['x'] * scale, jump_pad['y'] * scale, vel, rotation, scale, volume))

        rectangles = data.get('rectangles', None)
        if rectangles is not None:
            for rect in rectangles:

                min_x = min(rect['x'] * scale, min_x)
                max_x = max(rect['x'] * scale + rect['w'] * scale, max_x)
                min_y = min(rect['y'] * scale, min_y)
                max_y = max(rect['y'] * scale + rect['h'] * scale, max_y)

                texture = None
                texture_path = rect.get('texture', None)
                if texture_path is not None:
                    texture = Texture(os.path.join(self.map_folder, rect['texture']), rect.get('texture_scale', 1) * scale, rect.get('texture_offset_x', 0) * scale, rect.get('texture_offset_y', 0) * scale, rect.get('texture_rotation', 0))
                collider = Rectangle(rect['x'] * scale, rect['y'] * scale, int(rect['w'] * scale), int(rect['h'] * scale), texture, rect['wall_type'])
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
                    texture = Texture(os.path.join(self.map_folder, triangle['texture']), triangle.get('texture_scale', 1) * scale, triangle.get('texture_offset_x', 0) * scale, triangle.get('texture_offset_y', 0) * scale, triangle.get('texture_rotation', 0))
                points = triangle.get('points', None)
                for p in points:
                    min_x = min(p['x'] * scale, min_x)
                    max_x = max(p['x'] * scale, max_x)
                    min_y = min(p['y'] * scale, min_y)
                    max_y = max(p['y'] * scale, max_y)
                collider = Triangle(Vector2(points[0]['x'] * scale, points[0]['y'] * scale), Vector2(points[1]['x'] * scale, points[1]['y'] * scale), Vector2(points[2]['x'] * scale, points[2]['y'] * scale), texture)
                if triangle['wall_type'] == 'ramp':
                    self.ramp_colliders.append(collider)

        ####################################
        ### store everything in quadtree ###
        ####################################

        self.tree = QuadTree(bbox=(min_x, min_y, max_x, max_y))

        for item in self.items:
            self.tree.insert(item, (item.x, item.y, item.x + item.w, item.y + item.h))
        self.items = []

        for portal in self.portals:
            self.tree.insert(portal, (portal.x, portal.y, portal.x + portal.w, portal.y + portal.h))
        self.portals = []

        for jump_pad in self.jump_pads:
            self.tree.insert(jump_pad, (jump_pad.x, jump_pad.y, jump_pad.x + jump_pad.w, jump_pad.y + jump_pad.h))
        self.jump_pads = []

        for rect in self.static_colliders + self.wall_colliders + self.decoration + self.death_colliders:
            self.tree.insert(rect, (rect.x, rect.y, rect.x + rect.w, rect.y + rect.h))
        self.static_colliders = self.wall_colliders = self.decoration = self.death_colliders = []

        for triangle in self.ramp_colliders:
            self.tree.insert(triangle, triangle.bbox)
        self.ramp_colliders = []

        sky = data.get('sky', None)
        if sky is not None:
            sky_path = os.path.join(self.map_folder, sky)
            if os.path.isfile(sky_path):
                self.sky = pygame.image.load(sky_path).convert()
                width = self.game.settings.resolution[0]
                height = int(width * self.sky.get_height() / self.sky.get_width())
                self.sky = pygame.transform.scale(self.sky, (width, height))

        parallax_1 = data.get('parallax_1', None)
        if parallax_1 is not None:
            parallax_1_path = os.path.join(self.map_folder, parallax_1)
            if os.path.isfile(parallax_1_path):
                self.parallax_1 = pygame.image.load(parallax_1_path).convert_alpha()
                self.parallax_1_width = self.game.settings.resolution[0]
                height = int(self.parallax_1_width * self.parallax_1.get_height() / self.parallax_1.get_width())
                self.parallax_1 = pygame.transform.scale(self.parallax_1, (self.parallax_1_width, height))

        parallax_2 = data.get('parallax_2', None)
        if parallax_2 is not None:
            parallax_2_path = os.path.join(self.map_folder, parallax_2)
            if os.path.isfile(parallax_2_path):
                self.parallax_2 = pygame.image.load(parallax_2_path).convert_alpha()
                self.parallax_2_width = self.game.settings.resolution[0]
                height = int(self.parallax_2_width * self.parallax_2.get_height() / self.parallax_2.get_width())
                self.parallax_2 = pygame.transform.scale(self.parallax_2, (self.parallax_2_width, height))

    def reset(self):

        self.sky: pygame.image = None
        self.parallax_1: pygame.image = None
        self.parallax_1_width: int | None = None
        self.parallax_1_offset: int = 0
        self.parallax_2: pygame.image = None
        self.parallax_2_width: int | None = None
        self.parallax_2_offset: int = 0

        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.death_colliders = []
        self.dynamic_colliders = []
        self.decoration = []
        self.projectiles: list[Projectile] = []
        self.decals: list[Decal] = []
        self.items = []
        self.last_decal_velocity: int = 0
        self.player_start: Vector2 = Vector2(70, 70)

        self.portals = []
        self.jump_pads = []

        self.tree: QuadTree | None = None
        self.filtered_objects = []

        self.start_line: StartLine | None = None
        self.finish_line: FinishLine | None = None
        self.timer: int = 0
        self.timer_start = None
        self.timer_stop = None

        self.load(self.map_name)
        self.game.camera.is_looking_ahead_y = True


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

        # extend the boundary to the bottom extremely (42) so we can always find the distance to the collider below
        boundary = (self.game.camera.x, self.game.camera.y, self.game.camera.x + self.game.camera.w, self.game.camera.y + self.game.camera.h * 42)
        self.filtered_objects = self.tree.intersect(boundary)
        for object in self.filtered_objects:
            if isinstance(object, Rectangle):
                if object.type == 'static':
                    self.static_colliders.append(object)
                elif object.type == 'wall':
                    self.wall_colliders.append(object)
                elif object.type == 'death':
                    self.death_colliders.append(object)
                elif object.type == 'deco':
                    self.decoration.append(object)
            elif isinstance(object, Triangle):
                if object.type == 'ramp':
                    self.ramp_colliders.append(object)
            elif isinstance(object, Item):
                self.items.append(object)
            elif isinstance(object, Portal):
                self.portals.append(object)
            elif isinstance(object, JumpPad):
                self.jump_pads.append(object)

        for i in range(len(self.projectiles) - 1, -1, -1):
            # projectile can produce a decal (e.g. on hit with wall)
            decal = self.projectiles[i].update(self)
            if decal:
                del self.projectiles[i]
                if isinstance(decal, Decal):
                    self.decals.append(decal)

        for i in range(len(self.decals) - 1, -1, -1):
            if self.decals[i].is_expired():
                del self.decals[i]

    def draw(self):
        self.game.surface.fill(config.BACKGROUND_COLOR)
        self.draw_sky()
        self.draw_parallax_2()
        self.draw_parallax_1()

        for collider in self.static_colliders + self.wall_colliders + self.ramp_colliders + self.death_colliders + self.decoration:
            collider.draw(self.game.surface, self.game.camera)

        for item in self.items:
            item.draw(self.game.surface, self.game.camera)

        for portal in self.portals:
            portal.draw(self.game.surface, self.game.camera)

        for jump_pad in self.jump_pads:
            jump_pad.draw(self.game.surface, self.game.camera)

        if self.start_line:
            self.start_line.draw_back(self.game.surface, self.game.camera)
        if self.finish_line:
            self.finish_line.draw_back(self.game.surface, self.game.camera)

        #print("num objects", len(self.filtered_objects))

        self.draw_decals()
        self.draw_projectiles()

    def draw_front(self):
        if self.start_line:
            self.start_line.draw_front(self.game.surface, self.game.camera)
        if self.finish_line:
            self.finish_line.draw_front(self.game.surface, self.game.camera)

    def draw_sky(self):
        if self.sky is not None:
            self.game.surface.blit(self.sky, (0, 0))

    def draw_parallax_1(self):
        if self.parallax_1 is not None:
            parallax_1_factor = 0.25  # smaller = further away

            offset_x = -parallax_1_factor / self.parallax_1_width * self.game.camera.x
            x = self.game.settings.resolution[0] + offset_x * self.parallax_1_width + self.parallax_1_offset

            y = -parallax_1_factor * self.game.camera.y

            if x < -self.parallax_1_width:
                self.parallax_1_offset += self.parallax_1_width * 2

            self.game.surface.blit(self.parallax_1, (x, y))

    def draw_parallax_2(self):
        if self.parallax_2 is not None:
            parallax_2_factor = 0.125  # smaller = further away

            # Calculate offset based on camera position
            offset_x = -parallax_2_factor * self.game.camera.x
            offset_y = -parallax_2_factor * self.game.camera.y

            # Wrap offset so it always stays within the texture width
            x = (offset_x % self.parallax_2_width)

            # Draw two instances to cover the gap
            self.game.surface.blit(self.parallax_2, (x - self.parallax_2_width, offset_y))
            self.game.surface.blit(self.parallax_2, (x, offset_y))

    def draw_projectiles(self):
        for projectiles in self.projectiles:
            projectiles.draw(self.game.surface, self.game.camera)

    def draw_decals(self):
        for decal in self.decals:
            decal.draw(self.game.surface, self.game.camera)

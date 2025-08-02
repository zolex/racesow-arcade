import os.path
from os import path
import pygame, yaml, random

from src.basetypes import Vector2, Triangle, Rectangle, Collider, Item, Decal, Camera, Texture
from src import sprites, config, sounds
from src.player import Player

class Level:
    def __init__(self, surface: pygame.surface, camera: Camera):

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
        self.decals = []
        self.items = []
        self.last_decal_velocity: int = 0
        self.player_start: Vector2 = Vector2(70, 70)


    def load(self, map_name: str, player: Player):

        self.player = player
        self.map_name = map_name

        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.dynamic_colliders = []
        self.decals = []
        self.items = []
        self.last_decal_velocity = 0



        self.map_folder = path.join(sprites.assets_folder, 'maps', self.map_name)

        map_file = path.join(self.map_folder, 'map.yaml')
        with open(map_file, 'r') as file:
            data = yaml.safe_load(file)

        spawnpoint = data.get('player_spawnpoint', None)
        if spawnpoint is not None:
            self.player_start = Vector2(spawnpoint['x'], spawnpoint['y'])

        items = data.get('items', None)
        if items is not None:
            for item in items:
                self.items.append(Item(item['type'], Vector2(item['x'], item['y'] + 12), item['ammo']))

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
            sky_path = path.join(self.map_folder, sky)
            if os.path.isfile(sky_path):
                self.sky = pygame.image.load(sky_path).convert()
                width = config.SCREEN_WIDTH
                height = int(width * self.sky.get_height() / self.sky.get_width())
                self.sky = pygame.transform.scale(self.sky, (width, height))

        overlay1 = data.get('overlay1', None)
        if overlay1 is not None:
            overlay1_path = path.join(self.map_folder, overlay1)
            if os.path.isfile(overlay1_path):
                self.overlay1 = pygame.image.load(overlay1_path).convert_alpha()
                self.overlay1_width = config.SCREEN_WIDTH
                height = int(self.overlay1_width * self.overlay1.get_height() / self.overlay1.get_width())
                self.overlay1 = pygame.transform.scale(self.overlay1, (self.overlay1_width, height))

    def update_decals(self, player: Player):
        for i in range(len(self.decals) - 1, -1, -1):
            if self.decals[i].start_time + self.decals[i].duration < pygame.time.get_ticks():
                del self.decals[i]
            elif self.decals[i].vel_x > 0:
                self.decals[i].x += self.decals[i].vel_x * config.delta_time
                self.last_decal_velocity += config.delta_time
                if self.last_decal_velocity > 1000 and (self.decals[i].vel_x > self.decals[i].target_vel):
                    self.decals[i].vel_x += self.decals[i].acc
                if self.decals[i].sound is not None:
                    distance = abs(player.pos.x - self.decals[i].x)
                    self.decals[i].sound.set_volume(1 - (distance / 1000))
                if self.decals[i].sprite == sprites.PROJECTILE_PLASMA or self.decals[i].sprite == sprites.PROJECTILE_ROCKET:
                    collider = self.decals[i].check_collisions(self.static_colliders + self.ramp_colliders)
                    if collider is not None:
                        if self.decals[i].sprite == sprites.PROJECTILE_ROCKET:
                            x = self.decals[i].x
                            y = self.decals[i].y
                            del self.decals[i]
                            self.decals.append(Decal(sprites.DECAL_ROCKET, 500, x, y))
                            distance = abs(player.pos.x - x)
                            sounds.rocket.set_volume(1 - (distance / 1000))
                            sounds.rocket.play()
                        if self.decals[i].sprite == sprites.PROJECTILE_PLASMA:
                            self.decals[i].x += random.randrange(-5, 5)
                            self.decals[i].y += random.randrange(-5, 5)
                            self.decals[i].vel_x = 0
                            self.decals[i].start_time = pygame.time.get_ticks()
                            self.decals[i].duration = 300

                    # player hit by rocket from behind
                    elif self.decals[i].vel_x > self.player.vel.x and self.decals[i].sprite == sprites.PROJECTILE_ROCKET:
                        collider = self.decals[i].check_collisions([self.player])
                        if collider is not None:
                            x = self.decals[i].x
                            y = self.decals[i].y
                            del self.decals[i]
                            self.decals.append(Decal(sprites.DECAL_ROCKET, 500, x, y))
                            distance = abs(player.pos.x - x)
                            print(distance)
                            sounds.rocket.set_volume(1)
                            sounds.rocket.play()
                            self.player.vel.x += 0.5
                            self.player.vel.y -= 0.5

    def draw(self):
        self.surface.fill(config.BACKGROUND_COLOR)
        self.draw_sky()
        self.draw_overlay1()

        self.draw_rects()
        self.draw_triangles()
        self.draw_items()
        self.draw_decals()

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
        for collider in self.static_colliders + self.wall_colliders:
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
                self.surface.blit(sprites.item_set, (view_pos.x, view_pos.y), item.sprite)

        #print("num ITEMS rendered", num)

    def draw_decals(self):
        #num = 0
        for decal in self.decals:
            view_pos = self.camera.to_view_space(Vector2(decal.x, decal.y))
            self.surface.blit(sprites.item_set, (view_pos.x, view_pos.y), decal.sprite)

        #print("num DECALS rendered", num)

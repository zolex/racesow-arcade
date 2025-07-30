from os import path
import pygame, yaml, random
from src.basetypes import Vector2, Triangle, Rectangle, Collider, Item, Decal, Camera
from src import sprites, config, sounds
from src.player import Player

class Level:
    def __init__(self, surface: pygame.surface, camera: Camera):

        self.map_name = None
        self.surface = surface
        self.camera = camera

        self.background = None
        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.dynamic_colliders = []
        self.decals = []
        self.items = []
        self.last_decal_velocity = 0
        self.height_offset = 0
        self.player_start = Vector2(70, 70)
        self.background_height = config.SCREEN_HEIGHT

    def load(self, map_name: str, player: Player):

        self.map_name = map_name

        self.static_colliders = []
        self.ramp_colliders = []
        self.wall_colliders = []
        self.dynamic_colliders = []
        self.decals = []
        self.items = []
        self.last_decal_velocity = 0

        self.background = pygame.image.load(path.join(sprites.assets_folder, 'maps', self.map_name, 'background.png'))
        self.background = self.background.convert_alpha()
        # self.background.set_colorkey((255, 0, 255))

        self.background_height = self.background.get_height()
        self.height_offset = -1 * (self.background_height - config.SCREEN_HEIGHT)


        map_file = path.join(sprites.assets_folder, 'maps', self.map_name, 'map.yaml')
        with open(map_file, 'r') as file:
            data = yaml.safe_load(file)

        start_pos = data.get('player_start', None)
        if start_pos is not None:
            self.player_start = Vector2(start_pos[0], start_pos[1])

        for item in data.get('player_items', []):
            if item['type'] == 'plasma':
                player.has_plasma = True
                player.plasma_ammo = item['ammo']
                player.animation.select_plasma()
                player.active_weapon = 'plasma'
            if item['type'] == 'rocket':
                player.has_rocket = True
                player.rocket_ammo = item['ammo']
                player.animation.select_rocket()
                player.active_weapon = 'rocket'

        for item in data['items']:
            self.items.append(Item(item['type'], Vector2(item['pos'][0], item['pos'][1] + self.height_offset), item['ammo']))

        for rect in data['static']:
            self.static_colliders.append(Collider(Rectangle(Vector2(rect[0], rect[1] + self.height_offset), rect[2], rect[3])))

        for rect in data['walls']:
            self.wall_colliders.append(Collider(Rectangle(Vector2(rect[0], rect[1] + self.height_offset), rect[2], rect[3])))

        for tri in data['ramps']:
            self.ramp_colliders.append(Collider(Triangle(Vector2(tri[0], tri[1] + self.height_offset), Vector2(tri[2], tri[3] + self.height_offset), Vector2(tri[4], tri[5] + self.height_offset))))

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
                if self.decals[i].sprite == sprites.PROJECTILE_PLASMA or self.decals[
                    i].sprite == sprites.PROJECTILE_ROCKET:
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

    def draw(self):
        self.surface.fill(config.BACKGROUND_COLOR)
        self.draw_background()
        self.draw_colliders()
        self.draw_items()
        self.draw_decals()

    def draw_background(self):
        """Extract rectangle from background image based on camera position"""
        self.surface.blit(self.background, (0, self.height_offset), (self.camera.pos.x, self.camera.pos.y, config.SCREEN_WIDTH, self.background_height))

    def draw_colliders(self):

        rect = pygame.Rect(0, 0, config.SCREEN_WIDTH, self.background_height)
        temp_surface = pygame.Surface(rect.size, pygame.SRCALPHA)

        for collider in self.static_colliders:
            view_pos = self.camera.to_view_space(collider.rect.pos)
            pygame.draw.rect(temp_surface, (0, 0, 0, 128), (view_pos.x, view_pos.y, collider.rect.w, collider.rect.h))

        for collider in self.wall_colliders:
            view_pos = self.camera.to_view_space(collider.rect.pos)
            pygame.draw.rect(temp_surface, (0, 0, 255, 128), (view_pos.x, view_pos.y, collider.rect.w, collider.rect.h))

        for triangle in self.ramp_colliders:
            pygame.draw.polygon(temp_surface, (160, 0, 44, 128), [
                (triangle.rect.p1.x - self.camera.pos.x, triangle.rect.p1.y - self.camera.pos.y),
                (triangle.rect.p2.x - self.camera.pos.x, triangle.rect.p2.y - self.camera.pos.y),
                (triangle.rect.p3.x - self.camera.pos.x, triangle.rect.p3.y - self.camera.pos.y)
            ])

        self.surface.blit(temp_surface, (0, 0))

    def draw_items(self):
        for item in self.items:
            if item.picked_up:
                continue
            view_pos = self.camera.to_view_space(item.pos)
            self.surface.blit(sprites.item_set, (view_pos.x, view_pos.y), item.sprite)

    def draw_decals(self):
        for decal in self.decals:
            self.surface.blit(sprites.item_set, (decal.x - self.camera.pos.x, decal.y - self.camera.pos.y), decal.sprite)

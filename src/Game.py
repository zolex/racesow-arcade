import os, pygame, math

from src.Scene import GameScene
from src.Map import Map
from src.Player import Player
from src import config
from src.Camera import Camera
from src.Settings import Settings
from src.Vector2 import Vector2
from src.Item import Item
from src.utils import color_gradient

from src.Decal import pre_load_decals
from src.Item import pre_load_items
from src.Projectile import pre_load_projectiles


class Game(GameScene):
    """Contains main loop and handles the game"""
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, settings: Settings = None):
        super().__init__(surface, clock, settings)

        self.quit = False

        SCALE = settings.get_scale()
        pre_load_decals(SCALE)
        pre_load_items(SCALE)
        pre_load_projectiles(SCALE)

        self.camera = Camera(Vector2(), self.settings)
        self.map = Map(self.surface, self.camera, self.settings)
        self.player = Player(self.surface, self.camera, self.settings)
        self.map.load('egypt', self.player)
        self.player.set_map(self.map)
        self.last_velocity = 0
        self.start_time = pygame.time.get_ticks()

        scale = self.settings.get_scale()
        self.font = pygame.font.Font('assets/console.ttf', int(8 * scale))
        self.font_small = pygame.font.Font('assets/console.ttf', int(6 * scale))
        self.font_big = pygame.font.Font('assets/console.ttf', int(12 * scale))

        hud = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'hud.png')).convert_alpha()
        self.hud = pygame.transform.scale(hud, (hud.get_width() / 2 * scale, hud.get_height() / 2 * scale))

        self.controllers: list[pygame.joystick.Joystick] = []
        pygame.joystick.init()
        for i in range(0, pygame.joystick.get_count()):
            controller = pygame.joystick.Joystick(i)
            self.controllers.append(controller)

    def draw(self):
        """Draw all GameObjects and sprites that are currently on screen"""
        self.map.draw()
        self.player.draw()
        self.map.draw_front()
        self.draw_hud()

    def draw_hud(self):
        hud_center = self.settings.width / 2
        hud_x = hud_center - self.hud.get_width() / 2
        hud_y = self.settings.height - self.hud.get_height()

        self.surface.blit(self.hud, (hud_x, hud_y))

        scale = self.settings.get_scale()

        fps = self.clock.get_fps()
        fpss = f"{0 if math.isinf(fps) else round(fps)}".rjust(3, "0")
        fps_text = self.font.render(f"FPS: {fpss}", True, (255, 255, 255))
        self.surface.blit(fps_text, (hud_center - 197 * scale, hud_y + 12 * scale))

        ups = f"{round(self.player.vel.x * 1000 / self.settings.get_scale())}".rjust(5, "0")
        fps_text = self.font_big.render(f"UPS: {ups}", True, color_gradient(self.player.vel.x, 0, 2))
        self.surface.blit(fps_text, (hud_center -75 * scale, hud_y + 10 * scale))

        if self.player.jump_timing is not None:
            if self.player.jump_timing < 0:
                early = f"{round(self.player.jump_timing, 2)}".rjust(4, "0")
                timing_text = self.font_big.render(f"DELTA: {early}", True, color_gradient(self.player.jump_timing, -20, 0))
            elif self.player.jump_timing > 0:
                late = f"{round(self.player.jump_timing, 2)}".rjust(4, "0")
                timing_text = self.font_big.render(f"DELTA: {late}", True, color_gradient(self.player.jump_timing, 20, 0))
            else:
                timing_text = self.font_big.render(f"DELTA:", True, (255, 255, 255))
        else:
            timing_text = self.font_big.render(f"DELTA:", True, (255, 255, 255))
        self.surface.blit(timing_text, (hud_center + 17 * scale, hud_y + 29 * scale))

        acc = f"{self.player.last_boost}".rjust(4, "0")
        acc_text = self.font_big.render(f"ACC: {acc}", True, color_gradient(self.player.last_boost, 0, 200))
        self.surface.blit(acc_text, (hud_center - 76 * scale, hud_y + 30 * scale))

        time_text = self.font_big.render(f"Time: {self.map.timer / 1000}", True, (255, 255, 255))
        self.surface.blit(time_text, (hud_center + 17 * scale, hud_y + 10 * scale))

        if self.player.has_plasma:
            self.surface.blit(Item.types['plasma'], (hud_center + 212 * scale, hud_y + 15 * scale))
            fps_text = self.font.render(f"{self.player.plasma_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (hud_center + 235 * scale, hud_y + 21 * scale))

        if self.player.has_rocket:
            self.surface.blit(Item.types['rocket'], (hud_center + 255 * scale, hud_y + 15 * scale))
            fps_text = self.font.render(f"{self.player.rocket_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (hud_center + 278 * scale, hud_y + 21 * scale))

    def update(self):

        # let it "load" a few milliseconds to avoid missing out collision checks
        # causing the player to fall out of the map at higher screen resolutions
        if self.start_time + 100 > pygame.time.get_ticks():
            return

        self.player.update()
        self.camera.update(self.player)
        self.map.update(self.player)

    def game_loop(self, main):
        keyboard = self.settings.mapping.get('keyboard', {})
        controller = self.settings.mapping.get('controller', {})

        mappings = {
            "left": lambda v: setattr(self.player, "pressed_left", v),
            "right": lambda v: setattr(self.player, "pressed_right", v),
            "up": lambda v: setattr(self.player, "pressed_up", v),
            "down": lambda v: setattr(self.player, "pressed_down", v),
            "jump": lambda v: self.player.input_jump(v),
            "wall_jump": lambda v: self.player.input_wall_jump(v),
            "shoot": lambda v: setattr(self.player, "pressed_shoot", v),
            "switch_weapon": lambda v: setattr(self.player, "pressed_switch_weapon", v),
            "back": lambda v: setattr(self, "quit", v),
        }

        while True:
            config.delta_time = self.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit = True
                    main.quit = True
                    break

                continue
                for mapping, callback in mappings.items():
                    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                        mapped_key = keyboard.get(mapping, {}).get('key')
                        if event.key == mapped_key:
                            callback(event.type == pygame.KEYDOWN)
                            break

                        mapped_mod = keyboard.get(mapping, {}).get('mod')
                        if mapped_mod and event.mod & mapped_mod:
                            callback(event.type == pygame.KEYDOWN)
                            break

                    elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                        mapped_button = controller.get(mapping, {}).get('button')
                        if event.button == mapped_button:
                            callback(event.type == pygame.JOYBUTTONDOWN)
                            break

                    elif event.type == pygame.JOYAXISMOTION:
                        mapped_axis = controller.get(mapping, {}).get('axis')
                        mapped_value = controller.get(mapping, {}).get('value')
                        if event.axis == mapped_axis:
                            callback(round(event.value) == mapped_value)
                            break

                    elif event.type == pygame.JOYHATMOTION:
                        mapped_hat = controller.get(mapping, {}).get('hat')
                        mapped_value = controller.get(mapping, {}).get('value')
                        if event.hat == mapped_hat:
                            callback(event.value == mapped_value)
                            break

            if self.quit:
                break

            self.update()
            self.draw()
            pygame.display.update()

        back = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'back.wav'))
        back.play()

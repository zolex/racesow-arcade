import os
import random

import pygame, math
from src.Level import Level
from src.Player import Player
from src.Projectile import Projectile
from src import sounds, config
from src.Camera import Camera
from src.Vector2 import Vector2
from src.Item import Item
from src.utils import color_gradient


class Game():
    """Contains main loop and handles the game"""
    def __init__(self, surface):
        self.surface = surface
        self.camera = Camera(Vector2(), config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.level = Level(self.surface, self.camera)
        self.player = Player(self.surface, self.camera)
        self.level.load('asd', self.player)
        self.camera.set_start_pos_y(self.level.player_start.y)
        self.player.set_level(self.level)
        self.last_velocity = 0
        self.font = pygame.font.Font(None, 16)
        self.font_small = pygame.font.Font(None, 14)
        self.font_big = pygame.font.Font(None, 20)

        self.hud = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'hud.png')).convert_alpha()

        pygame.joystick.init()
        if pygame.joystick.get_count():
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        pygame.mixer.music.load(sounds.main_theme)
        pygame.mixer.music.play()


    def draw(self):
        """Draw all GameObjects and sprites that are currently on screen"""
        self.level.draw()
        self.player.draw()
        self.level.draw_front()
        self.draw_hud()

    def draw_hud(self):

        #self.time.draw()

        hud_center = config.SCREEN_WIDTH / 2
        hud_x = hud_center - self.hud.get_width() / 2
        hud_y = config.SCREEN_HEIGHT - self.hud.get_height() / 2 - 20

        self.surface.blit(self.hud, (hud_x, hud_y))

        fps = config.clock.get_fps()
        fpss = f"{0 if math.isinf(fps) else round(fps)}".rjust(3, "0")
        fps_text = self.font.render(f"FPS: {fpss}", True, (255, 255, 255))
        self.surface.blit(fps_text, (hud_center - 240, hud_y + 17))

        acc = f"{self.player.last_boost}".rjust(4, "0")
        acc_text = self.font.render(f"ACC: {acc}", True, color_gradient(self.player.last_boost, 0, 200))
        self.surface.blit(acc_text, (hud_center - 65, hud_y + 14))


        if self.player.jumped_early is not None and self.player.jumped_early != float("inf"):
            early = f"{round(self.player.jumped_early, 2)}".rjust(4, "0")
            early_text = self.font_small.render(f"early: {early} ms", True, color_gradient(self.player.jumped_early, 20, 0))
            self.surface.blit(early_text, (hud_center - 65, hud_y + 24))
        elif self.player.jumped_late is not None and self.player.jumped_late != float("inf"):
            late = f"{round(self.player.jumped_late, 2)}".rjust(4, "0")
            late_text = self.font_small.render(f"late: {late} ms", True, color_gradient(self.player.jumped_late, 20, 0))
            self.surface.blit(late_text, (hud_center - 65, hud_y + 24))

        ups = f"{round(self.player.vel.x * 1000)}".rjust(5, "0")
        fps_text = self.font_big.render(f"UPS: {ups}", True, color_gradient(self.player.vel.x, 0, 2))
        self.surface.blit(fps_text, (hud_center + 30, hud_y + 15))

        time_text = self.font.render(f"Time: {self.level.timer / 1000}", True, (255, 255, 255))
        self.surface.blit(time_text, (hud_center + 160, hud_y + 16))

        if self.player.has_plasma:
            self.surface.blit(Item.item_plasma, (config.SCREEN_WIDTH - 45, config.SCREEN_HEIGHT - 20))
            fps_text = self.font.render(f"{self.player.plasma_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (config.SCREEN_WIDTH - 20, config.SCREEN_HEIGHT - 15))

        if self.player.has_rocket:
            self.surface.blit(Item.item_rocket, (config.SCREEN_WIDTH - 90, config.SCREEN_HEIGHT - 20))
            fps_text = self.font.render(f"{self.player.rocket_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (config.SCREEN_WIDTH - 60, config.SCREEN_HEIGHT - 15))

    def update(self):
        self.player.update()
        self.camera.update(self.player)
        self.level.update(self.player)

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis0 = self.joystick.get_axis(0)
                axis1 = self.joystick.get_axis(1)
                config.INPUT_DOWN = axis1 > 0.5
                config.INPUT_UP = axis1 < -0.5
                config.INPUT_LEFT = axis0 < -0.5
                config.INPUT_RIGHT = axis0 > 0.5

            if event.type == pygame.JOYBUTTONDOWN:
                config.INPUT_BUTTONS[event.button] = True

            if event.type == pygame.JOYBUTTONUP:
                config.INPUT_BUTTONS[event.button] = False

            if event.type == pygame.QUIT:
                return False


        if config.keys[pygame.K_ESCAPE] or config.INPUT_BUTTONS[8]:
            return False

        return True

    def game_loop(self):
        """Main game loop, updates and draws the level every frame"""
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        while True:
            config.delta_time = config.clock.tick(120)
            config.keys = pygame.key.get_pressed()
            config.mods = pygame.key.get_mods()
            if not self.handle_pygame_events():
                break

            self.update()
            self.draw()

            pygame.display.update()

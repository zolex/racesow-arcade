import os, pygame, math

from src.GameScene import GameScene
from src.Level import Level
from src.Player import Player
from src import sounds, config
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

        SCALE = settings.get_scale()
        pre_load_decals(SCALE)
        pre_load_items(SCALE)
        pre_load_projectiles(SCALE)

        self.camera = Camera(Vector2(), self.settings)
        self.level = Level(self.surface, self.camera, self.settings)
        self.player = Player(self.surface, self.camera, self.settings)
        self.level.load('asd', self.player)
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

        self.start_time = pygame.time.get_ticks()


    def draw(self):
        """Draw all GameObjects and sprites that are currently on screen"""
        self.level.draw()
        self.player.draw()
        self.level.draw_front()
        self.draw_hud()

    def draw_hud(self):

        #self.time.draw()

        hud_center = self.settings.width / 2
        hud_x = hud_center - self.hud.get_width() / 2
        hud_y = self.settings.height - self.hud.get_height() / 2 - 20

        self.surface.blit(self.hud, (hud_x, hud_y))

        fps = self.clock.get_fps()
        fpss = f"{0 if math.isinf(fps) else round(fps)}".rjust(3, "0")
        fps_text = self.font.render(f"FPS: {fpss}", True, (255, 255, 255))
        self.surface.blit(fps_text, (hud_center - 240, hud_y + 17))

        acc = f"{self.player.last_boost}".rjust(4, "0")
        acc_text = self.font.render(f"ACC: {acc}", True, color_gradient(self.player.last_boost, 0, 200))
        self.surface.blit(acc_text, (hud_center - 65, hud_y + 14))


        if self.player.jump_timing is not None:
            if self.player.jump_timing < 0:
                early = f"{round(self.player.jump_timing, 2)}".rjust(4, "0")
                early_text = self.font_small.render(f"early: {early} ms", True, color_gradient(self.player.jump_timing, -20, 0))
                self.surface.blit(early_text, (hud_center - 65, hud_y + 24))
            elif self.player.jump_timing > 0:
                late = f"{round(self.player.jump_timing, 2)}".rjust(4, "0")
                late_text = self.font_small.render(f"late: {late} ms", True, color_gradient(self.player.jump_timing, 20, 0))
                self.surface.blit(late_text, (hud_center - 65, hud_y + 24))

        ups = f"{round(self.player.vel.x * 1000 / self.settings.get_scale())}".rjust(5, "0")
        fps_text = self.font_big.render(f"UPS: {ups}", True, color_gradient(self.player.vel.x, 0, 2))
        self.surface.blit(fps_text, (hud_center + 30, hud_y + 15))

        time_text = self.font.render(f"Time: {self.level.timer / 1000}", True, (255, 255, 255))
        self.surface.blit(time_text, (hud_center + 160, hud_y + 16))

        if self.player.has_plasma:
            self.surface.blit(Item.types['plasma'], (self.settings.width - 45, self.settings.height - 20))
            fps_text = self.font.render(f"{self.player.plasma_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (self.settings.width - 20, self.settings.height - 15))

        if self.player.has_rocket:
            self.surface.blit(Item.types['rocket'], (self.settings.width - 90, self.settings.height - 20))
            fps_text = self.font.render(f"{self.player.rocket_ammo}", True, (255, 255, 255))
            self.surface.blit(fps_text, (self.settings.width - 60, self.settings.height - 15))

    def update(self):

        # let it "load" a few milliseconds to avoid missing out collision checks
        # causing the player to fall out of the level at higher screen resolutions
        if self.start_time + 100 > pygame.time.get_ticks():
            return

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
        while True:
            config.delta_time = self.tick()
            config.keys = pygame.key.get_pressed()
            config.mods = pygame.key.get_mods()
            if not self.handle_pygame_events():
                break

            self.update()
            self.draw()

            pygame.display.update()

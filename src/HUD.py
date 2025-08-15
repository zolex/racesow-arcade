import pygame, os, math
from src import config
from src.Item import Item
from src.utils import color_gradient, resource_path


class HUD:
    def __init__(self, game):
        self.game = game
        game_scale = game.settings.get_scale()
        hud = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'hud.png')).convert_alpha()
        self.hud = pygame.transform.scale(hud, (hud.get_width() / 2 * game_scale, hud.get_height() / 2 * game_scale))

        font_path = resource_path(os.path.join('assets', 'console.ttf'))
        self.font = pygame.font.Font(font_path, int(8 * game_scale))
        self.font_small = pygame.font.Font(font_path, int(6 * game_scale))
        self.font_big = pygame.font.Font(font_path, int(12 * game_scale))

        self.font_intro = pygame.font.Font(font_path, int(25 * game_scale))
        self.font_intro.set_bold(True)

        self.elapsed_time = 0
        self.timer = 0
        self.intro_alpha = 255 # grow
        self.intro_text = self.font_intro.render("LETS RACE", True, (255, 255, 255))

        self.ready = False

    def update(self):
        self.elapsed_time += config.delta_time
        if self.intro_alpha > 0:
            self.intro_alpha -= config.delta_time / 2
            self.intro_text.set_alpha(int(self.intro_alpha))
        else:
            self.intro_text = None
            self.ready = True

    def draw(self):

        if self.intro_text is not None:
            self.game.surface.blit(self.intro_text, (self.game.settings.resolution[0] / 2 - self.intro_text.get_width() / 2, self.game.settings.resolution[1] / 2 - self.intro_text.get_height() / 2), area=(0, 0, self.game.camera.w, self.game.camera.h))

        hud_center = self.game.settings.resolution[0] / 2
        hud_x = hud_center - self.hud.get_width() / 2
        hud_y = self.game.settings.resolution[1] - self.hud.get_height()

        self.game.surface.blit(self.hud, (hud_x, hud_y))
        game_scale = self.game.settings.get_scale()

        fps = self.game.clock.get_fps()
        fpss = f"{0 if math.isinf(fps) else round(fps)}".rjust(3, "0")
        fps_text = self.font.render(f"FPS: {fpss}", True, (255, 255, 255))
        self.game.surface.blit(fps_text, (hud_center - 197 * game_scale, hud_y + 12 * game_scale))

        ups = f"{round(self.game.player.vel.x * 1000 / self.game.settings.get_scale())}".rjust(5, "0")
        fps_text = self.font_big.render(f"UPS: {ups}", True, color_gradient(self.game.player.vel.x, 0, 2))
        self.game.surface.blit(fps_text, (hud_center -75 * game_scale, hud_y + 10 * game_scale))

        if self.game.player.jump_timing is not None:
            if self.game.player.jump_timing < 0:
                early = f"{round(self.game.player.jump_timing, 2)}".rjust(4, "0")
                timing_text = self.font_big.render(f"DELTA: {early}", True, color_gradient(self.game.player.jump_timing, -20, 0))
            elif self.game.player.jump_timing > 0:
                late = f"{round(self.game.player.jump_timing, 2)}".rjust(4, "0")
                timing_text = self.font_big.render(f"DELTA: {late}", True, color_gradient(self.game.player.jump_timing, 20, 0))
            else:
                timing_text = self.font_big.render(f"DELTA:", True, (255, 255, 255))
        else:
            timing_text = self.font_big.render(f"DELTA:", True, (255, 255, 255))
        self.game.surface.blit(timing_text, (hud_center + 17 * game_scale, hud_y + 29 * game_scale))

        acc = f"{self.game.player.last_boost}".rjust(4, "0")
        acc_text = self.font_big.render(f"ACC: {acc}", True, color_gradient(self.game.player.last_boost, 0, 200))
        self.game.surface.blit(acc_text, (hud_center - 76 * game_scale, hud_y + 30 * game_scale))

        time_text = self.font_big.render(f"Time: {self.game.map.timer / 1000}", True, (255, 255, 255))
        self.game.surface.blit(time_text, (hud_center + 17 * game_scale, hud_y + 10 * game_scale))

        if self.game.player.has_plasma:
            self.game.surface.blit(Item.types['plasma'], (hud_center + 212 * game_scale, hud_y + 15 * game_scale))
            fps_text = self.font.render(f"{self.game.player.plasma_ammo}", True, (255, 255, 255))
            self.game.surface.blit(fps_text, (hud_center + 235 * game_scale, hud_y + 21 * game_scale))

        if self.game.player.has_rocket:
            self.game.surface.blit(Item.types['rocket'], (hud_center + 255 * game_scale, hud_y + 15 * game_scale))
            fps_text = self.font.render(f"{self.game.player.rocket_ammo}", True, (255, 255, 255))
            self.game.surface.blit(fps_text, (hud_center + 278 * game_scale, hud_y + 21 * game_scale))

from .basetypes import Vector2
from . import sprites, config as c
import pygame as pygame


def get_scaled_rect(screen_size, base_size):
    sw, sh = screen_size
    bw, bh = base_size
    scale = min(sw / bw, sh / bh)
    new_size = (int(bw * scale), int(bh * scale))
    x = (sw - new_size[0]) // 2
    y = (sh - new_size[1]) // 2
    return pygame.Rect(x, y, *new_size)


class Menu():
    def __init__(self):
        self.selected = 0
        self.quit_state = None

        self.pressed_up = False
        self.pressed_down = False

        self.selector_pos = Vector2(239, 404)

        pygame.joystick.init()
        if pygame.joystick.get_count():
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def draw(self):
        c.surface.fill((0, 0, 0))
        c.surface.blit(sprites.menu, (0, 0))
        c.surface.blit(sprites.tile_set, (self.selector_pos.x, self.selector_pos.y), sprites.SELECTOR)

    def input_actions(self):
        if (c.keys[pygame.K_w] or c.INPUT_UP) and not self.pressed_down and not self.pressed_up:
            self.selected += 1
            self.pressed_up = True
        if (c.keys[pygame.K_s] or c.INPUT_DOWN) and not self.pressed_up and not self.pressed_down:
            self.selected -= 1
            self.pressed_down = True

        if not c.keys[pygame.K_w] and not c.INPUT_UP:
            self.pressed_up = False
        if not c.keys[pygame.K_s] and not c.INPUT_DOWN:
            self.pressed_down = False

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis0 = self.joystick.get_axis(0)
                axis1 = self.joystick.get_axis(1)
                c.INPUT_DOWN = axis1 > 0.5
                c.INPUT_UP = axis1 < -0.5
                c.INPUT_LEFT = axis0 < -0.5
                c.INPUT_RIGHT = axis0 > 0.5

            if event.type == pygame.JOYBUTTONDOWN:
                c.INPUT_BUTTONS[event.button] = True

            if event.type == pygame.JOYBUTTONUP:
                c.INPUT_BUTTONS[event.button] = False

    def check_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_state = 'exit'
                return False

        if c.keys[pygame.K_ESCAPE]:
            self.quit_state = 'exit'
            return False

        if (c.keys[pygame.K_RETURN] or c.INPUT_BUTTONS[0]) and self.selected % 2 == 0:
            c.INPUT_BUTTONS[0] = False
            self.quit_state = 'play'
            return False

        return True

    def menu_loop(self):
        while True:
            c.keys = pygame.key.get_pressed()
            c.clock.tick(60)

            self.handle_pygame_events()
            self.input_actions()
            if self.selected % 2 == 0:
                self.selector_pos = Vector2(239, 404)
            else:
                self.selector_pos = Vector2(239, 448)
            self.draw()

            if not self.check_for_quit():
                break

            c.surface.fill((0, 0, 0))
            scaled_rect = get_scaled_rect(c.surface.get_size(), c.surface.get_size())
            scaled_surface = pygame.transform.smoothscale(c.surface, scaled_rect.size)
            c.surface.blit(scaled_surface, scaled_rect.topleft)

            pygame.display.flip()

            
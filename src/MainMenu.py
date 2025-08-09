import os, tempfile
from _ast import Not
from time import sleep

import pygame
import yaml

from src.Game import Game
from src.Settings import Settings
from src.sounds import main_theme

from src.GameScene import GameScene
import src.config as config

class MainMenu(GameScene):

    ITEM_BACKGROUND_DEFAULT = (255, 255, 255, 128)  # semi-transparent white
    ITEM_BACKGROUND_ACTIVE = (255, 0, 0, 192)  # semi-transparent red
    ITEM_TEXT_DEFAULT = (0, 0, 0)
    ITEM_TEXT_ACTIVE = (255, 128, 16)

    MENU_SCALE = 256
    MENU_STYLES = {
        "default": {
            "font": pygame.font.Font(None, 30),
            "font_size": 30,
            "item_padding": 8,
            "item_margin": 10,
        },
        "small": {
            "font": pygame.font.Font(None, 16),
            "font_size": 16,
            "item_padding": 2,
            "item_margin": 4,
        },
        "medium": {
            "font": pygame.font.Font(None, 21),
            "font_size": 21,
            "item_padding": 4,
            "item_margin": 8,
        }
    }

    DEFAULT_SETTINGS = {
        'resolution': {
            'width': 640,
            'height': 240,
        },
        'fullscreen': False,
    }

    def __init__(self, surface, clock, settings: Settings):
        super().__init__(surface, clock, settings)
        self.quit = False
        self.splash: pygame.Surface = self.load_splash()
        self.selected_item = 0
        self.select = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'select.wav'))
        self.back = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'back.wav'))
        self.ok = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'ok.wav'))
        self.parent_menus = []
        self.active_menu = None
        self.load_menu()

        pygame.mixer.music.load(main_theme)
        pygame.mixer.music.play(loops=-1)

    def load_splash(self):
        splash = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'splash.jpg')).convert_alpha()

        # Get original dimensions
        orig_width, orig_height = splash.get_size()

        # Scale proportionally to screen width
        width = self.surface.get_width()
        scale_factor = width / orig_width
        new_height = int(orig_height * scale_factor)

        return pygame.transform.scale(splash, (width, new_height))

    def load_menu(self):
        menu_file = os.path.join(config.assets_folder, 'menu.yaml')
        with open(menu_file, 'r') as file:
            menu = yaml.safe_load(file)
            self.activate_menu(menu)

    def scale_style(self, style):
        return {
            "font": pygame.font.Font(None, int(style['font_size'] * self.surface.get_height() / MainMenu.MENU_SCALE)),
            "font_size": int(style['font_size'] * self.surface.get_height() / MainMenu.MENU_SCALE),
            "item_padding": int(style['item_padding'] * self.surface.get_height() / MainMenu.MENU_SCALE),
            "item_margin": int(style['item_margin'] * self.surface.get_height() / MainMenu.MENU_SCALE),
            "item_width": int(0.9 * self.surface.get_width() / (self.surface.get_width() / self.surface.get_height())),
        }

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.splash, (0, 0))

        if self.active_menu is None:
            return

        style = self.scale_style(MainMenu.MENU_STYLES.get(self.active_menu.get('style', 'default')))
        item_height = style['font_size'] + style['item_padding']
        total_height = len(self.active_menu.get('items')) * (item_height + style['item_margin']) - style['item_margin']
        start_y = self.surface.get_height() - total_height - 20
        rect_x = (self.surface.get_width() - style['item_width']) // 2

        # menu title
        title_style = self.scale_style(MainMenu.MENU_STYLES.get('medium'))
        text_surface = title_style['font'].render(self.active_menu.get('title'), True, (255, 255, 255))
        text_width, text_height = text_surface.get_size()
        text_x = self.settings.width - text_width - title_style['item_margin']
        self.surface.blit(text_surface, (text_x, title_style['item_margin']))

        menu_index = 0
        for item in self.active_menu.get('items'):

            if menu_index == self.selected_item:
                background_color = MainMenu.ITEM_BACKGROUND_ACTIVE
                text_color = MainMenu.ITEM_TEXT_ACTIVE
            else:
                background_color = MainMenu.ITEM_BACKGROUND_DEFAULT
                text_color = MainMenu.ITEM_TEXT_DEFAULT

            text_surface = style['font'].render(item.get('text'), True, text_color)
            text_width, text_height = text_surface.get_size()
            rect_height = item_height
            rect_y = start_y + menu_index * (item_height + style['item_margin'])

            # Draw transparent rectangle
            rect_surface = pygame.Surface((style['item_width'], rect_height), pygame.SRCALPHA)
            rect_surface.fill(background_color)
            self.surface.blit(rect_surface, (rect_x, rect_y))

            # Center text on the rectangle
            text_x = rect_x + (style['item_width'] - text_width) // 2
            text_y = rect_y + (rect_height - text_height) // 2
            self.surface.blit(text_surface, (text_x, text_y))

            menu_index += 1

    def update(self):
        pass

    def handle_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_back_or_quit()
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.menu_up()
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.menu_down()
                elif event.key == pygame.K_RETURN:
                    self.menu_ok()


    def menu_ok(self):
        self.ok.play()

        selected_item = self.active_menu.get('items')[self.selected_item]

        if selected_item.get('action') == 'play':
            Game(self.surface, self.clock, self.settings).game_loop()

        elif selected_item.get('action') == 'menu':
            self.activate_menu(selected_item)

        elif selected_item.get('action') == 'back':
            self.menu_back_or_quit()

        elif selected_item.get('action') == 'resolution':
            self.change_resolution(selected_item.get('width'), selected_item.get('height'))

        elif selected_item.get('action') == 'fps':
            self.change_max_fps(selected_item.get('fps'))

        elif selected_item.get('action') == 'switch_fullscreen':
            self.switch_fullscreen()

        elif selected_item.get('action') == 'quit':
            sleep(1)
            self.menu_back_or_quit()

    def activate_menu(self, menu_item):
        if self.active_menu is not None:
            self.active_menu['selected_item'] = self.selected_item
            self.parent_menus.append(self.active_menu)

        self.active_menu = menu_item.get('menu')
        self.selected_item = menu_item.get('selected_item', 0)

        if menu_item.get('action') == 'menu':
            items = menu_item.get('menu').get('items')
            for item in items:
                if item.get('action') == 'resolution' and self.settings.width == int(item.get('width')) and self.settings.height == int(item.get('height')):
                    self.selected_item = items.index(item)
                    break
                elif item.get('action') == 'fps' and self.settings.max_fps == int(item.get('fps')):
                    self.selected_item = items.index(item)
                    break

    def reload(self):
        display_options = pygame.SCALED
        if self.settings.fullscreen:
            display_options += pygame.FULLSCREEN

        self.surface = pygame.display.set_mode((self.settings.width, self.settings.height), display_options)
        self.splash = self.load_splash()

    def switch_fullscreen(self):
        self.settings.fullscreen = not self.settings.fullscreen
        self.reload()

    def change_resolution(self, width, height):
        self.settings.width = int(width)
        self.settings.height = int(height)
        self.reload()

    def change_max_fps(self, fps):
        self.settings.max_fps = int(fps)
        self.reload()

    def menu_back_or_quit(self):
        if len(self.parent_menus) > 0:
            self.active_menu = self.parent_menus.pop()
            self.selected_item = self.active_menu.get('selected_item', 0)
        else:
            self.quit = True

    def menu_up(self):
        if self.selected_item > 0:
            self.selected_item -= 1
            self.select.play()

    def menu_down(self):
        if self.selected_item < len(self.active_menu.get('items')) - 1:
            self.selected_item += 1
            self.select.play()

    def game_loop(self):
        while True:
            self.handle_inputs()
            if self.quit:
                break

            self.tick()
            self.update()
            self.draw()
            pygame.display.update()
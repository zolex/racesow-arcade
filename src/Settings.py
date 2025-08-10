import os, tempfile, yaml

import pygame


class Settings:
    def __init__(self):
        self.settings_file = os.path.join(tempfile.gettempdir(), 'racesow_acrade.yaml')
        self.width = 640
        self.height = 320
        self.fullscreen = False
        self.max_fps = 120

        self.mapping = {
            'controller': {
                'up': {'axis': 1, 'value': -1},
                'down': {'axis': 1, 'value': 1},
                'left': {'axis': 0, 'value': -1},
                'right': {'axis': 0, 'value': 1},
                'shoot': {'button': 2},
                'jump': {'button': 0},
                'wall_jump': {'button': 1},
                'switch_weapon': {'button': 3},
                'select': {'button': 2},
                'back': {'button': 8},
                'menu': {'button': 7},
            },
            'keyboard': {
                'up': {'key': pygame.K_w},
                'down': {'key': pygame.K_s},
                'left': {'key': pygame.K_a},
                'right': {'key': pygame.K_d},
                'shoot': {'key': pygame.K_RETURN},
                'jump': {'key': pygame.K_SPACE},
                'wall_jump': {'mod': pygame.KMOD_ALT},
                'switch_weapon': {'mod': pygame.KMOD_CTRL},
                'select': {'key': pygame.K_RETURN},
                'back': {'key': pygame.K_ESCAPE},
                'menu': {'key': pygame.K_F1},
            },
        }

    def get_scale(self):
        return self.height / 320

    def load(self):
        if not os.path.isfile(self.settings_file):
            return

        with open(self.settings_file, 'r') as file:
            data = yaml.safe_load(file)

        self.width = data.get('resolution', {}).get('width', 640)
        self.height = data.get('resolution', {}).get('height', 320)
        self.fullscreen = data.get('fullscreen', False)
        self.max_fps = data.get('max_fps', 120)

        mapping = data.get('mapping', {})
        controller = mapping.get('controller', {})
        for input in controller:
            self.mapping['controller'][input] = controller[input]

        keyboard = mapping.get('keyboard', {})
        for input in keyboard:
            self.mapping['keyboard'][input] = keyboard[input]

    def save(self):
        settings = {
            "resolution": {
                "width": self.width,
                "height": self.height,
            },
            "fullscreen": self.fullscreen,
            "max_fps": self.max_fps,
            "mapping": self.mapping,
        }

        with open(self.settings_file, "w") as file:
            yaml.dump(settings, file, default_flow_style=False)

import os, pygame, random, tempfile, yaml
from pygame._sdl2 import Window
from src import config
from src.Input import DEFAULT_INPUT

class Settings:
    def __init__(self):
        self.settings_file = os.path.join(tempfile.gettempdir(), 'racesow_acrade.yaml')
        self.resolution = [640, 320]
        self.fullscreen = False
        self.max_fps = 120
        self.music_enabled = True
        self.music_volume = 7
        self.volume = 10
        self.max_volume = 10
        self.cursor = 'corn'
        self.camera_style = 'default'
        self.new_plasma = False

        self.game_sounds = [
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'player', 'jump_1.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'player', 'jump_2.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'player', 'wj_1.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'player', 'wj_2.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'player', 'death.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'items', 'pickup.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'items', 'rocket.ogg')),
            pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'items', 'empty_shot.mp3')),
        ]

        self.mapping = DEFAULT_INPUT

    def get_volume(self):
        return self.volume / self.max_volume

    def play_game_sound(self):
        sound = self.game_sounds[random.randint(0, len(self.game_sounds) - 1)]
        sound.set_volume(self.get_volume())
        sound.play()

    def increase_volume(self):
        new_vol = min(self.max_volume, self.volume + 1)
        if new_vol == self.volume:
            return
        self.volume = new_vol
        self.play_game_sound()

    def reduce_volume(self):
        new_vol = max(1, self.volume - 1)
        if new_vol == self.volume:
            return
        self.volume = new_vol
        self.play_game_sound()

    def increase_music_volume(self):
        self.music_volume = min(self.max_volume, self.music_volume + 1)
        self.update_music_volume()

    def reduce_music_volume(self):
        self.music_volume = max(1, self.music_volume - 1)
        self.update_music_volume()

    def update_music_volume(self):
        pygame.mixer.music.set_volume(self.music_volume / self.max_volume)

    def get_scale(self):
        return self.resolution[1] / 320

    def get(self, setting):
        return getattr(self, setting, None)

    def set(self, setting, value):
        return setattr(self, setting, value)

    def reduce(self, setting):
        if setting == 'volume':
            self.reduce_volume()
        elif setting == 'music_volume':
            self.reduce_music_volume()

    def increase(self, setting):
        if setting == 'volume':
            self.increase_volume()
        elif setting == 'music_volume':
            self.increase_music_volume()

    def load(self):
        if not os.path.isfile(self.settings_file):
            return

        with open(self.settings_file, 'r') as file:
            try:
                data = yaml.safe_load(file)
            except:
                data = {}


        resolution = data.get('resolution', self.resolution)
        if isinstance(resolution, list):
            self.resolution = resolution

        fullscreen = data.get('fullscreen', self.fullscreen)
        if isinstance(fullscreen, bool):
            self.fullscreen = fullscreen

        max_fps = data.get('max_fps', self.max_fps)
        if isinstance(max_fps, int):
            self.max_fps = max_fps

        volume = data.get('volume', self.volume)
        if isinstance(volume, int):
            self.volume = volume

        music_volume = data.get('music_volume', self.music_volume)
        if isinstance(music_volume, int):
            self.music_volume = music_volume

        music_enabled = data.get('music_enabled', self.music_enabled)
        if isinstance(music_enabled, bool):
            self.music_enabled = music_enabled

        window = Window.from_display_module()
        position = data.get('window', {}).get('position', {'x': 0, 'y': 0})
        window.position = (position.get('x', 0), position.get('y', 0))

        pygame.mixer.music.set_volume(self.music_volume / (self.max_volume / self.volume))

        mapping = data.get('mapping', {})
        controller = mapping.get('controller', {})
        for input in controller:
            self.mapping['controller'][input] = controller[input]

        keyboard = mapping.get('keyboard', {})
        for input in keyboard:
            self.mapping['keyboard'][input] = keyboard[input]

    def save(self):

        window = Window.from_display_module()
        x, y = window.position

        settings = {
            "resolution": self.resolution,
            "fullscreen": self.fullscreen,
            "max_fps": self.max_fps,
            "mapping": self.mapping,
            "volume": self.volume,
            "music_volume": self.music_volume,
            "music_enabled": self.music_enabled,
            "window": {
                "position": {'x': x, 'y': y},
            }
        }

        with open(self.settings_file, "w") as file:
            yaml.dump(settings, file, default_flow_style=False)

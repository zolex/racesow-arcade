import os, stat, pygame, random, tempfile, yaml
from pathlib import Path
from pygame._sdl2 import Window
from src import config
from src.Input import DEFAULT_INPUT

class Settings:
    def __init__(self):
        self.resolution = [740, 400]
        self.fullscreen = False
        self.max_fps = 120
        self.music_enabled = True
        self.music_volume = 7
        self.volume = 10
        self.max_volume = 10
        self.cursor = 'corn'
        self.camera_style = 'fixed'
        self.launch_on_ramp_jump = True
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

        self.settings_file = self.get_settings_file()
        self.mapping = DEFAULT_INPUT


    def get_settings_file(self):
        filename = 'config.yaml'
        subdir = '.racesow_arcade'
        possible_dirs = [Path.home(), tempfile.gettempdir()]
        for dir in possible_dirs:
            settings_file = os.path.join(dir, subdir, filename)
            if os.path.isfile(settings_file) and os.access(settings_file, os.W_OK):
                return settings_file
            elif os.access(dir, os.W_OK):
                folder = dir / subdir
                folder.mkdir(exist_ok=True)
                return settings_file

        return filename

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
        setattr(self, setting, value)
        if setting == 'music_volume':
            self.update_music_volume()

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

        camera_style = data.get('camera_style', self.camera_style)
        if isinstance(camera_style, str):
            self.camera_style = camera_style

        volume = data.get('volume', self.volume)
        if isinstance(volume, int):
            self.volume = volume

        music_volume = data.get('music_volume', self.music_volume)
        if isinstance(music_volume, int):
            self.music_volume = music_volume

        music_enabled = data.get('music_enabled', self.music_enabled)
        if isinstance(music_enabled, bool):
            self.music_enabled = music_enabled

        #window = Window.from_display_module()
        #position = data.get('window', {}).get('position', {'x': 0, 'y': 0})
        #window.position = (position.get('x', 0), position.get('y', 0))

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
            "camera_style": self.camera_style,
            "volume": self.volume,
            "music_volume": self.music_volume,
            "music_enabled": self.music_enabled,
            "window": {
                "position": {'x': x, 'y': y},
            }
        }

        with open(self.settings_file, "w") as file:
            yaml.dump(settings, file, default_flow_style=False)

        os.chmod(self.settings_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

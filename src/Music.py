import os, pygame
import random
from src.Settings import Settings
from src import config


class Music:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.current_track = None
        self.current_index = None
        self.music = []
        music_path = os.path.join(config.assets_folder, 'music')
        for file in os.listdir(music_path):
            if file.endswith('ogg'):
                self.music.append(os.path.join(music_path, file))

    def play(self, force=False):
        if self.current_track is not None and not force:
            return

        if self.settings.music_enabled:
            index = None
            while index is None or index == self.current_index:
                index = random.randint(0, len(self.music) - 1)
            track = self.music[index]
            filename = os.path.basename(track)
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(loops=-1, fade_ms=3886)
            self.current_track = os.path.splitext(filename)[0]
            self.current_index = index

    def stop(self):
        self.current_track = None
        self.current_index = None
        pygame.mixer.music.fadeout(1337)

    def next(self):
        self.play(True)
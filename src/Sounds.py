import random

import pygame
from os import path
from src import config



class Sounds:
    def __init__(self, volume):

        sounds_folder = path.join(config.assets_folder, 'sounds')

        self.walljump1 = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'wj_1.ogg'))
        self.walljump1.set_volume(volume * 0.9)

        self.walljump2 = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'wj_2.ogg'))
        self.walljump2.set_volume(volume * 0.9)

        self.jump1 = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'jump_1.ogg'))
        self.jump1.set_volume(volume * 0.9)

        self.jump2 = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'jump_2.ogg'))
        self.jump2.set_volume(volume * 0.9)

        self.death = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'death.ogg'))
        self.death.set_volume(volume)

        self.plasma = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'plasma.ogg'))
        self.plasma.set_volume(0.7 * volume)

        self.rocket = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'rocket.ogg'))
        self.rocket.set_volume(volume)

        self.rocket_fly = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'rocket_fly.mp3'))
        self.rocket_fly.set_volume(volume)

        self.rocket_launch = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'rocket_launch.mp3'))
        self.rocket_launch.set_volume(volume)

        self.pickup = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'pickup.ogg'))
        self.pickup.set_volume(volume * 0.7)

        self.weapon_empty = pygame.mixer.Sound(path.join(sounds_folder, 'items', 'empty_shot.mp3'))
        self.weapon_empty.set_volume(0.7 * volume)

        self.slide = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'slide.ogg'))
        self.slide.set_volume(volume * 0.25)

        self.steps = []
        for i in range(1, 17):
            sound = pygame.mixer.Sound(path.join(sounds_folder, 'player', 'step_' + str(i) + '.ogg'))
            sound.set_volume(1)
            self.steps.append(sound)

    def play_step(self):
        step = random.randint(0, len(self.steps) - 1)
        #print("play step ", step)
        self.steps[step].play()

    def play_jump(self):
        if random.choice([True, False]):
            self.jump1.play()
        else:
            self.jump2.play()


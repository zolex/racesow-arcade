import pygame as pg
from os import path

pg.init()
#initialize mixer
pg.mixer.pre_init(44100, 16, 2, 4096)

sounds_folder = path.join(path.dirname(path.dirname(__file__)), 'assets', 'sounds')

#Load all sounds
walljump1 = pg.mixer.Sound(path.join(sounds_folder, 'player', 'wj_1.ogg'))
walljump2 = pg.mixer.Sound(path.join(sounds_folder, 'player', 'wj_2.ogg'))
jump1 = pg.mixer.Sound(path.join(sounds_folder, 'player', 'jump_1.ogg'))
jump2 = pg.mixer.Sound(path.join(sounds_folder, 'player', 'jump_2.ogg'))
death = pg.mixer.Sound(path.join(sounds_folder, 'player', 'death.ogg'))
plasma = pg.mixer.Sound(path.join(sounds_folder, 'items', 'plasma.ogg'))
rocket = pg.mixer.Sound(path.join(sounds_folder, 'items', 'rocket.ogg'))
rocket_fly = pg.mixer.Sound(path.join(sounds_folder, 'items', 'rocket_fly.mp3'))
rocket_launch = pg.mixer.Sound(path.join(sounds_folder, 'items', 'rocket_launch.mp3'))
pickup = pg.mixer.Sound(path.join(sounds_folder, 'items', 'pickup.ogg'))
weapon_empty = pg.mixer.Sound(path.join(sounds_folder, 'items', 'empty_shot.mp3'))
weapon_empty.set_volume(0.6)

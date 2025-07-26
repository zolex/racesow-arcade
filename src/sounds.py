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

#Get path to music files
main_theme = path.join(sounds_folder, 'menu_1.ogg')


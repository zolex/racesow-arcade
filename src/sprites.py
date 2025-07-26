from os import path

import pygame as pg

graphics_folder = path.join(path.dirname(path.dirname(__file__)), 'assets')

background = pg.image.load(path.join(graphics_folder, 'maps', 'egypt', 'background.png'))
#menu = pg.image.load(path.join(graphics_folder, 'menu.png'))
digits = pg.image.load(path.join(graphics_folder, 'graphics', 'digits.png'))

player = pg.image.load(path.join(graphics_folder, 'graphics', 'player.png'))
new_size = (player.get_width() // 2, player.get_height() // 2)  # downscale by 2
player_set = pg.transform.smoothscale(player, new_size)

#Sprite rectangles to retrieve section of atlas
EMPTY_SPRITE = (240, 48, 48, 48)
SELECTOR = (394, 12, 24, 24)

DEAD_PLAYER = (0, 0 , 64, 64)

PLAYER_IDLE = (0, 0, 64, 64)
PLAYER_RUN = [
    (0, 0 , 64, 64),
    (64, 0, 64, 64),
    (128, 0, 64, 64),
    (192, 0, 64, 64),
    (256, 0, 64, 64),
    (320, 0, 64, 64),
    (0, 64, 64, 64),
    (64, 64, 64, 64),
    (128, 64, 64, 64),
    (192, 64, 64, 64),
    (256, 64, 64, 64),
    (320, 64, 64, 64),
]
PLAYER_JUMP = (0, 0 , 64, 64)
PLAYER_BRAKE = (0, 0 , 64, 64)
PLAYER_CROUCH = (0, 128, 64, 64)
PLAYER_SWIM = (0, 0 , 64, 64)






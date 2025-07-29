from os import path

import pygame as pg

graphics_folder = path.join(path.dirname(path.dirname(__file__)), 'assets')

background = pg.image.load(path.join(graphics_folder, 'maps', 'egypt', 'background.png'))
digits = pg.image.load(path.join(graphics_folder, 'graphics', 'digits.png'))

I_SCALE    = 0.15
I_WIDTH    = 128
I_HEIGHT   = 128
I_WIDTH_S  = I_WIDTH  * I_SCALE
I_HEIGHT_S = I_HEIGHT * I_SCALE
items = pg.image.load(path.join(graphics_folder, 'graphics', 'items.png'))
new_size = (items.get_width() * I_SCALE, items.get_height() * I_SCALE)
item_set = pg.transform.smoothscale(items, new_size)

ITEM_ROCKET       = (0    * I_SCALE, 0    * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
DECAL_ROCKET      = (0    * I_SCALE, 128  * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
PROJECTILE_ROCKET = (0    * I_SCALE, 256  * I_SCALE, I_WIDTH_S, I_HEIGHT_S)

ITEM_PLASMA       = (128  * I_SCALE, 0    * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
DECAL_PLSAMA      = (128  * I_SCALE, 128  * I_SCALE, I_WIDTH_S, I_HEIGHT_S)
PROJECTILE_PLASMA = (128  * I_SCALE, 128  * I_SCALE, I_WIDTH_S, I_HEIGHT_S)

P_SCALE    = 0.5
P_WIDTH    = 128
P_HEIGHT   = 128
P_WIDTH_S  = P_WIDTH  * P_SCALE
P_HEIGHT_S = P_HEIGHT * P_SCALE

player = pg.image.load(path.join(graphics_folder, 'graphics', 'player.png'))
new_size = (player.get_width() * P_SCALE, player.get_height() * P_SCALE)
player_set = pg.transform.smoothscale(player, new_size)


DEAD_PLAYER          = (0    * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_IDLE          = (128  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_IDLE_PLASMA   = (128  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_IDLE_ROCKET   = (128  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_CROUCH        = (0    * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_CROUCH_PLASMA = (0    * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_CROUCH_ROCKET = (0    * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_SLIDE         = (0    * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_SLIDE_PLASMA  = (256  * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_SLIDE_ROCKET  = (128  * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_PLASMA_CLIMB  = (640  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLAYER_RUN = [
                       (0    * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (0    * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_RUN_PLASMA = [
                       (0    * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (0    * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_RUN_ROCKET = [
                       (0    * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (0    * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (256  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (640  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_WALLJUMP = [
                       (256  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_WALLJUMP_PLASMA = [
                       (256  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_WALLJUMP_ROCKET = [
                       (256  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (512  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_SHOOT_PLASMA = [
                       (640  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
PLAYER_SHOOT_ROCKET = [
                       (0    * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (128  * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
                       (384  * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

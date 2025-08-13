import pygame

class Input:
    KEYBOARD = 'keyboard'
    CONTROLLER = 'controller'
    SELECT = 'select'
    BACK = 'back'
    MENU = 'menu'
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    JUMP = 'jump'
    WALL_JUMP = 'wall_jump'
    SHOOT = 'shoot'
    SWITCH_WEAPON = 'switch_weapon'
    ANY = '*'

DEFAULT_INPUT = {
    Input.CONTROLLER: {
        Input.UP: {'axis': 1, 'value': -1},
        Input.DOWN: {'axis': 1, 'value': 1},
        Input.LEFT: {'axis': 0, 'value': -1},
        Input.RIGHT: {'axis': 0, 'value': 1},
        Input.SHOOT: {'button': 2},
        Input.JUMP: {'button': 0},
        Input.WALL_JUMP: {'button': 1},
        Input.SWITCH_WEAPON: {'button': 3},
        Input.SELECT: {'button': 2},
        Input.BACK: {'button': 8},
        Input.MENU: {'button': 7},
    },
    Input.KEYBOARD: {
        Input.UP: {'key': pygame.K_w},
        Input.DOWN: {'key': pygame.K_s},
        Input.LEFT: {'key': pygame.K_a},
        Input.RIGHT: {'key': pygame.K_d},
        Input.SHOOT: {'key': pygame.K_RETURN},
        Input.JUMP: {'key': pygame.K_SPACE},
        Input.WALL_JUMP: {'mod': pygame.KMOD_ALT},
        Input.SWITCH_WEAPON: {'mod': pygame.KMOD_CTRL},
        Input.SELECT: {'key': pygame.K_RETURN},
        Input.BACK: {'key': pygame.K_ESCAPE},
        Input.MENU: {'key': pygame.K_F1},
    }
}


import os

assets_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')

#Shared variables
screen = None
surface = None
clock = None
keys = None
mods = None
delta_time = None
final_count_down = False

#Controller Inputs
INPUT_DOWN = False
INPUT_UP = False
INPUT_LEFT = False
INPUT_RIGHT = False
INPUT_BUTTONS = {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False}

#Colors for level loading
BLACK = (0, 0, 0, 255)
BLUE = (0, 0, 255, 255)
RED = (255, 0, 0, 255)
GRAY = (100, 100, 100, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (100, 255, 100, 255)
BROWN = (124, 66, 0, 255)
PURPLE = (124, 0, 255, 255)
PINK = (255, 0, 255, 255)

#Background color of level
BACKGROUND_COLOR = (107, 140, 255)

#Window settings
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
CAPTION = 'Racesow Arcade'

#Physics values
PLAYER_ACCELERATION = 0.00015
MAX_RUN_VEL = 0.75
MAX_OVERAL_VEL = 2
MAX_FALL_VEL = 1
GRAVITY = 0.00092
MAX_JUMP_HEIGHT = 100000
MAX_WALLJUMP_HEIGHT = 42

#Velocities for different events
BOUNCE_VEL = 0.1
JUMP_VELOCITY = -0.325
WALLJUMP_VELOCITY = -0.22
DEATH_VEL_Y = -0.35

#End of level settings
MAXIMUM_CAMERA_SCROLL = 999999999999999
LEVEL_END_X = 999999999999999

#Distance from left side of the screen, when camera starts following
CAMERA_FOLLOW_X = 150

#Sets timer value so animations start instantly instead of counting up first
INITIAL_TIMER_VALUE = 1000











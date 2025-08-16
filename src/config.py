import os

assets_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')

FPS = 120

#Shared variables
screen = None
surface = None
clock = None
keys = None
mods = None
delta_time = None
final_count_down = False

#Colors for map loading
BLACK = (0, 0, 0, 255)
BLUE = (0, 0, 255, 255)
RED = (255, 0, 0, 255)
GRAY = (100, 100, 100, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (100, 255, 100, 255)
BROWN = (124, 66, 0, 255)
PURPLE = (124, 0, 255, 255)
PINK = (255, 0, 255, 255)

#Background color of map
BACKGROUND_COLOR = (107, 140, 255)

CAPTION = 'Racesow Arcade'

# Physics values

PLAYER_ACCELERATION=0.00015
PLAYER_AIR_ACCEL=0.003
PLAYER_AIR_BREAK=0.0003
FRICTION_BASE_FACTOR=0.9323
FRICTION_VELOCITY_SCALING=0.005
FRICTION_GRAVITY_EFFECT=0.002

MAX_OVERAL_VEL = float("inf")
MAX_FALL_VEL = 1
GRAVITY = 0.00092
MAX_JUMP_HEIGHT = 100000
MAX_WALLJUMP_HEIGHT = 42

ROCKET_DOWN_OFFSET_X = 9
ROCKET_DOWN_OFFSET_Y = 10

#Velocities for different events
BOUNCE_VEL = 0.1
JUMP_VELOCITY = -0.325
WALLJUMP_VELOCITY = -0.22
DEATH_VEL_Y = -0.35

#Sets timer value so animations start instantly instead of counting up first
INITIAL_TIMER_VALUE = 1000











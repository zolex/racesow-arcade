from src import config
from src.basetypes import Vector2

def clamp(x, a, b):
    """Clamps value x between a and b"""
    return max(a, min(b, x))

def accelerate(obj, accel_x, accel_y, limit_x = None):
    """Accelerate until the limit is reached"""
    obj.vel += Vector2(accel_x, accel_y) * config.delta_time
    if limit_x != None:
        obj.vel.x = clamp(obj.vel.x, 0, limit_x)

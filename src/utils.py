from src import config
from src.Vector2 import Vector2

def clamp(x, a, b):
    """Clamps value x between a and b"""
    return max(a, min(b, x))

def accelerate(obj, accel_x, accel_y, limit_x = None):
    """Accelerate until the limit is reached"""
    obj.vel += Vector2(accel_x, accel_y) * config.delta_time
    if limit_x != None:
        obj.vel.x = clamp(obj.vel.x, 0, limit_x)

def color_gradient(value, min_value, max_value):
    """Returns (R, G, B) color from red (min) → yellow (mid) → green (max).
    value: the value to grade
    min_value: gradient starts here (red)
    max_value: gradient ends here (green)
    """
    # Clamp value to [min_value, max_value]
    value = max(min_value, min(max_value, value))
    mid = (min_value + max_value) / 2

    if value <= mid:
        # Red to Yellow
        r = 255
        g = int(255 * (value - min_value) / (mid - min_value))
        b = 0
    else:
        # Yellow to Green
        r = int(255 * (1 - (value - mid) / (max_value - mid)))
        g = 255
        b = 0
    return (r, g, b)

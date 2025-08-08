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

    Args:
        value: The value to grade.
        min_value: The gradient's starting point.
        max_value: The gradient's ending point.

    Returns:
        A tuple (R, G, B) representing the color.
    """
    # Check if the min and max values are inverted.
    # If so, swap them and remember to invert the final color.
    inverse_gradient = False
    if min_value > max_value:
        min_value, max_value = max_value, min_value
        inverse_gradient = True

    # Handle the edge case where min_value and max_value are the same
    if min_value == max_value:
        return (127, 127, 0)  # Return a neutral yellow if there is no range

    # Clamp value to the new [min_value, max_value] range
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

    # If the original min and max were inverted, flip the color.
    if inverse_gradient:
        return (g, r, b)
    else:
        return (r, g, b)

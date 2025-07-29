import pygame

from src import sprites, config as c
import math

class GameObject():
    def __init__(self, rect):
        self.rect = rect

    def __getattr__(self, name):
        """Makes lines shorter by not having to type rect.pos when retrieving position"""
        if name == 'pos':
            return self.rect.pos
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Makes lines shorter by not having to type rect.pos when setting position"""
        if name == 'pos':
            self.rect.pos = value
        else:
            object.__setattr__(self, name, value)

class Collider(GameObject):
    """Class for static colliders"""
    def __init__(self, rect):
        super(Collider, self).__init__(rect)

class Vector2():
    """Vector class for 2D positions and velocities"""
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __mul__(self, other):
        """Overload multiplication"""
        return Vector2(self.x * other, self.y * other)

    def __add__(self, other):
        """Overload Addition"""
        return Vector2(self.x + other.x, self.y + other.y)

class Rectangle():
    """Rectangle class for collider rectangles"""
    def __init__(self, pos = Vector2(), w = 0, h = 0):
        self.pos = pos
        self.w = w
        self.h = h

    def overlaps(self, other):
        """Check if two rectangles overlap"""
        return not(other.pos.x + other.w <= self.pos.x or 
                   other.pos.x >= self.pos.x + self.w or
                   other.pos.y + other.h <= self.pos.y or
                   other.pos.y >= self.pos.y + self.h)

    def check_collisions(self, collider_list):
        """Check collisions between two rectangles, if in a rangle of 100px, returns a single collider"""
        for collider in collider_list:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.rect.w >= 100: #Wider colliders are checked anyway
                if self.overlaps(collider.rect):
                    return collider

    def check_triangle_collisions(self, collider_list):
        """Returns True if this rectangle collides with the given triangle."""

        def point_in_rect(pt):
            return (self.pos.x <= pt.x <= self.pos.x + self.w) and \
                (self.pos.y <= pt.y <= self.pos.y + self.h)

        def point_in_triangle(pt, t):
            def sign(p1, p2, p3):
                return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

            b1 = sign(pt, t.p1, t.p2) < 0.0
            b2 = sign(pt, t.p2, t.p3) < 0.0
            b3 = sign(pt, t.p3, t.p1) < 0.0
            return (b1 == b2) and (b2 == b3)

        for collider in collider_list:
            triangle = collider.rect

            # 1. Check if any triangle vertex is inside rectangle
            if any(point_in_rect(p) for p in [triangle.p1, triangle.p2, triangle.p3]):
                return triangle

            # 2. Check if any rectangle vertex is inside triangle
            rect_points = [
                self.pos,
                Vector2(self.pos.x + self.w, self.pos.y),
                Vector2(self.pos.x + self.w, self.pos.y + self.h),
                Vector2(self.pos.x, self.pos.y + self.h)
            ]
            if any(point_in_triangle(p, triangle) for p in rect_points):
                return triangle

        return None

    def check_entity_collisions(self, entity_list):
        """Check collisions but return a list of all colliding entities"""
        others = []
        for entity in entity_list:
            if entity.rect is not self and abs(self.pos.x - entity.pos.x) < 100:
                if self.overlaps(entity.rect):
                    others.append(entity)
        return others

class Triangle():
    """Triangle class for collider triangles (collides with rectangles)"""
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def overlaps(self, rect):
        """Returns True if the triangle overlaps with the rectangle."""
        # rect should have .pos (Vector2), .w, .h attributes
        triangle_points = [self.p1, self.p2, self.p3]
        rect_points = [
            rect.pos,
            Vector2(rect.pos.x + rect.w, rect.pos.y),
            Vector2(rect.pos.x + rect.w, rect.pos.y + rect.h),
            Vector2(rect.pos.x, rect.pos.y + rect.h),
        ]
        # Check if any triangle vertex is inside the rectangle
        for p in triangle_points:
            if (rect.pos.x <= p.x <= rect.pos.x + rect.w) and (rect.pos.y <= p.y <= rect.pos.y + rect.h):
                return True
        # Check if any rectangle corner is inside the triangle
        if any(self.point_in_triangle(rp) for rp in rect_points):
            return True
        # Optional: Check for edge intersection between triangle and rectangle (not implemented here)
        return False

    def point_in_triangle(self, pt):
        """Barycentric technique to determine if pt is inside this triangle."""
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)
        b1 = sign(pt, self.p1, self.p2) < 0.0
        b2 = sign(pt, self.p2, self.p3) < 0.0
        b3 = sign(pt, self.p3, self.p1) < 0.0
        return ((b1 == b2) and (b2 == b3))

    def check_collisions(self, collider_list):
        """Return first collider whose rectangle overlaps this triangle."""
        for collider in collider_list:
            if self.overlaps(collider.rect):
                return collider

    def check_entity_collisions(self, entity_list):
        """Return all entities whose rects overlap this triangle."""
        others = []
        for entity in entity_list:
            if self.overlaps(entity.rect):
                others.append(entity)
        return others


class Entity(GameObject):
    """Entity class for Gameobjects that possess velocity"""
    def __init__(self, vel, rect):
        super(Entity, self).__init__(rect)
        self.vel = vel

class Decal(Vector2):
    def __init__(self, sprite, duration, x, y):
        super(Decal, self).__init__(x, y)
        self.sprite = sprite
        self.duration = duration
        self.start_time = pygame.time.get_ticks()

class Camera(Rectangle):
    def __init__(self, pos, w, h):
        super(Camera, self).__init__(pos, w, h)
    
    def contains(self, other):
        """Checks if camera horizontally contains a rectangle"""
        return ((other.pos.x > self.pos.x and other.pos.x < self.pos.x + c.SCREEN_WIDTH) or 
                (other.pos.x + other.w > self.pos.x and other.pos.x + other.w < self.pos.x + c.SCREEN_WIDTH))

    def to_view_space(self, pos):
        """Returns position relative to camera"""
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y )

    def update(self, player):
        """Update position of camera based on player velocity and position"""
        self.pos.x = player.pos.x - 30 - (player.vel.x * 50)

        if player.pos.y < 20:
            self.pos.y = player.pos.y - 20

class State_Machine():
    """Manages states"""
    def __init__(self, initial_state, owner_object):
        self.state = initial_state
        self.owner_object = owner_object

    def on_event(self, event):
        """Updates current state and runs on_exit and on_enter"""
        new_state = self.state.on_event(event)
        if new_state is not self.state:
            self.state.on_exit(self.owner_object)
            self.state = new_state
            self.state.on_enter(self.owner_object)

    def update(self):
        self.state.update(self.owner_object)

    def get_state(self):
        return self.state.__class__.__name__

class State():
    """State Class"""
    def on_event(self, event):
        """Handles events delegated to this state"""
        pass

    def on_enter(self, owner_object):
        """Performs actions when entering state"""
        pass

    def update(self, owner_object):
        """Performs actions specific to state when active"""
        pass

    def on_exit(self, owner_object):
        """Performs actions when exiting state"""
        pass

class Digit_System():
    """Class for displaying and handling on-screen digits like score"""
    def __init__(self, start_pos, number_of_digits, start_value = 0):
        self.total_value = start_value
        self.start_pos = start_pos
        self.number_of_digits = number_of_digits #Total amount of digits the digit system handles
        self.digit_array = []
        self.update_value(start_value)
        sprites.digits = sprites.digits.convert()
        sprites.digits.set_colorkey((255, 0, 255))

    def update_value(self, new_value):
        """Updates the total value and digit array of the digit system"""
        self.total_value = new_value
        if new_value > 0:
            remaining_digits = self.number_of_digits - self.get_number_of_digits(new_value)
            self.digit_array = [0] * remaining_digits
            for x in str(self.total_value):
                self.digit_array.append(int(x))
        else:
            self.digit_array = [0] * self.number_of_digits
    
    def draw(self, surface):
        """Draw the digit system"""
        for i, x in enumerate(self.digit_array):
            #Digit width = 24
            surface.blit(sprites.digits, (self.start_pos.x + 24 * i, self.start_pos.y), (24 * x, 0, 24, 21))

    def get_number_of_digits(self, value):
        """Gets the number of digits in an integer"""
        if value == 0:
            return 0
        elif value == 1:
            return 1
        else:
            return math.ceil(math.log10(value))

    

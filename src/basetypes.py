import pygame

from src import sprites, config
import math

class GameObject():
    def __init__(self, shape):
        self.shape = shape

    def __getattr__(self, name):
        """Makes lines shorter by not having to type rect.pos when retrieving position"""
        if name == 'pos':
            return self.shape.pos
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Makes lines shorter by not having to type rect.pos when setting position"""
        if name == 'pos':
            self.shape.pos = value
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

    def __sub__(self, other):
        """Overload Addition"""
        return Vector2(self.x - other.x, self.y - other.y)

class Item():
    """Item class for items that can be picked up"""
    def __init__(self, item_type: str, pos: Vector2, ammo = 0):
        self.item_type = item_type
        self.pos = pos
        self.sprite = sprites.ITEM_ROCKET if item_type == 'rocket' else sprites.ITEM_PLASMA
        self.ammo = ammo
        self.picked_up = False

class Texture():
    def __init__(self, path: str, scale: float = 1.0, offset_x: float = 0.0, offset_y: float = 0.0, rotation: float = 0.0):
        self.offset_x = offset_x
        self.offset_y = offset_y

        surface: pygame.Surface = pygame.image.load(path).convert_alpha()
        surface_width = surface.get_width() * scale
        surface_height = surface.get_height() * scale
        scaled_surface = pygame.transform.scale(surface, (surface_width, surface_height))

        self.surface: pygame.Surface = pygame.transform.rotate(scaled_surface, rotation)


class Rectangle():
    """Rectangle class for collider rectangles"""
    def __init__(self, pos = Vector2(), w = 0, h = 0, texture: Texture|None=None):
        self.pos = pos
        self.w = w
        self.h = h
        self.surface = None

        # pre-render surface if there is a texture
        if texture is not None:
            self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            for x in range(-texture.surface.get_width(), self.w, texture.surface.get_width()):
                for y in range(-texture.surface.get_height(), self.h, texture.surface.get_height()):
                    self.surface.blit(texture.surface, (x + texture.offset_x, y + texture.offset_y))


    def overlaps(self, other):
        """Check if two rectangles overlap"""
        return not(other.pos.x + other.w <= self.pos.x or 
                   other.pos.x >= self.pos.x + self.w or
                   other.pos.y + other.h <= self.pos.y or
                   other.pos.y >= self.pos.y + self.h)

    def check_collisions(self, collider_list):
        """Check collisions between two rectangles, if in a rangle of 100px, returns a single collider"""
        for collider in collider_list:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.shape.w >= 100:  # Wider colliders are checked anyway
                if self.overlaps(collider.shape):
                    return collider

    def check_center_collisions(self, collider_list):
        """Check collision of the center of this rect and another rectangle"""
        for collider in collider_list:
            if collider.pos.x <= self.pos.x + self.w // 2 <= collider.pos.x + collider.shape.w and collider.pos.y <= self.pos.y + self.h // 2 <= collider.pos.y + collider.shape.h:
                return collider

    def check_entity_collisions(self, entity_list):
        """Check collisions but return a list of all colliding entities"""
        others = []
        for entity in entity_list:
            if entity.shape is not self and abs(self.pos.x - entity.pos.x) < 100:
                if self.overlaps(entity.shape):
                    others.append(entity)
        return others

    def check_triangle_top_sides_collision(self, collider_list):
        """
        Checks if this rectangle collides with any of the "top sides" of the given triangles.
        The "top sides" are the two sides connected to the highest vertex (lowest y-coordinate).

        Args:
            collider_list: A list of Triangle objects to check against

        Returns:
            A tuple of (Vector2, Vector2) representing the colliding side, or None if no collision
        """

        for collider in collider_list:
            triangle = collider.shape
            # Find the highest vertex (lowest y-coordinate)
            vertices = [triangle.p1, triangle.p2, triangle.p3]
            highest_vertex_idx = 0
            for i in range(1, 3):
                if vertices[i].y < vertices[highest_vertex_idx].y:
                    highest_vertex_idx = i

            # Determine the two sides connected to the highest vertex
            top_sides = []
            if highest_vertex_idx == 0:
                top_sides = [(triangle.p1, triangle.p2), (triangle.p1, triangle.p3)]
            elif highest_vertex_idx == 1:
                top_sides = [(triangle.p2, triangle.p1), (triangle.p2, triangle.p3)]
            else:  # highest_vertex_idx == 2
                top_sides = [(triangle.p3, triangle.p1), (triangle.p3, triangle.p2)]

            # Check if the rectangle intersects with either of these sides
            for side in top_sides:
                if self.line_intersects_rectangle(side[0], side[1]):
                    return side

        return None

    def line_intersects_rectangle(self, p1, p2):
        """
        Checks if a line segment intersects with this rectangle.

        Args:
            p1: Vector2 representing the start point of the line
            p2: Vector2 representing the end point of the line

        Returns:
            True if the line intersects with the rectangle, False otherwise
        """
        # Rectangle edges
        rect_edges = [
            (Vector2(self.pos.x, self.pos.y), Vector2(self.pos.x + self.w, self.pos.y)),  # Top
            (Vector2(self.pos.x + self.w, self.pos.y), Vector2(self.pos.x + self.w, self.pos.y + self.h)),  # Right
            (Vector2(self.pos.x + self.w, self.pos.y + self.h), Vector2(self.pos.x, self.pos.y + self.h)),  # Bottom
            (Vector2(self.pos.x, self.pos.y + self.h), Vector2(self.pos.x, self.pos.y))  # Left
        ]

        # Check if either endpoint is inside the rectangle
        if (self.pos.x <= p1.x <= self.pos.x + self.w and self.pos.y <= p1.y <= self.pos.y + self.h) or \
                (self.pos.x <= p2.x <= self.pos.x + self.w and self.pos.y <= p2.y <= self.pos.y + self.h):
            return True

        # Check if the line intersects with any of the rectangle's edges
        for edge in rect_edges:
            if self.line_segments_intersect(p1, p2, edge[0], edge[1]):
                return True

        return False

    def line_segments_intersect(self, p1, p2, p3, p4):
        """
        Checks if two line segments (p1,p2) and (p3,p4) intersect.

        Args:
            p1, p2: Vector2 points defining the first line segment
            p3, p4: Vector2 points defining the second line segment

        Returns:
            True if the line segments intersect, False otherwise
        """
        # Calculate the direction vectors
        d1x = p2.x - p1.x
        d1y = p2.y - p1.y
        d2x = p4.x - p3.x
        d2y = p4.y - p3.y

        # Calculate the determinant
        det = d1x * d2y - d1y * d2x

        # If determinant is zero, lines are parallel
        if det == 0:
            return False

        # Calculate the parameters for the intersection point
        s = ((p3.x - p1.x) * d2y - (p3.y - p1.y) * d2x) / det
        t = ((p3.x - p1.x) * d1y - (p3.y - p1.y) * d1x) / det

        # Check if the intersection point is within both line segments
        return 0 <= s <= 1 and 0 <= t <= 1

class Triangle():
    """Triangle class for collider triangles (collides with rectangles)"""
    def __init__(self, p1, p2, p3, texture: Texture|None=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.surface = None
        self.surface_pos = None

        # pre-render surface if there is a texture
        if texture is not None:
            tri_points = [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)]

            xs, ys = zip(*tri_points)
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            self.surface_pos = Vector2(minx, miny)
            b_rect = pygame.Rect(minx, miny, maxx - minx, maxy - miny)

            # Create a mask for the triangle
            triangle_mask = pygame.Surface((b_rect.width, b_rect.height), pygame.SRCALPHA)
            shifted_points = [(x - minx, y - miny) for x, y in tri_points]
            pygame.draw.polygon(triangle_mask, (255, 255, 255, 255), shifted_points)

            # Create a pattern surface to cover the triangle (bigger is safer)
            self.surface = pygame.Surface((b_rect.width, b_rect.height), pygame.SRCALPHA)
            for x in range(-texture.surface.get_width(), b_rect.width, texture.surface.get_width()):
                for y in range(-texture.surface.get_height(), b_rect.height, texture.surface.get_height()):
                    self.surface.blit(texture.surface, (x + texture.offset_x, y + texture.offset_y))

            # Use the mask to show only the triangle
            self.surface.blit(triangle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

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
            if self.overlaps(collider.shape):
                return collider

    def check_entity_collisions(self, entity_list):
        """Return all entities whose rects overlap this triangle."""
        others = []
        for entity in entity_list:
            if self.overlaps(entity.shape):
                others.append(entity)
        return others


class Entity(GameObject):
    """Entity class for Gameobjects that possess velocity"""
    def __init__(self, vel, rect):
        super(Entity, self).__init__(rect)
        self.vel = vel

class Decal(Vector2):
    def __init__(self, sprite, duration, x, y, vel_x = 0, target_vel = 0, acc = 0, sound = None):
        super(Decal, self).__init__(x, y)
        self.vel_x = vel_x
        self.target_vel = target_vel
        self.acc = acc
        self.sprite = sprite
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.sound = sound

    def point_in_triangle(self, pt, t):
        def sign(p1, p2, p3):
            return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

        b1 = sign(pt, t.p1, t.p2) < 0.0
        b2 = sign(pt, t.p2, t.p3) < 0.0
        b3 = sign(pt, t.p3, t.p1) < 0.0
        return (b1 == b2) and (b2 == b3)

    def check_collisions(self, collider_list):
        """Check collisions:
           - For Rectangle: usual AABB test
           - For Triangle: uses point_in_triangle function
           If collision is detected, returns the collider.
        """

        for collider in collider_list:
            if isinstance(collider.shape, Rectangle):
                if (collider.shape.pos.x < self.x < collider.shape.pos.x + collider.shape.w and
                        collider.shape.pos.y < self.y < collider.shape.pos.y + collider.shape.h):
                    if self.sound is not None:
                        self.sound.stop()
                    return collider
            elif isinstance(collider.shape, Triangle):
                # Assuming self.x and self.y represent the point to test
                class Pt:  # Minimal point object for compatibility
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                pt = Pt(self.x, self.y)
                if self.point_in_triangle(pt, collider.shape):
                    if self.sound is not None:
                        self.sound.stop()
                    return collider

        return None


class Camera(Rectangle):
    def __init__(self, pos, w, h):
        super(Camera, self).__init__(pos, w, h)
        self.start_pos_y = pos.y

    def contains_rect(self, other):
        """Checks if camera horizontally overlaps with a rectangle (partial or full containment)"""
        # Check if there's any horizontal overlap
        return not (other.pos.x + other.w <= self.pos.x or  # object is completely to the left
                    other.pos.x >= self.pos.x + config.SCREEN_WIDTH)  # object is completely to the right

    def contains_triangle(self, triangle):
        """Checks if camera horizontally overlaps with a triangle (partial or full containment)"""
        # Check if any of the triangle's vertices are horizontally within the camera view
        if (self.pos.x <= triangle.p1.x <= self.pos.x + config.SCREEN_WIDTH or
                self.pos.x <= triangle.p2.x <= self.pos.x + config.SCREEN_WIDTH or
                self.pos.x <= triangle.p3.x <= self.pos.x + config.SCREEN_WIDTH):
            return True

        # Check if the triangle completely contains the camera horizontally
        # This handles cases where all triangle vertices are outside but the triangle still overlaps
        left_x = min(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        right_x = max(triangle.p1.x, triangle.p2.x, triangle.p3.x)

        # If the leftmost point of the triangle is to the left of the camera's left edge
        # AND the rightmost point is to the right of the camera's right edge
        # then the triangle completely contains the camera horizontally
        if left_x <= self.pos.x and right_x >= self.pos.x + config.SCREEN_WIDTH:
            return True

        # Check if any of the triangle's edges intersect with the camera's vertical boundaries
        camera_left = self.pos.x
        camera_right = self.pos.x + config.SCREEN_WIDTH

        # Define the triangle's edges
        edges = [
            (triangle.p1, triangle.p2),
            (triangle.p2, triangle.p3),
            (triangle.p3, triangle.p1)
        ]

        # Check if any edge intersects with the camera's left or right boundary
        for p1, p2 in edges:
            # Skip horizontal edges (they can't intersect with vertical boundaries)
            if p1.x == p2.x:
                continue

            # Check intersection with left boundary
            if (p1.x <= camera_left <= p2.x) or (p2.x <= camera_left <= p1.x):
                return True

            # Check intersection with right boundary
            if (p1.x <= camera_right <= p2.x) or (p2.x <= camera_right <= p1.x):
                return True

        return False

    def contains_point(self, point):
        """Checks if camera horizontally contains a point"""
        # Check if the point's x-coordinate is within the camera's horizontal range
        return self.pos.x <= point.x <= self.pos.x + config.SCREEN_WIDTH

    def set_start_pos_y(self, y):
        self.start_pos_y = y - 100
        self.pos.y = y - 100

    def to_view_space(self, pos):
        """Returns position relative to camera"""
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y )

    def update(self, player):
        """Update position of camera based on player velocity and position"""
        # Update x position as before
        self.pos.x = player.pos.x - 30 - (player.vel.x * 50)

        # Calculate the top edge of the screen in world coordinates
        screen_top = self.pos.y

        # Calculate the position where the player would be too high in the view
        # (e.g., 1/4 of the screen height from the top)
        threshold_y = screen_top + (config.SCREEN_HEIGHT * 0.15)

        # If player is above the threshold, smoothly move the camera up
        if player.pos.y < threshold_y:
            # Calculate how far above the threshold the player is
            diff_y = threshold_y - player.pos.y

            # Move the camera up, but with smooth interpolation
            # The 0.1 factor controls the smoothness - lower is smoother
            self.pos.y -= diff_y * 0.1
        # If the camera is above its original position and the player is falling
        # (or already below the threshold), smoothly move the camera back down
        elif self.pos.y < self.start_pos_y:
            # Calculate how far the camera is from its original position
            diff_y = self.start_pos_y - self.pos.y

            # Move the camera down, but with smooth interpolation
            # The 0.05 factor controls the smoothness - lower is smoother
            self.pos.y += diff_y * 0.005

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

    

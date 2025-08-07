from src.Camera import Camera
from src.SimpleRect import SimpleRect
from src.Texture import Texture
from src.Vector2 import Vector2
import pygame

class Rectangle(SimpleRect):
    """Rectangle class for collider rectangles"""
    def __init__(self, pos = Vector2(), w = 0, h = 0, texture: Texture|None=None):
        super().__init__(pos, w, h)
        self.surface = None

        self.bbox = (self.pos.x, self.pos.y, self.pos.x + self.w, self.pos.y + self.h)

        # pre-render surface if there is a texture
        if texture is not None:
            self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            
            # Store the texture for reference
            self.texture = texture
            
            # New approach to align textures to the top-left corner:
            # 1. Start from top-left (0,0)
            # 2. Apply offset directly from the top-left
            # 3. Apply rotation if needed (around the texture's center)
            # 4. Apply scale
            
            # Get the dimensions of the texture at different stages
            scaled_width = texture.scaled_width
            scaled_height = texture.scaled_height
            
            # Calculate how many tiles we need in each direction
            # We need to account for the scale factor in determining tile coverage
            tiles_x = int(self.w / (scaled_width * 0.9)) + 2  # Add extra tiles to ensure coverage
            tiles_y = int(self.h / (scaled_height * 0.9)) + 2
            
            # Apply offset directly from the top-left corner
            # NO IDEA WHY, BUT WE NEED TO MULTIPLY WITH 2 TO GET THE SAME RESULTS AS IN MAPDESIGNER
            effective_offset_x = texture.offset_x * 2
            effective_offset_y = texture.offset_y * 2
            
            # For each tile position in our grid
            for i in range(-1, tiles_x):
                for j in range(-1, tiles_y):
                    # Calculate base position for this tile starting from top-left (0,0)
                    base_x = i * scaled_width
                    base_y = j * scaled_height
                    
                    # Apply the offset from the top-left corner
                    final_x = base_x + effective_offset_x
                    final_y = base_y + effective_offset_y
                    
                    # If rotation is needed, we need to handle it differently
                    if texture.rotation != 0:
                        # For rotated textures, we need to adjust the position
                        # to account for the size difference due to rotation
                        final_x -= texture.width_diff / 2
                        final_y -= texture.height_diff / 2
                    
                    # Only blit if this tile would be visible in the rectangle
                    # Use the rotated dimensions for visibility check
                    if (final_x < self.w and final_x + texture.rotated_width > 0 and 
                        final_y < self.h and final_y + texture.rotated_height > 0):
                        self.surface.blit(texture.surface, (final_x, final_y))

    def draw(self, target_surface: pygame.Surface, camera: Camera):
        view_pos = camera.to_view_space(self.pos)
        if self.surface is not None:
            target_surface.blit(self.surface, (view_pos.x, view_pos.y))
        else:
            pygame.draw.rect(target_surface, (0, 0, 0, 128), (view_pos.x, view_pos.y, self.w, self.h))


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

    def check_center_collisions(self, collider_list, less_x = 0, less_y = 0):
        """Check collision of the center of this rect and another rectangle"""
        for collider in collider_list:
            if collider.pos.x + less_x <= self.pos.x + self.w // 2 <= collider.pos.x - less_x + collider.shape.w and collider.pos.y + less_y <= self.pos.y + self.h // 2 <= collider.pos.y - less_y + collider.shape.h:
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
                # ignore vertical sides
                if side[0].x == side[1].x:
                    continue
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

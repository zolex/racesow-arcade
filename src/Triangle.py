from src.Texture import Texture
import pygame
import math

from src.Vector2 import Vector2


class Triangle():
    """Triangle class for collider triangles (collides with rectangles)"""
    def __init__(self, p1, p2, p3, texture: Texture|None=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.surface = None
        self.surface_pos = None
        self.type = 'ramp'

        tri_min_x = float("inf")
        tri_max_x = float("-inf")
        tri_min_y = float("inf")
        tri_max_y = float("-inf")
        for point in [p1, p2, p3]:
            if point.x < tri_min_x:
                tri_min_x = point.x
            if point.x > tri_max_x:
                tri_max_x = point.x
            if point.y < tri_min_y:
                tri_min_y = point.y
            if point.y > tri_max_y:
                tri_max_y = point.y
        self.bbox = (tri_min_x, tri_min_y, tri_max_x, tri_max_y)

        # pre-render surface if there is a texture
        if texture is not None:
            # Store the texture for reference
            self.texture = texture
            
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

            # Create a pattern surface to cover the triangle
            self.surface = pygame.Surface((b_rect.width, b_rect.height), pygame.SRCALPHA)
            
            # This approach matches MapDesigner's transformation order:
            # 1. Translate to center
            # 2. Rotate
            # 3. Translate back
            # 4. Apply offset (divided by scale)
            # 5. Apply scale

            # Get the dimensions of the texture at different stages
            scaled_width = texture.scaled_width
            scaled_height = texture.scaled_height
            
            # Calculate how many tiles we need in each direction
            # We need to account for the scale factor in determining tile coverage
            tiles_x = math.ceil(b_rect.width / scaled_width )
            tiles_y = math.ceil(b_rect.height / scaled_height)
            
            # Calculate the effective offset
            # NO IDEA WHY, BUT HERE WE DON'T NEED TO MULTIPLY WITH 2 (AS FOR RECTANGLE) TO GET THE SAME RESULTS AS IN MAPDESIGNER
            effective_offset_x = texture.offset_x
            effective_offset_y = texture.offset_y
            
            # For each tile position in our grid
            for i in range(-1, tiles_x):
                for j in range(-1, tiles_y):
                    # Calculate base position for this tile
                    base_x = i * scaled_width
                    base_y = j * scaled_height
                    
                    # Apply the offset
                    final_x = base_x + effective_offset_x
                    final_y = base_y + effective_offset_y

                    self.surface.blit(texture.surface, (final_x, final_y))

            # Use the mask to show only the triangle
            self.surface.blit(triangle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def draw(self, target_surface: pygame.Surface, camera):
        if self.surface is not None:
            target_surface.blit(self.surface, (self.surface_pos.x - camera.x, self.surface_pos.y - camera.y))
        else:
            pygame.draw.polygon(target_surface, (160, 0, 44, 128), [
                (self.p1.x - camera.x, self.p1.y - camera.y),
                (self.p2.x - camera.x, self.p2.y - camera.y),
                (self.p3.x - camera.x, self.p3.y - camera.y)
            ])

    def overlaps(self, rect):
        """Returns True if the triangle overlaps with the rectangle."""
        # rect should have .pos (Vector2), .w, .h attributes
        triangle_points = [self.p1, self.p2, self.p3]
        rect_points = [
            rect.pos,
            Vector2(rect.x + rect.w, rect.y),
            Vector2(rect.x + rect.w, rect.y + rect.h),
            Vector2(rect.x, rect.y + rect.h),
        ]
        # Check if any triangle vertex is inside the rectangle
        for p in triangle_points:
            if (rect.x <= p.x <= rect.x + rect.w) and (rect.y <= p.y <= rect.y + rect.h):
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
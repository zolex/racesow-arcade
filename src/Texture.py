import pygame
import math

class Texture:
    def __init__(self, path: str, scale: float = 1.0, offset_x: float = 0.0, offset_y: float = 0.0, rotation: float = 0.0):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.scale = scale
        self.rotation = rotation
        self.path = path

        # Load the original surface
        self.original_surface: pygame.Surface = pygame.image.load(path).convert_alpha()
        self.original_width = self.original_surface.get_width()
        self.original_height = self.original_surface.get_height()

        # Store the unrotated scaled surface for reference
        self.scaled_width = self.original_width * scale
        self.scaled_height = self.original_height * scale
        self.scaled_surface = pygame.transform.scale(self.original_surface, (self.scaled_width, self.scaled_height))

        # Create the rotated surface (in the other direction, to match map designer app!)
        self.surface: pygame.Surface = pygame.transform.rotate(self.scaled_surface, -rotation)

        # Calculate the size difference due to rotation (for proper positioning)
        self.rotated_width = self.surface.get_width()
        self.rotated_height = self.surface.get_height()
        self.width_diff = self.rotated_width - self.scaled_width
        self.height_diff = self.rotated_height - self.scaled_height
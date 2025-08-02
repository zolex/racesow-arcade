from src.Rectangle import Rectangle
from src import config
from src.Vector2 import Vector2


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
        self.start_pos_y = y - 80
        self.pos.y = y - 80

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
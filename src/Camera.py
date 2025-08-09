from src import config
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2


class Camera(SimpleRect):
    def __init__(self, pos, w, h):
        super(Camera, self).__init__(pos, w, h)
        self.start_pos_y = pos.y

        self.smoothing_factor = config.CAMERA_SMOOTHING_FACTOR
        self.offset_left = config.CAMERA_OFFSET_LEFT

        self.forward_factor = 0.15 # the faster the player, the closer he will be to the right side of the screen

    def contains_rect(self, other):
        """Checks if camera horizontally overlaps with a rectangle (partial or full containment)"""
        # Check if there's any horizontal overlap
        return not (other.pos.x + other.w <= self.pos.x or  # object is completely to the left
                    other.pos.x >= self.pos.x + self.w)  # object is completely to the right

    def contains_triangle(self, triangle):
        """Checks if camera horizontally overlaps with a triangle (partial or full containment)"""
        # Check if any of the triangle's vertices are horizontally within the camera view
        if (self.pos.x <= triangle.p1.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p2.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p3.x <= self.pos.x + self.w):
            return True

        # Check if the triangle completely contains the camera horizontally
        # This handles cases where all triangle vertices are outside but the triangle still overlaps
        left_x = min(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        right_x = max(triangle.p1.x, triangle.p2.x, triangle.p3.x)

        # If the leftmost point of the triangle is to the left of the camera's left edge
        # AND the rightmost point is to the right of the camera's right edge
        # then the triangle completely contains the camera horizontally
        if left_x <= self.pos.x and right_x >= self.pos.x + self.w:
            return True

        # Check if any of the triangle's edges intersect with the camera's vertical boundaries
        camera_left = self.pos.x
        camera_right = self.pos.x + self.w

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
        return self.pos.x <= point.x <= self.pos.x + self.w

    def set_start_pos_y(self, y):
        # This method is now a no-op as the camera always follows the player
        pass

    def to_view_space(self, pos):
        """Returns position relative to camera"""
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y )

    def update(self, player):
        """Update position of camera based on player velocity and position"""
        # Calculate target x position based on player position and velocity
        target_x = player.pos.x - self.offset_left - config.CAMERA_FOLLOW_X
        # Apply smoothing to horizontal movement
        diff_x = target_x - self.pos.x
        self.pos.x += diff_x * self.forward_factor
        
        # Calculate the player's position relative to the camera view
        player_rel_y = player.pos.y - self.pos.y

        # when falling, lower the bottom threshold to see where we land
        bottom_sub = 0
        if player.distance_to_ground is None or player.distance_to_ground > self.h * 0.35:
            bottom_sub = player.vel.y

        # Define thresholds - player can move freely within these bounds
        top_threshold = self.h * 0.25    # 25% from the top
        bottom_threshold = self.h * (0.6 - bottom_sub)  # 60% from the top

        # Only move camera if player goes beyond thresholds or has no y movement
        if player_rel_y < top_threshold:
            # Player is too high - move camera up
            target_y = player.pos.y - top_threshold
            diff_y = target_y - self.pos.y
            self.pos.y += diff_y * self.smoothing_factor
        elif player_rel_y > bottom_threshold:
            # Player is too low - move camera down
            target_y = player.pos.y - bottom_threshold
            diff_y = target_y - self.pos.y
            self.pos.y += diff_y * self.smoothing_factor

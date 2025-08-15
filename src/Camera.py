import math
from src import config
from src.Settings import Settings
from src.SimpleRect import SimpleRect
from src.Vector2 import Vector2

class Camera(SimpleRect):
    def __init__(self, pos, settings: Settings):
        super(Camera, self).__init__(pos, settings.resolution[0], settings.resolution[1])

        self.settings = settings

        scale = settings.get_scale()
        # Keep offsets scaled if you want UI/world scaling to still apply
        self.offset_left = config.CAMERA_OFFSET_LEFT * scale

        # Time-based smoothing parameters (units: "per second")
        # Higher values = snappier camera (smaller time constant)
        self.smooth_speed_x = 8.0
        self.smooth_speed_y = 6.0
        self.smooth_speed_y_top = 0.01

        # Vertical lookahead: when falling, show more below player
        self.fall_lookahead_time = -220
        self.max_fall_lookahead = 200

        # Keep the follow x base offset
        self.base_follow_x = 40
        self.lookahead_x = 0.15

        self.settling_time = 666
        self.settling = False
        self.settling_elapsed = None
        self.settling_start_y = None
        self.settling_target_y = None

        self.initial_falling_distance = None
        self.is_looking_ahead = False

    def set_start_pos_y(self, y):
        pass

    def to_view_space(self, pos):
        return Vector2(pos.x - self.pos.x, pos.y - self.pos.y)

    # --- New update: time-based smoothing, velocity lookahead ---
    def update(self, player):
        """Update camera. dt is seconds since last frame (e.g. clock.tick(60)/1000.0)."""
        dt = config.delta_time
        if dt <= 0:
            # avoid division by zero / exp(-0) weirdness; assume a small dt
            dt = 1.0 / 60.0

        # ---------- HORIZONTAL ----------
        # Calculate target x based on player position and velocity
        target_x = player.pos.x - self.offset_left - (self.base_follow_x * self.settings.get_scale())
        # Apply smoothing to horizontal movement
        delta_x = (target_x - self.pos.x) * self.lookahead_x
        self.pos.x += delta_x

        # ---------- VERTICAL ----------
        # player's position relative to camera
        player_rel_y = player.pos.y - self.pos.y

        # thresholds (percent of camera height) — keep these as proportions so they're resolution independent
        top_threshold = self.h * 0.15    # e.g. 15% from top
        bottom_threshold_base = self.h * 0.75  # base 60% from top

        alpha_fall = 1.0 - math.exp(-self.smooth_speed_y * dt)

        # when falling, add extra lookahead downward (in pixels)

        if player.vel.y == 0:
            self.initial_falling_distance = None

        fall_lookahead_px = 0.0
        if player.vel.y > 0 and player.distance_to_ground > self.settings.resolution[1] - bottom_threshold_base:

            if self.initial_falling_distance is None or self.initial_falling_distance == float("inf"):
                #print("initial fall distance", player.distance_to_ground)
                self.initial_falling_distance = player.distance_to_ground

            ## quad ease in-out
            if alpha_fall < 0.5:
                eased_alpha = 2 * alpha_fall * alpha_fall
            else:
                eased_alpha = -2 * (alpha_fall - 1) * (alpha_fall - 1) + 1

            ## quad ease in-out based on fall-percentage
            #delta = player.distance_to_ground / self.initial_falling_distance
            #if delta < 0.5:
            #    eased_delta = 2 * delta * delta
            #else:
            #    eased_delta = -2 * (delta - 1) * (delta - 1) + 1
            eased_delta = 1

            fall_lookahead_px = player.vel.y * self.fall_lookahead_time * eased_alpha * eased_delta

            if fall_lookahead_px > self.max_fall_lookahead:
                fall_lookahead_px = self.max_fall_lookahead

        if fall_lookahead_px < 0:
            self.is_looking_ahead = True

        bottom_threshold = bottom_threshold_base + fall_lookahead_px
        if player_rel_y < top_threshold and fall_lookahead_px == 0:
            self.settling = False
            # move up so player reaches top threshold
            target_y = player.pos.y - top_threshold
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y_top * dt)
            self.pos.y += (target_y - self.pos.y) * alpha_y
        elif player_rel_y > bottom_threshold and not self.settling:
            # move down so player reaches bottom threshold
            target_y = player.pos.y - bottom_threshold
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y * dt)
            eased_alpha_y = alpha_y * alpha_y
            self.pos.y += (target_y - self.pos.y) * eased_alpha_y
        elif self.is_looking_ahead:
            # Target Y so player is slightly above bottom threshold (e.g. player's height above it)
            desired_target_y = player.pos.y - bottom_threshold + player.shape.h
            distance = abs(self.pos.y - desired_target_y)

            if player.vel.y == 0 and distance > 23:
                # Start settling if not already started or target changed significantly
                if not self.settling: #abs(self.settling_target_y - desired_target_y) > 100:
                    #print("Settling camera to target Y:", desired_target_y, "dist", distance)
                    self.settling = True
                    self.settling_elapsed = 0.0
                    self.settling_start_y = self.pos.y
                    self.settling_target_y = desired_target_y

            if self.settling and self.settling_target_y is not None and self.settling_elapsed is not None and self.settling_start_y is not None:
                # Accumulate elapsed time in milliseconds
                self.settling_elapsed += dt

                # Clamp elapsed to settling_time max
                t = min(self.settling_elapsed / self.settling_time, 1.0)

                # Smooth interpolation
                # ease_t = t * t * (3 - 2 * t) # cubic in-out
                ease_t = 1 - (1 - t) ** 3 # cubic out

                # Interpolate camera Y between start and target
                self.pos.y = round((1 - ease_t) * self.settling_start_y + ease_t * self.settling_target_y, 2)

                # Stop settling once done
                if t >= 1.0:
                    self.stop_settling()

    def stop_settling(self):
        self.settling = False
        self.settling_elapsed = None
        self.settling_start_y = None
        self.settling_target_y = None
        self.is_looking_ahead = False

        # --- containment helpers kept as-is (you had them already) ---
    def contains_rect(self, other):
        return not (other.pos.x + other.w <= self.pos.x or other.pos.x >= self.pos.x + self.w)

    def contains_triangle(self, triangle):
        if (self.pos.x <= triangle.p1.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p2.x <= self.pos.x + self.w or
                self.pos.x <= triangle.p3.x <= self.pos.x + self.w):
            return True
        left_x = min(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        right_x = max(triangle.p1.x, triangle.p2.x, triangle.p3.x)
        if left_x <= self.pos.x and right_x >= self.pos.x + self.w:
            return True
        camera_left = self.pos.x
        camera_right = self.pos.x + self.w
        edges = [(triangle.p1, triangle.p2), (triangle.p2, triangle.p3), (triangle.p3, triangle.p1)]
        for p1, p2 in edges:
            if p1.x == p2.x:
                continue
            if (p1.x <= camera_left <= p2.x) or (p2.x <= camera_left <= p1.x):
                return True
            if (p1.x <= camera_right <= p2.x) or (p2.x <= camera_right <= p1.x):
                return True
        return False

    def contains_point(self, point):
        return self.pos.x <= point.x <= self.pos.x + self.w
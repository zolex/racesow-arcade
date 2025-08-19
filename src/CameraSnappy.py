import math
from src import config
from src.Camera import Camera
from src.Settings import Settings
from src.Vector2 import Vector2
from src.utils import ease_in_out_cubic


class CameraSnappy(Camera):
    def __init__(self, settings: Settings):
        super(CameraSnappy, self).__init__(settings)

        self.settings = settings

        # Horizontal Cam settings
        self.offset_x = self.calculate_offset()
        self.lookahead_x = 0.15
        self.velocity_offset = 0.0
        self.plasma_velocity_smoothing = 0.00025
        self.base_follow_x = 20 * self.settings.get_scale()


        # Vertical Cam Settings
        self.smooth_speed_y = 6.0
        self.smooth_speed_y_top = 0.01
        self.max_fall_lookahead = -180 * self.settings.get_scale()
        self.top_threshold = self.h * 0.15  # 15% from top
        self.bottom_threshold_base = self.h * 0.66  # 75% from top

    def update(self, player):
        dt = config.delta_time
        scale = self.settings.get_scale()

        # ---------- HORIZONTAL ----------

        # Calculate target x based on player position and velocity
        target_x = player.x - self.offset_x - (self.base_follow_x * scale)
        # Apply smoothing to horizontal movement
        delta_x = (target_x - self.x) * self.lookahead_x
        self.x += delta_x


        # ---------- VERTICAL ----------

        fall_lookahead_px = 0.0
        if player.vel.y > 0 and player.distance_to_ground > self.settings.resolution[1]:
            alpha_fall = 1.0 - math.exp(-1 * dt)
            eased_alpha = ease_in_out_cubic(alpha_fall)
            fall_lookahead_px = player.vel.y * self.max_fall_lookahead * eased_alpha
            if 0 < player.distance_to_ground < fall_lookahead_px:
                fall_lookahead_px -= player.distance_to_ground
            # apply "ease-out" as it goes near zero
            if fall_lookahead_px < self.max_fall_lookahead:
                t = fall_lookahead_px / self.max_fall_lookahead
                t_eased = 1 - pow(1 - t, 3)
                fall_lookahead_px = t_eased * self.max_fall_lookahead

        player_rel_y = player.y - self.y
        bottom_threshold = self.bottom_threshold_base + fall_lookahead_px
        if player_rel_y < self.top_threshold and fall_lookahead_px == 0:
            # move up so the player reaches the top threshold
            target_y = player.y - self.top_threshold
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y_top * dt)
            self.y += (target_y - self.y) * alpha_y
        elif player_rel_y > bottom_threshold:
            # move down so the player reaches the bottom threshold
            target_y = player.y - bottom_threshold
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y * dt)
            eased_alpha_y = alpha_y * alpha_y
            self.y += (target_y - self.y) * eased_alpha_y
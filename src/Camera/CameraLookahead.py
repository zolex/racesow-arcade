import math
from src import config
from src.Camera.Camera import Camera
from src.Settings import Settings
from src.utils import ease_in_out_cubic


class CameraLookahead(Camera):
    def __init__(self, settings: Settings):
        super(CameraLookahead, self).__init__(settings)

        self.settings = settings

        # Horizontal Cam settings
        self.base_offset_x = self.calculate_offset()
        self.offset_x = self.base_offset_x
        self.current_offset_x = 0
        self.transition_start = 0
        self.transition_target = 0
        self.transition_elapsed = 0.0
        self.transition_duration = 3886
        self.lookahead_x = 0.15
        self.velocity_offset = 0.0
        self.plasma_velocity_smoothing = 0.00025
        self.run_smoothing = 0.1
        self.base_follow_x = 20 * self.settings.get_scale()


        # Vertical Cam Settings
        self.smooth_speed_y = 6.0
        self.smooth_speed_y_top = 0.01
        self.fall_lookahead_time = -220
        self.max_fall_lookahead = -180 * self.settings.get_scale()
        self.max_rise_lookahead = 360 * self.settings.get_scale()
        self.settling_time = 666
        self.settling = False
        self.settling_elapsed = None
        self.settling_start_y = None
        self.settling_target_y = None
        self.initial_falling_distance = None
        self.is_looking_ahead_y = False
        self.last_lookahead_dir_y = 0  # -1 = down, +1 = up, 0 = none
        self.top_threshold = self.h * 0.15  # 15% from top
        self.bottom_threshold_base = self.h * 0.66  # 75% from top

    def set_start_pos_y(self, y):
        pass

    def update_x(self, player):
        target_lookahead_offset = 0
        # 1. Determine the instant target for the lookahead offset based on direction.
        if player.direction == 1:  # Player is moving right
            target_lookahead_offset = -self.offset_x
        elif player.direction == -1:  # Player is moving left
            target_lookahead_offset = self.offset_x + player.w - self.w

        # 2. If target changes, reset easing transition
        if target_lookahead_offset != self.transition_target:
            self.transition_start = self.current_offset_x
            self.transition_target = target_lookahead_offset
            self.transition_elapsed = 0.0

        # 3. Progress easing for lookahead offset
        self.transition_elapsed = min(self.transition_elapsed + config.delta_time, self.transition_duration)
        t = self.transition_elapsed / self.transition_duration
        eased_t = ease_in_out_cubic(t)

        if player.current_action_state == 'Plasma':
            velocity_smoothing = self.plasma_velocity_smoothing
        else:
            velocity_smoothing = self.run_smoothing

        # Velocity-based offset
        target_velocity_offset = 36 * self.settings.get_scale() * abs(player.vel.x) * player.direction
        self.velocity_offset = (self.velocity_offset + (target_velocity_offset - self.velocity_offset) * (1 - math.exp(-velocity_smoothing * config.delta_time)))

        # left/right transition
        self.current_offset_x = ((self.transition_start + ( self.transition_target - self.transition_start) * eased_t) - self.velocity_offset)

        # Eased camera toward target_x
        dx = player.x + self.current_offset_x - self.x
        alpha = 1.0 - math.exp(-self.lookahead_x * config.delta_time)  # exponential smoothing
        eased_alpha = ease_in_out_cubic(alpha) # cubic easing
        self.x += dx * eased_alpha


    def update_y(self, player):
        # Compute vertical lookahead both for falling (down) and rising (up)
        fall_lookahead_px = 0.0   # negative values move bottom threshold upward
        rise_lookahead_px = 0.0   # positive values move top threshold downward (i.e., larger margin)

        # Downward lookahead (existing behavior)
        if player.vel.y > 0 and player.distance_to_ground > self.settings.resolution[1] - self.bottom_threshold_base:
            alpha_fall = 1.0 - math.exp(-self.smooth_speed_y * config.delta_time)
            eased_alpha_fall = ease_in_out_cubic(alpha_fall)
            fall_lookahead_px = player.vel.y * self.fall_lookahead_time * eased_alpha_fall
            if fall_lookahead_px < self.max_fall_lookahead:
                # Exceeded the cap: snap faster toward the limit with a stronger ease-out and clamp
                t = min(1.0, fall_lookahead_px / self.max_fall_lookahead)
                t_eased = 1 - pow(1 - t, 4)  # quartic ease-out for faster response
                fall_lookahead_px = t_eased * self.max_fall_lookahead

        # Upward lookahead (amplified vs falling)
        if player.vel.y < 0:
            alpha_rise = 1.0 - math.exp(-self.smooth_speed_y * config.delta_time)
            eased_alpha_rise = ease_in_out_cubic(alpha_rise)
            # Start from symmetric amount and amplify with factor
            rise_lookahead_px = (-player.vel.y) * (-self.fall_lookahead_time) * eased_alpha_rise
            if rise_lookahead_px > self.max_rise_lookahead:
                t = rise_lookahead_px / self.max_rise_lookahead
                t_eased = 1 - pow(1 - t, 3)
                rise_lookahead_px = t_eased * self.max_rise_lookahead

        # Track whether we are currently looking ahead and in which direction
        self.is_looking_ahead_y = fall_lookahead_px < 0 or rise_lookahead_px > 0
        if fall_lookahead_px < 0:
            self.last_lookahead_dir_y = -1
        elif rise_lookahead_px > 0:
            self.last_lookahead_dir_y = 1

        player_rel_y = player.y - self.y

        # Effective thresholds including lookahead offsets
        bottom_threshold = self.bottom_threshold_base + fall_lookahead_px
        top_threshold_eff = self.top_threshold + rise_lookahead_px

        # Move up toward top threshold (disabled while falling lookahead is active to prevent conflicts)
        if player_rel_y < top_threshold_eff and fall_lookahead_px == 0 and not self.settling:
            self.settling = False
            target_y = player.y - top_threshold_eff
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y_top * config.delta_time)
            self.y += (target_y - self.y) * alpha_y
        # Move down toward bottom threshold (disabled while settling)
        elif player_rel_y > bottom_threshold and not self.settling:
            target_y = player.y - bottom_threshold
            alpha_y = 1.0 - math.exp(-self.smooth_speed_y * config.delta_time)
            eased_alpha_y = alpha_y * alpha_y
            self.y += (target_y - self.y) * eased_alpha_y
        # Settling phase after a lookahead
        elif self.is_looking_ahead_y:
            if self.last_lookahead_dir_y == -1:
                # Settling after downward lookahead
                desired_target_y = player.y - bottom_threshold + player.h
            else:
                # Settling after upward lookahead
                desired_target_y = player.y - top_threshold_eff

            if not self.settling and player.vel.y == 0:
                self.settling = True
                self.settling_elapsed = 0.0
                self.settling_start_y = self.y
                self.settling_target_y = desired_target_y
            if self.settling and self.settling_target_y is not None and self.settling_elapsed is not None and self.settling_start_y is not None:
                self.settling_elapsed += config.delta_time
                t = min(self.settling_elapsed / self.settling_time, 1.0)
                ease_t = 1 - (1 - t) ** 3  # cubic out
                self.y = round((1 - ease_t) * self.settling_start_y + ease_t * self.settling_target_y, 2)
                if ease_t >= 1.0:
                    self.stop_settling(player)

    def update(self, player):
        self.update_x(player)
        self.update_y(player)

    def stop_settling(self, player):
        self.settling = False
        self.settling_elapsed = None
        self.settling_start_y = None
        self.settling_target_y = None
        self.is_looking_ahead_y = False

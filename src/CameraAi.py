import pygame
from src.Camera import Camera
from src.Settings import Settings

class CameraAI(Camera):
    def __init__(self, settings: Settings):
        super(CameraAI, self).__init__(settings)
        self.offset_x = self.settings.get_scale() * 60
        self.offset_y = settings.resolution[1] / 2
        self.base_speed_x = 0.05   # min smoothing
        self.max_speed_x = 1     # max smoothing
        self.smooth_speed_y = 0.5
        self.fall_start_time = None
        self.lookahead_offset = 0

        # tuning constants
        self.max_lookahead = None  # set later from self.h
        self.lookahead_growth = 10  # px per update

        # horizontal delay handling
        self.last_direction = None
        self.switch_time = None
        self.direction_delay = 1000  # ms before camera switches side

    def ease_in_out(self, t: float) -> float:
        # cubic easing between 0 and 1
        return t * t * (3 - 2 * t)

    def lerp(self, start, end, t):
        return start + (end - start) * t

    def update(self, player):
        if self.max_lookahead is None:
            self.max_lookahead = self.h * 0.4 - player.shape.h

        current_time = pygame.time.get_ticks()  # ms timestamp

        # --- Track falling state ---
        if player.vel.y > 0:  # falling
            if self.fall_start_time is None:
                self.fall_start_time = current_time
            else:
                fall_duration = current_time - self.fall_start_time
                if fall_duration > 666:
                    if player.distance_to_ground > self.max_lookahead:
                        self.lookahead_offset += self.lookahead_growth
                    else:
                        self.lookahead_offset = self.lerp(
                            self.lookahead_offset, 0, self.smooth_speed_y
                        )
        else:
            self.fall_start_time = None
            self.lookahead_offset = self.lerp(self.lookahead_offset, 0, self.smooth_speed_y)

        self.lookahead_offset = min(self.max_lookahead, self.lookahead_offset)

        # --- Horizontal follow (with delay + easing) ---
        direction_changed = (
            self.last_direction is not None and player.direction != self.last_direction
        )
        if direction_changed:
            self.switch_time = current_time

        allow_switch = True
        if self.switch_time is not None:
            if current_time - self.switch_time < self.direction_delay:
                allow_switch = False
            else:
                allow_switch = True
                self.switch_time = None

        if player.direction == 1:  # facing right
            target_x = player.pos.x + player.shape.w - self.offset_x
        else:  # facing left
            target_x = player.pos.x - self.w + self.offset_x + player.shape.w

        if allow_switch:
            # --- Adaptive smoothing based on velocity ---
            vel_factor = min(0.1, abs(player.vel.x) / 7.5)  # scale with speed
            adaptive_speed_x = self.base_speed_x + (self.max_speed_x - self.base_speed_x) * vel_factor
            eased_speed_x = self.ease_in_out(adaptive_speed_x)

            self.pos.x = self.lerp(self.pos.x, target_x, eased_speed_x)

        self.last_direction = player.direction

        # --- Vertical follow with lookahead (linear) ---
        top_bound = self.pos.y + self.h * 0.25
        bottom_bound = self.pos.y + self.h * 0.75

        target_y = self.pos.y
        player_bottom = player.pos.y + player.shape.h
        player_top = player.pos.y

        if player_top < top_bound:
            target_y = player_top - self.h * 0.25
        elif player_bottom > bottom_bound:
            target_y = player_bottom - self.h * 0.75

        target_y += self.lookahead_offset

        self.pos.y = self.lerp(self.pos.y, target_y, self.smooth_speed_y)

    def stop_settling(self, player):
        # allow instant camera switch when teleporting
        self.fall_start_time = None
        self.lookahead_offset = 0
        self.switch_time = float("-inf")
        self.last_direction = player.direction

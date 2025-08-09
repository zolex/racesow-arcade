from src import config

class Animation:
    """Contains specific animation variables and functions for this class"""

    def __init__(self, player):
        
        self.DEAD_PLAYER = (0 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S)
        self.IDLE = (128 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S)
        self.IDLE_PLASMA = (128 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S)
        self.IDLE_ROCKET = (128 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S)
        self.CROUCH = (0 * player.P_SCALE, 256 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.CROUCH_PLASMA = (0 * player.P_SCALE, 640 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.CROUCH_ROCKET = (0 * player.P_SCALE, 1024 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.SLIDE = (0 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.SLIDE_PLASMA = (256 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.SLIDE_ROCKET = (128 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF)
        self.PLASMA_CLIMB = (640 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S)

        self.RUN = [
            (0 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (0 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.RUN_PLASMA = [
            (0 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (0 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.RUN_ROCKET = [
            (0 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 768 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (0 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (640 * player.P_SCALE, 896 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.WALLJUMP = [
            (256 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.WALLJUMP_PLASMA = [
            (256 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.WALLJUMP_ROCKET = [
            (256 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (384 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (512 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.SHOOT_PLASMA = [
            (640 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]

        self.SHOOT_ROCKET = [
            (0 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (128 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            (256 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
        ]
        
        
        self.player = player
        self.current_sprite = self.IDLE
        self.end_frame = 11
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE

        self.start_height = None
        self.new_y = self.start_height
        self.start_sprite_height = 0

        self.active_run_anim = None
        self.active_walljump_anim = None
        self.active_slide_anim = None
        self.active_crouch_anim = None
        self.active_idle_anim = None

        self.pre_shoot_sprite = None

        self.select_no_weapon()

    def select_no_weapon(self):
        self.active_run_anim = self.RUN
        self.active_walljump_anim = self.WALLJUMP
        self.active_crouch_anim = self.CROUCH
        self.active_slide_anim = self.SLIDE
        self.active_idle_anim = self.IDLE

    def select_plasma(self):
        self.active_run_anim = self.RUN_PLASMA
        self.active_walljump_anim = self.WALLJUMP_PLASMA
        self.active_crouch_anim = self.CROUCH_PLASMA
        self.active_slide_anim = self.SLIDE_PLASMA
        self.active_idle_anim = self.IDLE_PLASMA

    def select_rocket(self):
        self.active_run_anim = self.RUN_ROCKET
        self.active_walljump_anim = self.WALLJUMP_ROCKET
        self.active_crouch_anim = self.CROUCH_ROCKET
        self.active_slide_anim = self.SLIDE_ROCKET
        self.active_idle_anim = self.IDLE_ROCKET

    def set_active_weapon(self):
        if self.player.active_weapon == 'plasma':
            self.select_plasma()
        elif self.player.active_weapon == 'rocket':
            self.select_rocket()
        else:
            self.select_no_weapon()

    def reset_anim(self):
        """Reset animation variables"""
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE

    def animate(self):
        if self.player.current_action_state == 'Idle_State':
            self.idle_anim()
        elif self.player.current_action_state == 'Move_State':
            self.run_anim()
        elif self.player.current_action_state == 'Decel_State':
            self.run_anim()
        elif self.player.current_action_state == 'Jump_State':
            self.jump_anim()
        elif self.player.current_action_state == 'Fall_State':
            self.jump_anim()
        elif self.player.current_action_state == 'Walljump_State':
            self.walljump_anim()
        elif self.player.current_action_state == 'Crouch_State':
            self.crouch_anim()
        elif self.player.current_action_state == 'Rocket_State':
            self.rocket_anim()
        elif self.player.current_action_state == 'Plasma_State':
            self.plasma_anim()


    def idle_anim(self):
        self.current_sprite = self.active_idle_anim

    def crouch_anim(self):
        if self.player.pressed_right and self.player.vel.x > 0:
            self.current_sprite = self.active_slide_anim
        else:
            self.current_sprite = self.active_crouch_anim

    def run_anim(self):
        frame_time = 50 / max(0.7, self.player.vel.x * 2.5)
        self.current_sprite = self.active_run_anim[self.anim_frame]
        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.anim_frame > len(self.active_run_anim) - 1:
                self.anim_frame = 0

    def begin_jump(self):
        current_frame = self.anim_frame
        self.end_frame = 5 if current_frame < 5 or current_frame == 11 else 11

    def jump_anim(self):
        if self.player.active_weapon == 'rocket' and self.player.pressed_down :
            self.current_sprite = self.SHOOT_ROCKET[2]
            return


        frame_time = 50
        self.anim_timer += config.delta_time
        self.current_sprite = self.active_run_anim[self.anim_frame]
        if self.anim_timer > frame_time and self.anim_frame != self.end_frame:
            self.anim_timer = 0
            if self.anim_frame == len(self.active_run_anim) - 1:
                self.anim_frame = 0
            else:
                self.anim_frame += 1

    def walljump_anim(self):
        frame_time = 50
        if self.anim_frame > len(self.active_walljump_anim) - 1:
            self.anim_frame = 0
        self.current_sprite = self.active_walljump_anim[self.anim_frame]
        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += 1

    def rocket_anim(self):
        frame_time = 50
        if self.anim_frame > len(self.SHOOT_ROCKET) - 1:
            return
        self.current_sprite = self.SHOOT_ROCKET[self.anim_frame]
        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += 1

    def plasma_anim(self):
        self.current_sprite = self.SHOOT_PLASMA[0]

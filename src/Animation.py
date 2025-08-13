import os, pygame

from PIL.ImImagePlugin import FRAMES
from pygame.examples.headless_no_windows_needed import scaleit

from src import config

class Animation:
    """Contains specific animation variables and functions for this class"""

    def __init__(self, player):

        SPRITES = {
            'DEAD_PLAYER': (640 * player.P_SCALE, 1280 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            'IDLE': (128 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            'IDLE_PLASMA': (128 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            'IDLE_ROCKET': (128 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            'CROUCH': (0 * player.P_SCALE, 256 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'CROUCH_PLASMA': (0 * player.P_SCALE, 640 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'CROUCH_ROCKET': (0 * player.P_SCALE, 1024 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'SLIDE': (0 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'SLIDE_PLASMA': (256 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'SLIDE_ROCKET': (128 * player.P_SCALE, 1280 * player.P_SCALE + player.CROUCH_OFF, player.P_WIDTH_S, player.P_HEIGHT_S - player.CROUCH_OFF),
            'PLASMA_CLIMB': (640 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            'RUN': [
                (0 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (128 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (256 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (640 * player.P_SCALE, 0 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (0 * player.P_SCALE,   128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (128 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (256 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (640 * player.P_SCALE, 128 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'RUN_PLASMA': [
                (0 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (128 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (256 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (640 * player.P_SCALE, 384 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (0 * player.P_SCALE,   512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (128 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (256 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (640 * player.P_SCALE, 512 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'RUN_ROCKET': [
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
            ],
            'WALLJUMP': [
                (256 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 256 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'WALLJUMP_PLASMA': [
                (256 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'WALLJUMP_ROCKET': [
                (256 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (384 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (512 * player.P_SCALE, 1024 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'SHOOT_PLASMA': [
                (640 * player.P_SCALE, 640 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
            'SHOOT_ROCKET': [
                (0 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (128 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
                (256 * player.P_SCALE, 1152 * player.P_SCALE, player.P_WIDTH_S, player.P_HEIGHT_S),
            ],
        }


        sprite_sheet = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'player.png'))
        new_size = (sprite_sheet.get_width() * player.P_SCALE, sprite_sheet.get_height() * player.P_SCALE)
        self.sprite_sheet = pygame.transform.smoothscale(sprite_sheet, new_size).convert_alpha()

        game_scale = player.game.settings.get_scale()
        self.frames = {}
        for anim, frames in SPRITES.items():
            if isinstance(frames, tuple):
                new_frame = self.sprite_sheet.subsurface(frames).copy()
                self.frames[anim] = pygame.transform.scale(new_frame, (new_frame.get_width() * game_scale, new_frame.get_height() * game_scale))
            elif isinstance(frames, list):
                self.frames[anim] = []
                for frame in frames:
                    new_frame = self.sprite_sheet.subsurface(frame).copy()
                    scaled_frame = pygame.transform.scale(new_frame, (new_frame.get_width() * game_scale, new_frame.get_height() * game_scale))
                    self.frames[anim].append(scaled_frame)

        self.player = player
        self.end_frame = 11
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE
        self.active_run_anim = None
        self.active_walljump_anim = None
        self.active_slide_anim = None
        self.active_crouch_anim = None
        self.active_idle_anim = None
        self.select_no_weapon()
        self.current_sprite = self.get_idle_anim()

    def get_run_anim(self):
        return self.frames[self.active_run_anim]

    def get_walljump_anim(self):
        return self.frames[self.active_walljump_anim]

    def get_slide_anim(self):
        return self.frames[self.active_slide_anim]

    def get_crouch_anim(self):
        return self.frames[self.active_crouch_anim]

    def get_idle_anim(self):
        return self.frames[self.active_idle_anim]

    def select_no_weapon(self):
        self.active_run_anim = 'RUN'
        self.active_walljump_anim = 'WALLJUMP'
        self.active_crouch_anim = 'CROUCH'
        self.active_slide_anim = 'SLIDE'
        self.active_idle_anim = 'IDLE'

    def select_plasma(self):
        self.active_run_anim = 'RUN_PLASMA'
        self.active_walljump_anim = 'WALLJUMP_PLASMA'
        self.active_crouch_anim = 'CROUCH_PLASMA'
        self.active_slide_anim = 'SLIDE_PLASMA'
        self.active_idle_anim = 'IDLE_PLASMA'

    def select_rocket(self):
        self.active_run_anim = 'RUN_ROCKET'
        self.active_walljump_anim = 'WALLJUMP_ROCKET'
        self.active_crouch_anim = 'CROUCH_ROCKET'
        self.active_slide_anim = 'SLIDE_ROCKET'
        self.active_idle_anim = 'IDLE_ROCKET'

    def set_active_weapon(self):
        if self.player.active_weapon == 'plasma':
            self.select_plasma()
        elif self.player.active_weapon == 'rocket':
            self.select_rocket()
        else:
            self.select_no_weapon()

    def reset_anim(self):
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE

    def animate(self):
        if self.player.current_action_state == 'Dead_State':
            self.current_sprite = self.frames['DEAD_PLAYER']
        elif self.player.current_action_state == 'Idle_State':
            self.idle_anim()
        elif self.player.current_action_state == 'Move_State':
            self.run_anim()
        elif self.player.current_action_state == 'Decel_State':
            self.run_anim()
        elif self.player.current_action_state == 'Jump_State':
            self.jump_anim()
        elif self.player.current_action_state == 'Fall_State':
            self.fall_anim()
        elif self.player.current_action_state == 'Walljump_State':
            self.walljump_anim()
        elif self.player.current_action_state == 'Crouch_State':
            self.crouch_anim()
        elif self.player.current_action_state == 'Plasma_State':
            self.plasma_anim()


    def idle_anim(self):
        self.current_sprite = self.get_idle_anim()

    def crouch_anim(self):
        #print(self.player.distance_to_ground)
        if self.player.pressed_right and self.player.ground_touch_pos is not None:
            self.current_sprite = self.get_slide_anim()
        else:
            self.current_sprite = self.get_crouch_anim()

    def run_anim(self):
        if (self.player.
                pressed_down):
            self.crouch_anim()
        else:
            anim = self.get_run_anim()
            frame_time = 50 / max(0.7, self.player.vel.x * 2.5 / self.player.game.settings.get_scale())
            self.current_sprite = anim[self.anim_frame]
            self.anim_timer += config.delta_time
            if self.anim_timer > frame_time:
                self.anim_timer = 0
                self.anim_frame += 1
                if self.anim_frame > len(anim) - 1:
                    self.anim_frame = 0

    def begin_jump(self):
        current_frame = self.anim_frame
        self.end_frame = 5 if current_frame < 5 or current_frame == 11 else 11

    def fall_anim(self):
        if self.player.pressed_down:
            if self.player.active_weapon == 'rocket':
                self.rocket_anim()
            else:
                self.crouch_anim()
        else:
            self.jump_anim()

    def jump_anim(self):
        if self.player.active_weapon == 'rocket' and self.player.pressed_down :
            self.rocket_anim()
        else:
            anim = self.get_run_anim()
            frame_time = 50
            self.anim_timer += config.delta_time
            self.current_sprite = anim[self.anim_frame]
            if self.anim_timer > frame_time and self.anim_frame != self.end_frame:
                self.anim_timer = 0
                if self.anim_frame == len(anim) - 1:
                    self.anim_frame = 0
                else:
                    self.anim_frame += 1

    def walljump_anim(self):
        anim = self.get_walljump_anim()
        frame_time = 50
        self.current_sprite = anim[self.anim_frame]
        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.anim_frame > len(anim) - 1:
                self.anim_frame = 0

    def rocket_anim(self):
        self.current_sprite = self.frames['SHOOT_ROCKET'][2]

    def plasma_anim(self):
        self.current_sprite = self.frames['SHOOT_PLASMA'][0]

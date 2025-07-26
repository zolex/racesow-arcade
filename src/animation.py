from src import config, sprites

class Animation():
    """Contains specific animation variables and functions for this class"""

    def __init__(self, player):
        self.player = player
        self.current_sprite = sprites.PLAYER_IDLE
        self.end_frame = 11
        self.player_size = 'Default_Player'
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE

        self.start_height = None
        self.new_y = self.start_height

        self.grow_frames = [0, 1, 0, 1, 2, 0, 1, 2]
        self.shrink_frames = [0, 1, 0, 1, 2, 1, 2, 1]
        self.run_frames = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.start_sprite_height = 0

    def reset_anim_vars(self):
        """Reset animation variables"""
        self.anim_frame = 0
        self.anim_timer = config.INITIAL_TIMER_VALUE

    def run_anim(self):
        """Animation when running"""
        frame_time = 50 / max(1, self.player.vel.x * 2)
        self.current_sprite = sprites.PLAYER_RUN[self.run_frames[self.anim_frame]]
        self.anim_timer += config.delta_time
        if self.anim_timer > frame_time:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.anim_frame > len(self.run_frames) - 1:
                self.anim_frame = 0

    def jump_anim(self):
        """Animation when jumping"""
        frame_time = 50
        self.anim_timer += config.delta_time
        self.current_sprite = sprites.PLAYER_RUN[self.run_frames[self.anim_frame]]
        if self.anim_timer > frame_time and self.anim_frame != self.end_frame:
            self.anim_timer = 0
            self.anim_frame += 1
            if self.anim_frame > len(self.run_frames) - 1:
                self.anim_frame = 0
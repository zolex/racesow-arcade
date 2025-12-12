import pygame

from src.Player.State.State import State

class RocketJump(State):

    def __init__(self):
        self.entered_time = 0

    def can_transition(self, event):
        return event in [
            'Fall',
            'WallJump',
            'Plasma',
            'Dead'
            'Move'
            'Decel'
        ]

    def can_exit(self, player):
        return player.distance_to_ground > 2

    def on_enter(self, player, old_state):
        self.entered_time = pygame.time.get_ticks()
        player.anim.play('aim_down', player.visible_direction)
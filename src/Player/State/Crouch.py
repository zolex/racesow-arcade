import pygame
from src.Player.State.State import State

class Crouch(State):
    """State when player is crouching"""

    def can_transition(self, event):
        return event in [
            'Jump',
            'Decel',
            'Fall',
            'RocketJump',
            'Launch',
            'Slide',
            'Move',
            'Idle',
            'Plasma',
            'Dead'
        ]

    def can_enter(self, player):
        return player.distance_to_ground <= 2

    def on_enter(self, player, old_state):
        player.anim.play('crouch', player.visible_direction)
        player.crouching = True
        player.acceleration = 0

    def update(self, player):
        if (player.visible_direction == 1 and player.pressed_right) or (player.visible_direction == -1 and player.pressed_left):
            player.state.transition('Slide')

        if 0 < player.vel.x < 0.25:
            player.vel.x = max(0, player.vel.x - 0.005)
        elif 0 > player.vel.x > -0.25:
            player.vel.x = min(0, player.vel.x + 0.005)

    def on_exit(self, player):
        player.crouching = False

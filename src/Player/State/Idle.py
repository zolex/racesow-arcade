import pygame
from src.Player.State.State import State


class Idle(State):
    """State when on the ground and not moving"""

    def can_transition(self, event):
        return event in [
            'Jump',
            'Move',
            'Decel',
            'Crouch',
            'Plasma',
            'Dead'
        ]

    def can_enter(self, player):
        return not player.pressed_right and not player.pressed_left and not player.pressed_down

    def on_enter(self, player, old_state):
        player.anim.play('idle', player.visible_direction)
        return

    def update(self, player):
        if player.pressed_down:
            player.state.transition('crouch')

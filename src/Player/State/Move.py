import pygame

from src import config
from src.Player.State.State import State

class Move(State):
    """State when moving on the ground and not breaking or decelerating"""

    def can_transition(self, event):
        return event in [
            #'idle',
            'Decel',
            'Fall',
            'Jump',
            'Launch',
            'Crouch',
            'Slide',
            'Plasma',
            'Dead'
        ]

    def can_enter(self, player):
        if player.current_action_state == 'Plasma' and player.can_plasma_climb:
            return False
        if player.pressed_down:
            return False
        return True

    def on_enter(self, player, old_state):
        player.anim.play('run', player.visible_direction)
        return

    def update(self, player):
        player.acceleration = config.PLAYER_ACCELERATION * player.visible_direction
        if player.pressed_down:
            if (player.direction == 1 and player.pressed_right) or (player.direction == -1 and player.pressed_left):
                player.state.transition('Slide')
            else:
                player.state.transition('Crouch')

import pygame
from src.Player.State.State import State

class Decel(State):
    """State when moving when there is no longer any input"""

    def can_transition(self, event):
        return event in [
            'Idle',
            'Move',
            'Launch',
            'Fall',
            'Jump',
            'Crouch',
            'Slide',
            'Plasma',
            'Dead'
        ]

    def can_enter(self, player):
        return player.distance_to_ground <= 2 and player.current_action_state != 'Crouch'

    def on_enter(self, player, old_state):
        if not player.pressed_down:
            player.anim.play('run', player.visible_direction)
        player.acceleration = 0

    def update(self, player):
        if player.pressed_down:
            if (player.direction == 1 and player.pressed_right) or (player.direction == -1 and player.pressed_left):
                player.state.transition('Slide')
            else:
                player.state.transition('Crouch')

import pygame

from src.Player.State.State import State

class Plasma(State):
    def __init__(self):
        self.previous_anim = None
        self.previous_frame = None

    def can_transition(self, event):
        return event in [
            'Fall',
            'WallJump',
            'Move',
            'Idle',
            'Decel',
            'Dead'
        ]

    def on_enter(self, player, old_state):
        player.last_ramp_radians = 0
        player.anim.play('plasma_climb', player.visible_direction)

    def update(self, player):
        player.can_plasma_climb = player.plasma_climb_collisions()
        if not player.can_plasma_climb or not player.pressed_shoot or (not player.pressed_down and not player.pressed_up and not player.pressed_right and not player.pressed_left):
            player.state.transition('Fall')

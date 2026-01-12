import pygame

from src import config
from src.Player.State.State import State

class Launch(State):
    def __init__(self):
        self.launch_time = 0

    def can_transition(self, event):
        return event in [
            'Idle',
            'Decel',
            'Move',
            'WallJump',
            'Ramp',
            'Fall',
            'Plasma',
            'Dead'
        ]

    def on_enter(self, player, old_state):
        player.last_ramp_radians = 0
        self.launch_time = 0
        print("launch from", old_state)
        if old_state != 'Move':
            player.anim.play('run', player.visible_direction)
        player.anim.pause()

    def update(self, player):
        player.acceleration = 0
        self.launch_time += config.delta_time
        if self.launch_time > 100:
            player.state.transition('Fall')

import pygame

from src.Player.State.State import State

class Fall(State):
    """State when in mid air but spacebar input does not affect velocity"""

    def can_transition(self, event):
        return event in [
            'Idle',
            'Decel',
            'Move',
            'Crouch',
            'WallJump',
            'Launch',
            'Ramp',
            'Plasma',
            'Dead',
            'Slide'
        ]

    def on_enter(self, player, old_state):
        player.ground_collider = None
        if old_state == 'Crouch' or old_state == 'Slide':
            player.anim.play('run', player.visible_direction)
        elif old_state == 'Plasma':
            player.anim.play('idle', player.visible_direction)

        player.anim.pause()

    def update(self, player):
        player.acceleration = 0

        if player.pressed_down:
            player.anim.play('aim_down', player.visible_direction)
            player.state.transition('Crouch') # just try
        elif player.anim.current_animation == 'aim_down':
            #player.anim.previous(player.visible_direction)
            if abs(player.vel.x) > 0.5:
                player.anim.play('run', stopped=True)
            else:
                player.anim.play('idle')

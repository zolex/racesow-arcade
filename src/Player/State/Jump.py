import random
from src.Item.Decal import Decal
from src.Player.State.State import State

class Jump(State):
    """State when jumping when spacebar input affects velocity"""

    def can_transition(self, event):
        return event in [
            'Fall',
            'WallJump',
            'RocketJump',
            'Plasma',
            'Ramp',
            'Dead',
            'Decel',
        ]

    def on_enter(self, player, old_state):
        player.anim.play('jump', player.visible_direction)
        player.ground_collider = None
        player.last_walljump = 0
        player.sounds.play_step()
        player.sounds.play_jump()

        dash = f'dash{random.choice([1, 2])}'
        if player.direction == -1:
            dash = f'{dash}_left'

        player.game.map.decals.append(Decal(dash, 666, player.x, player.y + player.h, bottom=True, fade_out=True))
        player.add_jump_velocity()

    def update(self, player):
        if player.pressed_down:
            player.anim.play('aim_down', player.visible_direction)
        elif player.anim.current_animation == 'aim_down':
            #player.anim.previous(player.visible_direction)
            #player.anim.play('run', stopped=True)
            if abs(player.vel.x) > 0.5:
                player.anim.play('run', stopped=True)
            else:
                player.anim.play('idle')

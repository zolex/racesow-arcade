import pygame
from src import config
from src.Player.State.State import State

class Slide(State):

    def can_transition(self, event):
        return event in [
            'Decel',
            'Fall',
            'Launch',
            'Move',
            'Jump',
            'Dead',
            'Crouch',
            'RocketJump'
        ]

    def can_enter(self, player):
        return player.distance_to_ground <= 2

    def on_enter(self, player, old_state):
        player.acceleration = 0
        player.sounds.slide.play(loops=-1, fade_ms=333)
        player.anim.play('slide', player.visible_direction)
        player.crouching = True
        if abs(player.vel.x) < 0.001:
            print("slide impulse")
            player.vel.x = config.PLAYER_SLIDE_IMPULSE * player.visible_direction * player.game.settings.get_scale()

    def update(self, player):
        player.sounds.slide.set_volume(0.1 * player.vel.x)
        if not player.pressed_right and not player.pressed_left:
            player.state.transition('Crouch')

        if 0 < player.vel.x < 0.25:
            player.vel.x = max(0, player.vel.x - 0.005)
        elif 0 > player.vel.x > -0.25:
            player.vel.x = min(0, player.vel.x + 0.005)

    def on_exit(self, player):
        player.sounds.slide.fadeout(100)
        player.crouching = False

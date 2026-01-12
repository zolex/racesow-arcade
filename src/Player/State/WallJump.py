import pygame
import random

from src.Player.State.State import State
from src import config


class WallJump(State):
    def __init__(self):
        self.animation_finished = False

    def can_transition(self, event):
        return event in [
            'Fall',
            'Plasma',
            'Dead'
        ]

    def on_animation_finished(self):
        self.animation_finished = True

    def can_enter(self, player):
        return pygame.time.get_ticks() - player.last_walljump > 1000 and player.walljump_collisions()

    def on_enter(self, player, old_state):
        if random.choice([True, False]):
            player.sounds.walljump1.play()
        else:
            player.sounds.walljump2.play()

        player.anim.play('wall_jump', player.direction, callback=self.on_animation_finished, reset=True)
        boost = config.WALLJUMP_VELOCITY * player.game.settings.get_scale()
        player.vel.y = min(-boost, player.vel.y - boost)

        player.last_walljump = pygame.time.get_ticks()

    def can_exit(self, player):
        return self.animation_finished

    def on_exit(self, player):
        player.anim.play('jump', player.visible_direction, reset=False, start_frame=-1)

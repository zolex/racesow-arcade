import pygame
from src.Player.State.State import State
from src import config


class Dead(State):
    """State when player is dead"""
    def __init__(self):
        self.death_timer = 0

    def on_enter(self, player, old_state):
        player.freeze_input = True
        player.sounds.death.play()
        player.anim.play('dead', player.visible_direction)

    def update(self, player):
        self.death_timer += config.delta_time
        player.vel.x = 0
        player.vel.y = 0.1
        if self.death_timer > 300 * config.delta_time:
            self.death_timer = float("-inf")
            player.game.map.reset()
            player.reset()
            player.state.transition('Idle')

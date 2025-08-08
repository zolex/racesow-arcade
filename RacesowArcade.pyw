import pygame, os
from src.Game import Game
from src import config

if __name__ == '__main__':
    display_options = pygame.SCALED
    if os.getenv("WINDOWED"):
        display_options += pygame.FULLSCREEN
    
    pygame.init()    
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), display_options)
    config.clock = pygame.time.Clock()

    Game(screen).game_loop()
    
    pygame.quit()

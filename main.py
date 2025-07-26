from src import game, config
import pygame, os

if __name__ == '__main__':
    display_options = pygame.SCALED
    if os.getenv("WINDOWED"):
        display_options += pygame.FULLSCREEN
    
    pygame.init()    
    config.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), display_options)
    config.surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    config.clock = pygame.time.Clock()

    game.Game().game_loop()
    
    pygame.quit()

import pygame, os
from time import sleep
from src.MainMenu import MainMenu
from src.Settings import Settings
from src.config import assets_folder

if __name__ == '__main__':

    settings = Settings()
    settings.load()

    is_fullscreen = False
    display_options = pygame.SCALED
    if os.getenv("WINDOWED") or settings.fullscreen:
        display_options += pygame.FULLSCREEN
        is_fullscreen = True
    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(64)
    pygame.display.set_caption("Racesow Arcade")
    pygame.mouse.set_visible(False)

    screen = pygame.display.set_mode((settings.width, settings.height), display_options)
    clock = pygame.time.Clock()

    MainMenu(screen, clock, settings).game_loop()

    settings.save()

    back = pygame.mixer.Sound(os.path.join(assets_folder, 'sounds', 'menu', 'back.wav'))
    back.play()
    sleep(0.75)

    pygame.mixer.quit()
    pygame.quit()

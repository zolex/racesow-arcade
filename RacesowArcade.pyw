import pygame, os
from time import sleep
from src.MainMenu import MainMenu
from src.Settings import Settings
from src.config import assets_folder

from profilehooks import profile

@profile
def main():
    settings = Settings()
    settings.load()

    display_options = pygame.SCALED
    if os.getenv("WINDOWED") or settings.fullscreen:
        display_options += pygame.FULLSCREEN

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(64)
    pygame.display.set_caption("Racesow Arcade")
    pygame.mouse.set_visible(True)

    screen = pygame.display.set_mode((settings.width, settings.height), display_options)
    clock = pygame.time.Clock()

    scene = MainMenu(screen, clock, settings)
    while scene is not None:
        scene.init_input_mappings()
        scene = scene.game_loop()

    settings.save()

    back = pygame.mixer.Sound(os.path.join(assets_folder, 'sounds', 'menu', 'back.wav'))
    back.play()
    sleep(0.75)

    pygame.mixer.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
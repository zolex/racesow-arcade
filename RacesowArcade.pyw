import argparse, pygame, os
from time import sleep
from src.MainMenu import MainMenu
from src.Settings import Settings
from src.config import assets_folder

#from profilehooks import profile
#@profile
def main(args):
    settings = Settings()
    settings.load()
    for key, value in vars(args).items():
        if value is not None:
            settings.set(key, value)

    display_options = pygame.SCALED
    if args.fullscreen is not None:
        if args.fullscreen:
            display_options += pygame.FULLSCREEN
    elif settings.fullscreen:
        display_options += pygame.FULLSCREEN

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(64)
    pygame.display.set_caption("Racesow Arcade")
    pygame.mouse.set_visible(settings.cursor is None)

    screen = pygame.display.set_mode((settings.resolution[0], settings.resolution[1]), display_options)
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

def parse_resolution(s):
    return [int(x) for x in s.split('x')]

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'y', 'on', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'n', 'off', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def volume_type(v):
    v = int(v)
    if 1 <= v <= 10:
        return v
    raise argparse.ArgumentTypeError("Volume must be between 1 and 10.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Racesow Arcade")
    parser.add_argument('--fullscreen', nargs='?', const=True, default=None, type=str2bool, help='Enable or disable fullscreen mode')
    parser.add_argument("--resolution", type=parse_resolution, help=f"Resolution in the format 'WxH'")
    parser.add_argument('--max-fps', type=int, default=None, help='Set max fps')
    parser.add_argument('--volume', type=volume_type, default=None, help='Set game volume (1-10)')
    parser.add_argument('--music-enabled', type=str2bool, default=None, help='Enable or disable music')
    parser.add_argument('--music-volume', type=volume_type, default=None, help='Set music volume (1-10)')


    main(parser.parse_args())
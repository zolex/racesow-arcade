import copy, os, pygame

from src.CameraAi import CameraAI
from src.CameraFixed import CameraFixed
from src.CameraLookahead import CameraLookahead
from src.CameraSnappy import CameraSnappy
from src.Input import Input
from src.Scene import GameScene
from src.Map import Map
from src.Player import Player
from src import config
from src.Settings import Settings
from src.HUD import HUD

from src.Decal import pre_load_decals
from src.Item import pre_load_items
from src.Projectile import pre_load_projectiles

def create_camera(settings: Settings):
    if settings.camera_style == 'fixed':
        return CameraFixed(settings)

    if settings.camera_style == 'snappy':
        return CameraSnappy(settings)

    if settings.camera_style == 'lookahead':
        return CameraLookahead(settings)

    if settings.camera_style == 'ai':
        return CameraAI(settings)

    raise Exception(f'Invalid camera style: {settings.camera_style}')

class Game(GameScene):
    """Contains main loop and handles the game"""
    def __init__(self, map: str, surface: pygame.Surface, clock: pygame.time.Clock, settings: Settings = None):
        super().__init__(surface, clock, settings)

        game_scale = settings.get_scale()
        pre_load_decals(game_scale)
        pre_load_items(game_scale)
        pre_load_projectiles(game_scale)

        self.camera = create_camera(settings)
        self.hud = HUD(self)
        self.map = Map(self)
        self.player = Player(self)
        self.map.load(map)
        self.player.set_map(self.map)
        self.last_velocity = 0
        self.start_time = pygame.time.get_ticks()
        self.input_mappings = None
        self.show_options = False

    def draw(self):
        self.map.draw()
        self.player.draw()
        self.map.draw_front()
        self.hud.draw()

    def update_settings(self):
        self.camera = create_camera(self.settings)
        pass

    def update(self):
        # let it "load" a few milliseconds to avoid missing out collision checks
        # causing the player to fall out of the map at higher screen resolutions
        if self.start_time + 333 > pygame.time.get_ticks():
            return

        self.hud.update()
        self.player.update()
        self.camera.update(self.player)
        self.map.update(self.player)

    def set_quit_really(self):
        self.set_quit()
        if self.next_scene is not None:
            self.next_scene.set_quit()

    def show_settings(self, key_down):
        if not key_down:
            return

        menu = copy.copy(self.next_scene)
        menu.set_next_scene(self)
        menu.game_loop(entrypoint=['SETTINGS'], force_quit=True)

    def init_input_mappings(self):
        self.input_mappings = {
            Input.LEFT: lambda v, e: self.player.input_left(v),
            Input.RIGHT: lambda v, e: self.player.input_right(v),
            Input.UP: lambda v, e: self.player.input_up(v),
            Input.DOWN: lambda v, e: self.player.input_down(v),
            Input.JUMP: lambda v, e: self.player.input_jump(v),
            Input.WALL_JUMP: lambda v, e: self.player.input_wall_jump(v),
            Input.SHOOT: lambda v, e: setattr(self.player, "pressed_shoot", v),
            Input.SWITCH_WEAPON: lambda v, e: self.player.input_switch_weapon(v),
            Input.BACK: lambda v, e: self.set_quit(v),
            Input.MENU: lambda v, e: self.show_settings(v),
        }

    def game_loop(self):
        while True:
            config.delta_time = self.clock.tick(self.settings.max_fps)
            if self.hud.ready:
                self.handle_events(self.input_mappings, lambda: self.set_quit_really())

            self.update()
            self.draw()
            pygame.display.update()

            if self.quit:
                back = pygame.mixer.Sound(os.path.join(config.assets_folder, 'sounds', 'menu', 'back.wav'))
                back.play()
                next_scene = copy.copy(self.next_scene)
                self.next_scene = None
                return next_scene



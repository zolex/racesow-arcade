import random

import pygame, math
from src import level, sounds, sprites, config, player
from src.basetypes import Camera, Vector2, Rectangle, Digit_System, Decal


class Game():
    """Contains main loop and handles the game"""
    def __init__(self, surface):
        self.surface = surface
        self.camera = Camera(Vector2(), config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.player = player.Player(Rectangle(Vector2(config.PLAYER_START_X, config.PLAYER_START_Y), config.PLAYER_WIDTH, config.PLAYER_HEIGHT))

        sprites.background = sprites.background.convert_alpha()
        #sprites.background.set_colorkey((255, 0, 255))

        pygame.joystick.init()
        if pygame.joystick.get_count():
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        pygame.mixer.music.load(sounds.main_theme)
        pygame.mixer.music.play()

        self.font = pygame.font.Font(None, 16)

        self.quit_state = None
        self.tick = pygame.USEREVENT
        self.time = Digit_System(Vector2(10, 10), 3, 0)
        #self.fps = Digit_System(Vector2(80, 10), 5, 0)
        #self.ups = Digit_System(Vector2(150, 10), 4, 0, 0, 1750)
        #self.acc = Digit_System(Vector2(230, 10), 3, 0, 0, 200)
        #self.timer = 0 # timer for counting up the race time
        pygame.time.set_timer(self.tick, 1000)

        self.last_velocity = 0

    def draw(self):
        """Draw all GameObjects and sprites that are currently on screen"""
        self.surface.fill(config.BACKGROUND_COLOR)
        self.draw_background()
        #self.draw_colliders()
        self.draw_items()
        self.draw_decals()
        self.player.draw(self.camera, self.surface)
        self.draw_digit_systems()

    def draw_background(self):
        """Extract rectangle from background image based on camera position"""
        self.surface.blit(sprites.background, (0, 0), (self.camera.pos.x, self.camera.pos.y, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    def draw_colliders(self):
        for collider in level.static_colliders:
            view_pos = self.camera.to_view_space(collider.rect.pos)
            pygame.draw.rect(self.surface, (0, 0, 0), (view_pos.x, view_pos.y, collider.rect.w, collider.rect.h))

        for collider in level.wall_colliders:
            view_pos = self.camera.to_view_space(collider.rect.pos)
            pygame.draw.rect(self.surface, (0, 0, 255), (view_pos.x, view_pos.y, collider.rect.w, collider.rect.h))

        for triangle in level.ramp_colliders:
            pygame.draw.polygon(self.surface, (160, 0, 44), [
                (triangle.rect.p1.x - self.camera.pos.x, triangle.rect.p1.y - self.camera.pos.y),
                (triangle.rect.p2.x - self.camera.pos.x, triangle.rect.p2.y - self.camera.pos.y),
                (triangle.rect.p3.x - self.camera.pos.x, triangle.rect.p3.y - self.camera.pos.y)
            ])

    def draw_items(self):
        for item in level.items:
            if item.get('picked_up', False):
                continue
            view_pos = self.camera.to_view_space(Vector2(item['pos'][0], item['pos'][1]))
            if item['type'] == 'rocket':
                self.surface.blit(sprites.item_set, (view_pos.x, view_pos.y), sprites.ITEM_ROCKET)
            elif item['type'] == 'plasma':
                self.surface.blit(sprites.item_set, (view_pos.x, view_pos.y), sprites.ITEM_PLASMA)

    def draw_decals(self):
        for decal in level.decals:
            self.surface.blit(sprites.item_set, (decal.x - self.camera.pos.x, decal.y - self.camera.pos.y), decal.sprite)

    def draw_digit_systems(self):
        """Draw all digit systems on screen"""

        #self.time.draw()

        fps = config.clock.get_fps()
        fpss = f"{0 if math.isinf(fps) else round(fps)}".rjust(6, "0")
        fps_text = self.font.render(f"FPS: {fpss}", True, (255, 255, 255))
        self.surface.blit(fps_text, (10, 10))

        acc = f"{config.LAST_BOOST}".rjust(4, "0")
        acc_text = self.font.render(f"ACC: {acc}", True, self.color_gradient(config.LAST_BOOST, 0, 200))
        self.surface.blit(acc_text, (120, 10))

        ups = f"{round(self.player.vel.x * 1000)}".rjust(5, "0")
        fps_text = self.font.render(f"UPS: {ups}", True,
                                    self.color_gradient(self.player.vel.x, 0, config.MAX_OVERAL_VEL))
        self.surface.blit(fps_text, (220, 10))

    def update_level(self):
        """Update all Gameobjects in the level"""

        for i in range(len(level.decals) - 1, -1, -1):
            if level.decals[i].start_time + level.decals[i].duration < pygame.time.get_ticks():
                del level.decals[i]
            elif level.decals[i].vel_x > 0:
                level.decals[i].x += level.decals[i].vel_x * config.delta_time
                self.last_velocity += config.delta_time
                if self.last_velocity > 1000 and (level.decals[i].vel_x > level.decals[i].target_vel):
                    level.decals[i].vel_x += level.decals[i].acc
                if level.decals[i].sound is not None:
                    distance = abs(self.player.pos.x - level.decals[i].x)
                    level.decals[i].sound.set_volume(1 - (distance / 1000))
                if level.decals[i].sprite == sprites.PROJECTILE_PLASMA or level.decals[i].sprite == sprites.PROJECTILE_ROCKET:
                    collider = level.decals[i].check_collisions(level.static_colliders + level.ramp_colliders)
                    if collider is not None:
                        if level.decals[i].sprite == sprites.PROJECTILE_ROCKET:
                            x = level.decals[i].x
                            y = level.decals[i].y
                            del level.decals[i]
                            level.decals.append(Decal(sprites.DECAL_ROCKET, 500, x, y))
                            distance = abs(self.player.pos.x - x)
                            sounds.rocket.set_volume(1 - (distance / 1000))
                            sounds.rocket.play()
                        if level.decals[i].sprite == sprites.PROJECTILE_PLASMA:
                            level.decals[i].x += random.randrange(-5, 5)
                            level.decals[i].y += random.randrange(-5, 5)
                            level.decals[i].vel_x = 0
                            level.decals[i].start_time = pygame.time.get_ticks()
                            level.decals[i].duration = 300





        self.player.update()
        self.camera.update(self.player)

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.type == self.tick:
                    self.time.update_value(self.time.total_value + 1)

            if event.type == pygame.JOYAXISMOTION:
                axis0 = self.joystick.get_axis(0)
                axis1 = self.joystick.get_axis(1)
                config.INPUT_DOWN = axis1 > 0.5
                config.INPUT_UP = axis1 < -0.5
                config.INPUT_LEFT = axis0 < -0.5
                config.INPUT_RIGHT = axis0 > 0.5

            if event.type == pygame.JOYBUTTONDOWN:
                config.INPUT_BUTTONS[event.button] = True

            if event.type == pygame.JOYBUTTONUP:
                config.INPUT_BUTTONS[event.button] = False

            if event.type == pygame.QUIT:
                return False


        if config.keys[pygame.K_ESCAPE] or config.INPUT_BUTTONS[8]:
            return False

        return True

    def color_gradient(self, value, min_value, max_value):
        """Returns (R, G, B) color from red (min) → yellow (mid) → green (max).
        value: the value to grade
        min_value: gradient starts here (red)
        max_value: gradient ends here (green)
        """
        # Clamp value to [min_value, max_value]
        value = max(min_value, min(max_value, value))
        mid = (min_value + max_value) / 2

        if value <= mid:
            # Red to Yellow
            r = 255
            g = int(255 * (value - min_value) / (mid - min_value))
            b = 0
        else:
            # Yellow to Green
            r = int(255 * (1 - (value - mid) / (max_value - mid)))
            g = 255
            b = 0
        return (r, g, b)

    def game_loop(self):
        """Main game loop, updates and draws the level every frame"""
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        while True:
            config.delta_time = config.clock.tick()
            config.keys = pygame.key.get_pressed()
            config.mods = pygame.key.get_mods()
            if not self.handle_pygame_events():
                break

            self.surface.fill(config.BACKGROUND_COLOR)
            self.update_level()
            self.draw()

            pygame.display.update()

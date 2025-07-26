import copy, math, pygame, random

from src.animation import Animation
from src.basetypes import Vector2, Entity, State_Machine, State
from src.utils import accelerate
from src import level, sounds, sprites, config

class Player(Entity):
    """Player Class"""
    def __init__(self, rect, vel = Vector2()):
        super(Player, self).__init__(vel, rect)
        self.ground_touch_time = 0
        self.last_walljump = 0
        self.last_ramp_radians = -1
        self.animation = Animation(self)
        self.action_states = State_Machine(self.Idle_State(), self)
        self.player_states = State_Machine(self.Default_Player(), self)
        self.last_velocity = 0
        self.pressed_left = False
        self.pressed_right = False
        self.jump_pressed_at = None
        self.spacebar = False
        self.crouching = False
        self.crouch = False
        self.freeze_movement = False
        self.freeze_input = False
        self.can_uncrouch = False
        self.flip_sprites = False
        self.to_menu = False

        self.start_height = 0

        sprites.player_set = sprites.player_set.convert_alpha()

    def __getattr__(self, name):
        """Shorter variable calls"""
        if name == 'current_action_state':
            return self.action_states.get_state()
        elif name == 'pos':
            return self.rect.pos
        elif name == 'current_player_state':
            return self.player_states.get_state()
        return object.__getattribute__(self, name)

    def draw(self):
        """Extract sprite from atlas"""
        if config.camera.contains(self.rect):
            view_pos_sprite = config.camera.to_view_space(Vector2(self.rect.pos.x - 16, self.rect.pos.y - (31 if self.crouching else 21)))
            config.surface.blit(sprites.player_set, (view_pos_sprite.x, view_pos_sprite.y), self.animation.current_sprite)

            #view_pos_rect = config.camera.to_view_space(self.rect.pos)
            #pygame.draw.rect(config.surface, (0, 255, 0), (view_pos_rect.x, view_pos_rect.y, self.rect.w, self.rect.h), width=2)

    def handle_inputs(self):
        """Get input and perform actions"""
        if self.freeze_input:
            return

        if config.INPUT_RIGHT or config.keys[pygame.K_d]:
            self.pressed_right = True

        if not config.keys[pygame.K_d] and not config.INPUT_RIGHT:
            self.pressed_right = False

        if (config.INPUT_UP or config.keys[pygame.K_w]) and (pygame.time.get_ticks() - self.last_walljump > 1000) and self.walljump_collisions():
            self.last_walljump = pygame.time.get_ticks()
            self.action_states.on_event('walljump')

        if (config.keys[pygame.K_SPACE] or config.INPUT_BUTTONS[0]) and not self.spacebar:
            if self.jump_pressed_at is None:
                self.jump_pressed_at = pygame.time.get_ticks()
            self.spacebar = True


        if not config.keys[pygame.K_SPACE] and not config.INPUT_BUTTONS[0]:
            self.jump_pressed_at = None
            self.spacebar = False

        if config.keys[pygame.K_s] or config.INPUT_DOWN:
            self.crouch = True
        else:
            self.crouch = False

    def update(self):

        self.handle_inputs()

        self.can_uncrouch = self.crouching and self.check_can_uncrouch()

        if self.spacebar and (not self.crouching or self.can_uncrouch):
            self.jump_diff = pygame.time.get_ticks() - self.jump_pressed_at
            if self.jump_diff < 300:
                self.action_states.on_event('jump')

        if self.vel.x == 0 and self.vel.y == 0 and self.crouching and not self.can_uncrouch:
            self.player_states.on_event('dead')

        if not self.freeze_movement:
            self.state_events()
            self.action_states.update()
            self.movement()

            #Make sure that player can't jump when running off a ledge
            #if self.pos.y > self.start_height:
            #    self.action_states.on_event('fall')

        self.player_states.update()

        #self.rect.h = self.animation.current_sprite[3]

        if self.pos.y > config.SCREEN_HEIGHT:
            self.player_states.on_event('dead')

    def movement(self):
        # apply friction independent of fps
        self.last_velocity += config.delta_time
        if self.last_velocity > 20:
            self.vel.x *= config.FRICTION
            self.last_velocity = 0

            if any(self.current_action_state == state for state in ['Jump_State', 'Fall_State', 'Idle_State', 'Crouch_State']):
                self.vel.y += config.GRAVITY
                if self.vel.y >= 0:
                    self.action_states.on_event('fall')

        accelerate(self, config.ACCELERATION, 0, config.MAX_OVERAL_VEL)
        self.move()

    def move(self):
        """Separates x and y movement"""
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """Move based on velocity and check for collisions based on new position"""
        self.pos.x += dx * config.delta_time
        self.pos.y += dy * config.delta_time

        self.collider_collisions(dx, dy)
        self.ramp_collisions()

    def state_events(self):
        """Change current state based on events and perform actions based on current state"""

        if any(self.current_action_state == state for state in ['Move_State', 'Decel_State', 'Idle_State', 'Crouch_State']):
            self.start_height = self.pos.y

        if self.vel.y == 0 and (not self.crouching or self.can_uncrouch):

            if self.pressed_right and not self.crouch:
                self.action_states.on_event('move')

            if self.vel.x > 0 and not self.pressed_right and not self.crouch:
                self.action_states.on_event('decel')

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State':
                self.vel.x = 0
                self.action_states.on_event('idle')

        elif self.crouching and abs(self.vel.x) < 0.02:
            self.vel.x = 0

        if all(self.current_action_state != state for state in ['Decel_State', 'Crouch_State']):
            config.FRICTION = 1

        if self.current_action_state != 'Crouch_State' and self.crouch:
            self.action_states.on_event('crouch')

    def collider_collisions(self, dx, dy):
        """Check for collisions with tiles"""
        other_collider = self.rect.check_collisions(level.static_colliders)

        if other_collider is None:
            return

        if dx > 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x - self.rect.w
            self.vel.x = 0
        elif dx < 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x + other_collider.rect.w
            self.vel.x = 0
        elif dy > 0:
            if self.current_action_state == 'Fall_State':
                self.ground_touch_time = pygame.time.get_ticks()
                self.action_states.on_event('idle')
            self.pos.y = other_collider.pos.y - self.rect.h
            self.vel.y = 0
        elif dy < 0:
            self.action_states.on_event('fall')
            self.pos.y = other_collider.pos.y + other_collider.rect.h
            self.vel.y = config.BOUNCE_VEL

    def ramp_collisions(self):

        if self.current_action_state == 'Jump_State':
            return

        ramp_collider = self.rect.check_triangle_collisions(level.ramp_colliders)

        # keep momentum when leaving a ramp
        if ramp_collider is None:
            if self.last_ramp_radians > 0:
                self.vel.y = - 0.4 * (self.vel.x * math.sin(self.last_ramp_radians) + self.vel.x * math.cos(self.last_ramp_radians))
                self.last_ramp_radians = 0
                self.action_states.on_event('fall')
            return

        # Get the relevant ramp start and end points
        x0 = ramp_collider.p1.x  # base start x
        y0 = ramp_collider.p1.y  # base start y
        x1 = ramp_collider.p3.x  # top of ramp x
        y1 = ramp_collider.p3.y  # top of ramp y

        # Calculate horizontal progress (progress ratio) across the ramp
        x = self.rect.pos.x + self.rect.w / 2  # Player center x
        ramp_width = x1 - x0 if x1 != x0 else 1  # avoid div by zero
        progress = (x - x0) / ramp_width
        progress = max(0, min(1, progress))  # Clamp to [0,1]

        # Linear interpolation from base y to top y
        y_on_ramp = (1 - progress) * y0 + progress * y1

        # Set player's feet to ramp surface (assume rect.h = player height)
        self.rect.pos.y = y_on_ramp - self.rect.h

        # Remember an angle for momentum when leaving the ramp
        self.last_ramp_radians = math.atan2(x1 - x0, y1 - y0)

        self.vel.y = 0

        self.action_states.on_event('ramp')

    def walljump_collisions(self):
        """Check for collisions with walls when walljumping"""
        wall_collider = self.rect.check_collisions(level.wall_colliders)

        return wall_collider is not None

    def check_can_uncrouch(self):
        stand_rect = copy.copy(self.rect)
        stand_rect.pos = copy.copy(self.rect.pos)
        stand_rect.pos.y -= (config.PLAYER_HEIGHT - self.rect.h)
        stand_rect.h = config.PLAYER_HEIGHT
        for collider in level.static_colliders:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.rect.w >= 100:
                if stand_rect.overlaps(collider.rect):
                    return False

        return True

    class Idle_State(State):
        """State when on the ground and not moving"""
        #def on_enter(self, owner_object):
        #    owner_object.animation.current_sprite = sprites.PLAYER_RUN[owner_object.animation.anim_frame] if owner_object.animation.anim_frame in sprites.PLAYER_RUN else sprites.PLAYER_IDLE

        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

    class Jump_State(State):
        """State when jumping when spacebar input affects velocity"""

        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            owner_object.last_walljump = 0
            current_frame = owner_object.animation.anim_frame
            owner_object.animation.end_frame = 5 if current_frame < 5 or current_frame == 11 else 11

            if random.choice([True, False]):
                sounds.jump1.play()
            else:
                sounds.jump2.play()


            ground_diff = pygame.time.get_ticks() - owner_object.ground_touch_time
            diff = max(10, owner_object.jump_diff, ground_diff)
            boost = round(1.75 / diff, 3)

            if not owner_object.pressed_right:
                boost *= 1.33

            config.ACCELERATION = 0
            config.LAST_BOOST = round(boost * 1000)


            if config.player.vel.x < 0.2:
                config.player.vel.x = 0.15

            owner_object.vel.y = config.JUMP_VELOCITY

            # add additional momentum when jumping from a ramp
            if owner_object.last_ramp_radians > 0:
                owner_object.vel.y -= 0.125 * (owner_object.vel.x * math.sin(owner_object.last_ramp_radians) + owner_object.vel.x * math.cos(owner_object.last_ramp_radians))
                owner_object.last_ramp_radians = 0

            owner_object.vel.x += boost


        def update(self, owner_object):
            owner_object.animation.jump_anim()

    class Walljump_State(State):
        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            if random.choice([True, False]):
                sounds.walljump1.play()
            else:
                sounds.walljump2.play()

        def update(self, owner_object):
            owner_object.vel.y = config.WALLJUMP_VELOCITY
            owner_object.action_states.on_event('fall')

    class Fall_State(State):
        """State when in mid air but spacebar input does not affect velocity"""
        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'ramp':
                return Player.Move_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            owner_object.last_ramp_radians = 0

        def update(self, owner_object):
            owner_object.animation.jump_anim()

    class Move_State(State):
        """State when moving on the ground and not breaking or decelerating"""
        def on_event(self, event):
            if event == 'decel':
                return Player.Decel_State()
            elif event == 'fall':
                return Player.Fall_State()
            elif event == 'jump':
                return Player.Jump_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            elif event == 'idle':
                return Player.Idle_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

        def update(self, owner_object):
            if not owner_object.pressed_right:
                return

            if owner_object.vel.x > 1:
                config.FRICTION = 1 - owner_object.vel.x / 23
            else:
                config.FRICTION = 1 - owner_object.vel.x / 142

            if owner_object.vel.x < config.MAX_RUN_VEL:
                config.ACCELERATION = config.PLAYER_ACCELERATION
            else:
               config.ACCELERATION = 0

            owner_object.animation.run_anim()

    class Decel_State(State):
        """State when moving when there is no longer any input"""
        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'fall':
                return Player.Fall_State()
            elif event == 'jump':
                return Player.Jump_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            config.ACCELERATION = 0
            config.FRICTION = config.DECEL_FRICTION

        def update(self, owner_object):
            owner_object.animation.run_anim()

    class Default_Player(State):
        """State when player is big"""
        def on_event(self, event):
            if event == 'shrink':
                return Player.Shrink_Player()
            elif event == 'dead':
                return Player.Dead_Player()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

    class Crouch_State(State):
        """State when player is crouching"""
        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'idle':
                return Player.Idle_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            if owner_object.last_ramp_radians > 0:
                config.FRICTION = config.RAMP_FRICTION
            else:
                config.FRICTION = config.BRAKE_FRICTION
            owner_object.animation.current_sprite = sprites.PLAYER_CROUCH
            owner_object.pos.y += (config.PLAYER_HEIGHT - config.PLAYER_CROUCH_HEIGHT)
            owner_object.rect.h = config.PLAYER_CROUCH_HEIGHT
            owner_object.crouching = True

        def update(self, owner_object):
            config.ACCELERATION = 0

        def on_exit(self, owner_object):
            owner_object.animation.current_sprite = sprites.PLAYER_IDLE
            owner_object.pos.y -= (config.PLAYER_HEIGHT - config.PLAYER_CROUCH_HEIGHT)
            owner_object.start_height = owner_object.pos.y
            owner_object.rect.h = config.PLAYER_HEIGHT
            owner_object.crouching = False

    class Dead_Player(State):
        """State when player is dead"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            owner_object.animation.current_sprite = sprites.DEAD_PLAYER
            owner_object.vel.y = config.DEATH_VEL_Y
            owner_object.vel.x = 0
            owner_object.freeze_movement = True
            owner_object.freeze_input = True
            pygame.mixer.music.stop()
            sounds.death.play()

        def update(self, owner_object):
            self.death_timer += config.delta_time
            if self.death_timer > 20 * config.delta_time:
                accelerate(owner_object, 0, config.GRAVITY)
                owner_object.pos += owner_object.vel * config.delta_time


            
            



        
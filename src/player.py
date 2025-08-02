import copy, math, pygame, random

from pygame.time import get_ticks

from src.animation import Animation
from src.basetypes import Vector2, Entity, State_Machine, State, Decal, Camera, Rectangle
from src.utils import accelerate
from src import level, sounds, sprites, config

class Player(Entity):
    def __init__(self, surface: pygame.surface.Surface, camera: Camera):
        super(Player, self).__init__(Vector2(0, 0), Rectangle(Vector2(0, 0), config.PLAYER_WIDTH, config.PLAYER_HEIGHT))
        self.camera = camera
        self.surface = surface
        self.level = None

        self.ground_touch_time = 0
        self.last_walljump = 0
        self.last_ramp_radians = -1
        self.animation = Animation(self)
        self.action_states = State_Machine(self.Idle_State(), self)
        self.player_states = State_Machine(self.Default_Player(), self)
        self.last_velocity = 0
        self.pressed_up = False
        self.pressed_left = False
        self.pressed_right = False
        self.lifted_right = False
        self.jump_pressed_at = None
        self.pressed_jump = False
        self.crouching = False
        self.pressed_down = False
        self.freeze_movement = False
        self.freeze_input = False
        self.can_uncrouch = False
        self.flip_sprites = False
        self.shooting = False
        self.jump_diff = float("inf")

        self.start_height = 0

        self.has_rocket = False
        self.rocket_ammo = 0
        self.last_rocket_time = 0

        self.has_plasma = False
        self.plasma_ammo = 0
        self.last_plasma_time = 0

        self.active_weapon = None
        self.last_weapon_switch = 0

        self.is_plasma_climbing = False

        sprites.player_set = sprites.player_set.convert_alpha()

    def set_level(self, level):
        self.level = level
        self.shape.pos = level.player_start

    def __getattr__(self, name):
        if name == 'current_action_state':
            return self.action_states.get_state()
        elif name == 'pos':
            return self.shape.pos
        elif name == 'current_player_state':
            return self.player_states.get_state()
        return object.__getattribute__(self, name)

    def draw(self):
        #if camera.contains(self.rect):
        view_pos_sprite = self.camera.to_view_space(
            Vector2(
                self.shape.pos.x - 16,
                self.shape.pos.y - (31 if self.crouching else 21)
            )
        )

        # 1. Crop the current sprite frame
        sprite_surface = sprites.player_set.subsurface(self.animation.current_sprite).copy()

        # 2. Rotate the sprite
        rotated_sprite = pygame.transform.rotate(sprite_surface, self.last_ramp_radians * -10)

        # 3. Center the rotated sprite on the position
        rect = rotated_sprite.get_rect(center=(view_pos_sprite.x + sprite_surface.get_width() // 2,
                                               view_pos_sprite.y + sprite_surface.get_height() // 2))

        # 4. Blit the rotated sprite
        self.surface.blit(rotated_sprite, rect.topleft)

    def handle_inputs(self):
        if self.freeze_input:
            return

        if config.INPUT_UP or config.keys[pygame.K_w]:
            self.pressed_up = True
        elif not config.INPUT_UP and not config.keys[pygame.K_w]:
            self.pressed_up = False

        if config.keys[pygame.K_s] or config.INPUT_DOWN:
            self.pressed_down = True
        elif not config.keys[pygame.K_s] and not config.INPUT_DOWN:
            self.pressed_down = False

        if config.INPUT_RIGHT or config.keys[pygame.K_d]:
            self.pressed_right = True
        elif not config.INPUT_RIGHT and not config.keys[pygame.K_d]:
            self.lifted_right = True
            self.pressed_right = False

        if config.INPUT_LEFT or config.keys[pygame.K_a]:
            self.pressed_left = True
        elif not config.INPUT_LEFT and not config.keys[pygame.K_a]:
            self.pressed_left = False


        if (config.INPUT_BUTTONS[1] or config.mods & pygame.KMOD_ALT) and (pygame.time.get_ticks() - self.last_walljump > 1000) and self.walljump_collisions():
            self.last_walljump = pygame.time.get_ticks()
            self.action_states.on_event('walljump')

        if (config.INPUT_BUTTONS[3] or config.mods & pygame.KMOD_CTRL) and self.last_weapon_switch + 666 < pygame.time.get_ticks():
            if self.active_weapon == 'rocket' and self.has_plasma:
                self.active_weapon = 'plasma'
            elif self.active_weapon == 'plasma' and self.has_rocket:
                self.active_weapon = 'rocket'
            self.animation.set_active_weapon()
            self.last_weapon_switch = pygame.time.get_ticks()

        if config.keys[pygame.K_RETURN] or config.INPUT_BUTTONS[2]:
            self.shooting = True
        elif not config.keys[pygame.K_RETURN] and not config.INPUT_BUTTONS[2]:
            self.shooting = False

        if (config.keys[pygame.K_SPACE] or config.INPUT_BUTTONS[0]) and not self.pressed_jump:
            if self.jump_pressed_at is None:
                self.jump_pressed_at = pygame.time.get_ticks()
            self.pressed_jump = True


        if not config.keys[pygame.K_SPACE] and not config.INPUT_BUTTONS[0]:
            self.jump_pressed_at = None
            self.pressed_jump = False


    def update(self):

        self.handle_inputs()

        self.can_uncrouch = self.crouching and self.check_can_uncrouch()

        if self.pressed_jump and (not self.crouching or self.can_uncrouch):
            self.jump_diff = pygame.time.get_ticks() - self.jump_pressed_at
            if self.jump_diff < 300:
                self.action_states.on_event('jump')

        if not self.freeze_movement:
            self.state_events()
            self.action_states.update()
            self.movement()

        self.player_states.update()

        if self.shooting:
            ticks = pygame.time.get_ticks()
            if self.active_weapon == 'rocket':
                if self.last_rocket_time + 1337 < ticks:
                    self.last_rocket_time = pygame.time.get_ticks()
                    if self.rocket_ammo <= 0:
                        sounds.weapon_empty.play()
                    else:
                        self.rocket_ammo -= 1
                        if self.pressed_down:
                            sounds.rocket_launch.play()
                            sounds.rocket.play()
                            self.action_states.on_event('rocket')
                        else:
                            sounds.rocket_launch.play()
                            channel = sounds.rocket_fly.play(loops=-1)
                            self.level.decals.append(Decal(sprites.PROJECTILE_ROCKET, 1337000, self.pos.x + 40, self.pos.y + 8, self.vel.x + 1, 1, -0.00075, channel))


            elif self.active_weapon == 'plasma':
                if self.last_plasma_time + 100 < ticks:
                    self.last_plasma_time = ticks
                    if self.plasma_ammo <= 0:
                        sounds.weapon_empty.play()
                    else:
                        sounds.plasma.play()
                        self.plasma_ammo -= 1
                        if (self.pressed_down or self.pressed_left or self.pressed_up or self.pressed_right) and self.plasma_climb_collisions():
                            self.action_states.on_event('plasma')
                            self.level.decals.append(Decal(sprites.DECAL_PLASMA, 1000, self.pos.x + 25, self.pos.y + 5))
                            if self.pressed_down:
                                if self.pressed_left or self.pressed_right:
                                    self.vel.y -= 0.08
                                else:
                                    self.vel.y -= 0.1
                            elif self.pressed_up:
                                self.vel.y += 0.02

                            if self.pressed_left:
                                self.vel.x += 0.05
                            elif self.pressed_right:
                                self.vel.x -= 0.05
                        else:
                            self.level.decals.append(Decal(sprites.PROJECTILE_PLASMA, 10000, self.pos.x + 30, self.pos.y + 5, 1 + self.vel.x))

        else:
            if self.current_action_state == 'Plasma_State':
                self.action_states.on_event('fall')


        self.animation.animate()

    def get_distance_to_collider_below(self):
        player_bottom = self.shape.pos.y + self.shape.h
        player_centerx = self.shape.pos.x + self.shape.w / 2

        min_distance = None  # None means no collider found below

        # Check static (rectangle) colliders
        for collider in self.level.static_colliders:
            if collider.shape.pos.x <= player_centerx <= collider.shape.pos.x + collider.shape.w:
                if collider.shape.pos.y >= player_bottom:
                    distance = collider.shape.pos.y - player_bottom
                    if min_distance is None or distance < min_distance:
                        min_distance = distance

        # Check ramp (triangle) colliders
        for collider in self.level.ramp_colliders:
            tri = collider.shape
            if tri.p1.x <= player_centerx <= tri.p2.x:
                print("above ramp")
                t = (player_centerx - tri.p1.x) / (tri.p3.x - tri.p1.x)
                y_on_edge = tri.p1.y + t * (tri.p3.y - tri.p1.y)
                print(y_on_edge)
                print(player_bottom)
                if y_on_edge >= player_bottom:
                    distance = y_on_edge - player_bottom
                    if min_distance is None or distance < min_distance:
                        min_distance = distance

        return min_distance

    def movement(self):
        self.last_velocity += config.delta_time
        if self.last_velocity > 20:
            self.vel.x *= config.FRICTION
            self.last_velocity = 0
            #if any(self.current_action_state == state for state in ['Jump_State', 'Walljump_State', 'Fall_State', 'Idle_State', 'Crouch_State']):
            self.vel.y += config.GRAVITY

            if self.vel.y >= 0 and self.current_action_state != 'Plasma_State':
                self.vel.y = min(self.vel.y, config.MAX_FALL_VEL)
                self.action_states.on_event('fall')
            if not self.pressed_left and not self.pressed_right and not self.pressed_up and not self.pressed_down and self.current_action_state == 'Plasma_State':
                self.action_states.on_event('fall')

        accelerate(self, config.ACCELERATION, 0, config.MAX_OVERAL_VEL)
        self.move()

    def move(self):
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        self.pos.x += dx * config.delta_time
        self.pos.y += dy * config.delta_time

        self.collider_collisions(dx, dy)
        self.ramp_collisions()
        self.item_collisions()

    def state_events(self):
        if any(self.current_action_state == state for state in ['Move_State', 'Decel_State', 'Idle_State', 'Crouch_State']):
            self.start_height = self.pos.y

        if self.vel.y == 0 and (not self.crouching or self.can_uncrouch):

            if self.pressed_right and not self.pressed_down:
                self.action_states.on_event('move')

            if self.vel.x > 0 and not self.pressed_right and not self.pressed_down:
                self.action_states.on_event('decel')

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State':
                self.vel.x = 0
                self.action_states.on_event('idle')

        elif self.crouching and self.vel.x < 0.02:
            self.vel.x = 0

        if all(self.current_action_state != state for state in ['Decel_State', 'Crouch_State']):
            config.FRICTION = 1

        if self.current_action_state != 'Crouch_State' and self.pressed_down:
            self.action_states.on_event('crouch')

    def collider_collisions(self, dx, dy):
        other_collider = self.shape.check_collisions(self.level.static_colliders)

        if other_collider is None:
            return

        if self.current_action_state == 'Plasma_State':
         self.vel.x -= 0.1

        if dx > 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x - self.shape.w
            self.vel.x = 0
        elif dx < 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x + other_collider.shape.w
            self.vel.x = 0
        elif dy > 0:
            if self.current_action_state == 'Fall_State':
                self.ground_touch_time = pygame.time.get_ticks()
                self.action_states.on_event('idle')
            self.pos.y = other_collider.pos.y - self.shape.h
            self.vel.y = 0
        elif dy < 0:
            self.action_states.on_event('fall')
            self.pos.y = other_collider.pos.y + other_collider.shape.h
            self.vel.y = config.BOUNCE_VEL

    def add_ramp_momentum(self):
        # Calculate the component of velocity parallel to the ramp
        # Note: ramp_radians is the angle from horizontal, so we need to adjust
        parallel_velocity = self.vel.x * math.cos(self.last_ramp_radians) - self.vel.y * math.sin(self.last_ramp_radians)

        # Apply conservation of momentum when leaving the ramp
        # The parallel component gets split between x and y based on ramp angle
        # We use a coefficient to tune the effect for gameplay feel
        coefficient = 1.3  # Tuned for gameplay feel (0.85 = 85% conservation)

        # Calculate new vertical velocity component
        # More horizontal speed and steeper ramps result in more "launch"
        momentum = coefficient * parallel_velocity * math.sin(self.last_ramp_radians)

        # Add a small boost based on ramp steepness for more dramatic effects on steep ramps
        steepness_boost = abs(math.sin(self.last_ramp_radians)) * 0.1

        # Apply the momentum and boost to vertical velocity
        self.vel.y += momentum + steepness_boost

        # Cap the vertical velocity to prevent excessive launching
        max_launch_vel = config.MAX_FALL_VEL * coefficient
        self.vel.y = max(-max_launch_vel, min(self.vel.y, max_launch_vel))

        # Debug info
        print("ramp momentum", momentum, "steepness boost", steepness_boost, "final y-vel", self.vel.y)

        # Set the player state to falling
        self.action_states.on_event('fall')

    def ramp_collisions(self):

        #if self.current_action_state == 'Jump_State' or self.current_action_state == 'Rocket_State':
        #    return

        ramp_collider = self.shape.check_triangle_top_sides_collision(self.level.ramp_colliders)

        # keep momentum when leaving a ramp
        if ramp_collider is None:
            if self.last_ramp_radians < 0:
                self.add_ramp_momentum()
            self.last_ramp_radians = 0
            return

        # Get the relevant ramp start and end points
        x0 = ramp_collider[0].x  # base start x
        y0 = ramp_collider[0].y  # base start y
        x1 = ramp_collider[1].x  # top of ramp x
        y1 = ramp_collider[1].y  # top of ramp y

        # Remember an angle for momentum when leaving the ramp
        next_rad = math.atan2(x1 - x0, y1 - y0)

        # keep momentum when sliding over the peak of a two-sided ramp
        if self.last_ramp_radians < 0 < next_rad:
            self.add_ramp_momentum()
            return

        self.last_ramp_radians = next_rad


        # Calculate horizontal progress (progress ratio) across the ramp
        x = self.shape.pos.x + self.shape.w / 2  # Player center x
        ramp_width = x1 - x0 if x1 != x0 else 0.001  # avoid div by zero
        progress = (x - x0) / ramp_width
        progress = max(0, min(1, progress))  # Clamp to [0,1]

        # Linear interpolation from base y to top y
        y_on_ramp = (1 - progress) * y0 + progress * y1

        # Set player's feet to ramp surface (assume rect.h = player height)
        self.shape.pos.y = y_on_ramp - self.shape.h



        self.vel.y = 0

        self.action_states.on_event('ramp')

    def item_collisions(self):
        for item in self.level.items:
            if item.picked_up:
                continue
            if item.pos.x - 10 <= self.pos.x + self.shape.w / 2 <= item.pos.x + 10 and item.pos.y - 10 <= self.pos.y + self.shape.h / 2 <= item.pos.y + 10:
                sounds.pickup.play()
                self.active_weapon = item.item_type
                if item.item_type == 'rocket':
                    self.has_rocket = True
                    self.rocket_ammo = item.ammo
                elif item.item_type == 'plasma':
                    self.has_plasma = True
                    self.plasma_ammo = item.ammo
                item.picked_up = True
                self.animation.set_active_weapon()#

    def walljump_collisions(self):
        wall_collider = self.shape.check_collisions(self.level.wall_colliders)

        return wall_collider is not None

    def plasma_climb_collisions(self):
        wall_collider = self.shape.check_center_collisions(self.level.wall_colliders)

        return wall_collider is not None

    def check_can_uncrouch(self):
        stand_rect = copy.copy(self.shape)
        stand_rect.pos = copy.copy(self.shape.pos)
        stand_rect.pos.y -= (config.PLAYER_HEIGHT - self.shape.h)
        stand_rect.h = config.PLAYER_HEIGHT
        for collider in self.level.static_colliders:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.shape.w >= 100:
                if stand_rect.overlaps(collider.shape):
                    return False

        return True

    def add_jump_velocity(self):
        ground_diff = pygame.time.get_ticks() - self.ground_touch_time
        diff = max(10, self.jump_diff, ground_diff)
        boost = round(1.75 / diff, 3)

        if not self.pressed_right:
            boost *= 1.33

        config.ACCELERATION = 0
        config.LAST_BOOST = round(boost * 1000)

        if self.vel.x < 0.2:
            self.vel.x = 0.15

        self.vel.y = config.JUMP_VELOCITY
        print("jump vel", self.vel.y)

        # add additional momentum when jumping from a ramp
        #if self.last_ramp_radians > 0:
        #    self.vel.y -= 0.125 * (self.vel.x * math.sin(self.last_ramp_radians) + self.vel.x * math.cos(self.last_ramp_radians))
        #    self.last_ramp_radians = 0

        if self.last_ramp_radians != 0:
            y_offset = abs(math.cos(self.last_ramp_radians) * (self.vel.x + 0.1) * 100)
            print("ramp y offset", y_offset)
            self.pos.y -= y_offset  # Apply the offset
            self.last_ramp_radians = 0

        self.vel.x += boost

    def add_rocket_velocity(self):
        distance = self.get_distance_to_collider_below()
        print("rocket distance", distance)
        if distance is not None:
            if distance < 1 and not self.pressed_jump:
                vel = 0.4
            elif distance <= 5:
                vel = 0.32
            elif distance < 10:
                vel = 0.256
            elif distance < 20:
                vel = 0.223
            elif distance < 30:
                vel = 0.2
            elif distance < 40:
                vel = 0.175
            elif distance < 50:
                vel = 0.15
            elif distance < 60:
                vel = 0.125
            else:
                vel = 0

            # add additional momentum when jumping from a ramp
            if self.last_ramp_radians > 0:
                vel += 0.225 * (self.vel.x * math.sin(self.last_ramp_radians) + self.vel.x * math.cos(self.last_ramp_radians))
                self.last_ramp_radians = 0

            self.vel.y -= vel
            print("rocket vel", vel)

        return distance

    class Idle_State(State):
        """State when on the ground and not moving"""
        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            return

    class Jump_State(State):
        """State when jumping when spacebar input affects velocity"""

        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            owner_object.last_walljump = 0
            owner_object.animation.begin_jump()

            if random.choice([True, False]):
                sounds.jump1.play()
            else:
                sounds.jump2.play()

            owner_object.add_jump_velocity()

        def update(self, owner_object):
            if owner_object.pressed_right and owner_object.vel.x < 0.1:
                config.ACCELERATION = 0.0005

    class Walljump_State(State):
        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            if random.choice([True, False]):
                sounds.walljump1.play()
            else:
                sounds.walljump2.play()

            owner_object.vel.y = config.WALLJUMP_VELOCITY
            owner_object.animation.reset_anim()


    class Rocket_State(State):
        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            owner_object.animation.reset_anim()
            distance = owner_object.add_rocket_velocity()
            owner_object.level.decals.append(Decal(sprites.DECAL_ROCKET, 500, owner_object.pos.x, owner_object.pos.y + distance + owner_object.shape.h / 2 + 10))


        def update(self, owner_object):
            if owner_object.last_rocket_time + 350 > pygame.time.get_ticks():
                owner_object.action_states.on_event('jump')

    class Plasma_State(State):
        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'idle':
                return Player.Idle_State()
            elif event == 'decel':
                return Player.Decel_State()
            return self

        def on_enter(self, owner_object):
            owner_object.animation.reset_anim()

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
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            owner_object.last_ramp_radians = 0
            # allows moving forward when stuck in front of a wall
            #if owner_object.vel.x == 0:
            #    owner_object.vel.x = 0.02

        def update(self, owner_object):
            if owner_object.pressed_right and owner_object.vel.x < 0.1:
                config.ACCELERATION = 0.0005

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
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            return

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
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            config.ACCELERATION = 0
            config.FRICTION = config.DECEL_FRICTION

    class Default_Player(State):
        """State when player is big"""
        def on_event(self, event):
            if event == 'shrink':
                return Player.Shrink_Player()
            elif event == 'dead':
                return Player.Dead_Player()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            return

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
            elif event == 'rocket':
                return Player.Rocket_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            owner_object.pos.y += (config.PLAYER_HEIGHT - config.PLAYER_CROUCH_HEIGHT)
            owner_object.shape.h = config.PLAYER_CROUCH_HEIGHT
            owner_object.crouching = True

        def update(self, owner_object):
            config.ACCELERATION = 0
            if owner_object.pressed_right:
                if owner_object.vel.x == 0 and owner_object.lifted_right:
                    owner_object.vel.x = 0.1
                    owner_object.lifted_right = False
                if owner_object.last_ramp_radians > 0:
                    # For ramps, friction should be above 1 to create acceleration based on steepness
                    # The steeper the ramp, the higher the value (more acceleration)
                    ramp_steepness = math.cos(owner_object.last_ramp_radians)
                    config.FRICTION = 1.0 + ramp_steepness * 0.1 # Ensures friction is always > 1
                else:
                    config.FRICTION = config.SLIDE_FRICTION
            else:
                config.FRICTION = config.CROUCH_FRICTION

        def on_exit(self, owner_object):
            owner_object.pos.y -= (config.PLAYER_HEIGHT - config.PLAYER_CROUCH_HEIGHT)
            owner_object.start_height = owner_object.pos.y
            owner_object.shape.h = config.PLAYER_HEIGHT
            owner_object.crouching = False


    class Dead_Player(State):
        """State when player is dead"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

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


            
            



        
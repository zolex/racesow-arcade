import copy, math, pygame, random, os

from src.Animation import Animation
from src.Entity import Entity
from src.Rectangle import Rectangle
from src.StateMachine import StateMachine
from src.State import State
from src.Camera import Camera
from src.Vector2 import Vector2
from src.utils import accelerate
from src.Projectile import Projectile
from src import sounds, config

class Player(Entity):
    def __init__(self, surface: pygame.surface.Surface, camera: Camera):
        super(Player, self).__init__(Vector2(0, 0), Rectangle(Vector2(0, 0), WIDTH, HEIGHT))
        self.distance_to_ground = 0
        self.last_boost = 0
        self.acceleration = 0
        self.camera = camera
        self.surface = surface
        self.level = None
        self.last_walljump = 0
        self.last_ramp_radians = -1
        self.animation = Animation(self)
        self.action_states = StateMachine(self.Idle_State(), self)
        self.player_states = StateMachine(self.Default_Player(), self)
        self.last_velocity = 0
        self.pressed_up = False
        self.pressed_left = False
        self.pressed_right = False
        self.lifted_right = False
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

        self.jump_pressed_at = None
        self.jump_action_distance = 0
        self.jumped_early = None
        self.jumped_late = None
        self.ground_touch_time = 0
        self.ground_touch_pos = Vector2(0,0)


        self.has_rocket = False
        self.rocket_ammo = 0
        self.last_rocket_time = 0

        self.has_plasma = False
        self.plasma_ammo = 0
        self.last_plasma_time = 0

        self.active_weapon = None
        self.last_weapon_switch = 0

        self.is_plasma_climbing = False

        player = pygame.image.load(os.path.join(config.assets_folder, 'graphics', 'player.png'))
        new_size = (player.get_width() * P_SCALE, player.get_height() * P_SCALE)
        self.sprite = pygame.transform.smoothscale(player, new_size).convert_alpha()
        self.height = player.get_height() * P_SCALE

    def reset(self):
        self.distance_to_ground = 0
        self.last_boost = 0
        self.acceleration = 0
        self.ground_touch_time = 0
        self.last_walljump = 0
        self.last_ramp_radians = -1
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

        self.shape.pos = Vector2(0, 180)
        self.vel = Vector2(0, 0)
        self.action_states = StateMachine(self.Fall_State(), self)
        self.player_states = StateMachine(self.Default_Player(), self)

        print("player reset")

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
        sprite_surface = self.sprite.subsurface(self.animation.current_sprite).copy()

        # 2. Rotate the sprite
        rotated_sprite = pygame.transform.rotate(sprite_surface, self.last_ramp_radians * -10)

        # 3. Center the rotated sprite on the position
        rect = rotated_sprite.get_rect(center=(view_pos_sprite.x + sprite_surface.get_width() // 2, view_pos_sprite.y + sprite_surface.get_height() // 2))

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
                self.jump_action_distance = self.get_distance_to_collider_below()
            self.pressed_jump = True


        if not config.keys[pygame.K_SPACE] and not config.INPUT_BUTTONS[0]:
            self.jump_pressed_at = None
            self.pressed_jump = False


    def update(self):

        self.handle_inputs()

        self.can_uncrouch = self.crouching and self.check_can_uncrouch()
        self.distance_to_ground = self.get_distance_to_collider_below()

        # Handle state transitions
        if self.vel.y > 0 and self.current_action_state != 'Plasma_State':
            self.action_states.on_event('fall')
        if not self.pressed_left and not self.pressed_right and not self.pressed_up and not self.pressed_down and self.current_action_state == 'Plasma_State':
            self.action_states.on_event('fall')

        if self.pressed_jump and (not self.crouching or self.can_uncrouch):
            self.jump_diff = pygame.time.get_ticks() - self.jump_pressed_at
            if self.jump_diff < 333:
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
                        sounds.rocket_launch.play()
                        channel = sounds.rocket_fly.play(loops=-1)
                        if self.pressed_down:
                            #self.action_states.on_event('rocket')
                            self.level.projectiles.append(Projectile(Projectile.PROJECTILE_ROCKET_DOWN, 1337000, self.pos.x + 15, self.pos.y + 8, self.vel.x, self.vel.y + 1 , 0.7, -0.0015, channel))
                        else:
                            self.level.projectiles.append(Projectile(Projectile.PROJECTILE_ROCKET, 1337000, self.pos.x + 40, self.pos.y + 8, self.vel.x + 1, 0, 1.1, -0.00075, channel))


            elif self.active_weapon == 'plasma':
                if self.last_plasma_time + 100 < ticks:
                    self.last_plasma_time = ticks
                    if self.plasma_ammo <= 0:
                        sounds.weapon_empty.play()
                    else:
                        sounds.plasma.play()
                        self.plasma_ammo -= 1
                        if (self.pressed_down or self.pressed_left or self.pressed_up or self.pressed_right) and self.plasma_climb_collisions():
                            if self.pressed_left:
                                decal_offset = 3
                            elif self.pressed_right:
                                decal_offset = 14
                            else:
                                decal_offset = 7
                            self.action_states.on_event('plasma')
                            self.level.projectiles.append(Projectile(Projectile.DECAL_PLASMA, 1000, self.pos.x + decal_offset, self.pos.y + 5))
                            if self.pressed_down:
                                if self.pressed_left or self.pressed_right:
                                    self.vel.y -= 0.08
                                else:
                                    self.vel.y -= 0.1
                                # add some extra velocity if climbing very slow
                                if self.vel.y > -0.15:
                                    self.vel.y -= 0.015
                            elif self.pressed_up:
                                self.vel.y += 0.02

                            if self.pressed_left:
                                self.vel.x += 0.04
                            elif self.pressed_right:
                                self.vel.x -= 0.04
                        else:
                            self.level.projectiles.append(Projectile(Projectile.PROJECTILE_PLASMA, 10000, self.pos.x + 30, self.pos.y + 5, 1 + self.vel.x))

        else:
            if self.current_action_state == 'Plasma_State':
                self.action_states.on_event('fall')


        self.animation.animate()

    def get_distance_to_collider_below(self):
        """
        Returns the vertical distance to the closest line of all static_colliders and ramp_colliders
        that are directly below the player.

        Returns:
            float: The vertical distance to the closest collider below the player.
                  Returns float('inf') if no collider is found below the player.
        """
        player_x = self.shape.pos.x + self.shape.w / 2  # Player center x-coordinate
        player_bottom_y = self.shape.pos.y + self.shape.h  # Player bottom y-coordinate

        min_distance = float('inf')

        # Check static colliders
        for collider in self.level.static_colliders:
            # Only check colliders that are horizontally aligned with the player
            if collider.pos.x <= player_x <= collider.pos.x + collider.shape.w:
                # Only check colliders that are below the player
                if collider.pos.y > player_bottom_y:
                    distance = collider.pos.y - player_bottom_y
                    min_distance = min(min_distance, distance)

        # Check ramp colliders
        for collider in self.level.ramp_colliders:
            triangle = collider.shape
            vertices = [triangle.p1, triangle.p2, triangle.p3]

            # Find the horizontal range of the triangle
            min_x = min(v.x for v in vertices)
            max_x = max(v.x for v in vertices)

            # Only check triangles that are horizontally aligned with the player
            if min_x <= player_x <= max_x:
                # Find the y-coordinate on the triangle at the player's x-coordinate
                # We need to find the line segment that contains player_x
                for i in range(3):
                    p1 = vertices[i]
                    p2 = vertices[(i + 1) % 3]

                    # Check if player_x is between p1.x and p2.x
                    if (p1.x <= player_x <= p2.x) or (p2.x <= player_x <= p1.x):
                        # Calculate the y-coordinate on the line at player_x
                        if p1.x == p2.x:  # Vertical line
                            continue

                        # Linear interpolation to find y
                        t = (player_x - p1.x) / (p2.x - p1.x)
                        y = p1.y + t * (p2.y - p1.y)

                        # Only consider if the point is below the player
                        if y > player_bottom_y:
                            distance = y - player_bottom_y
                            min_distance = min(min_distance, distance)

        if min_distance == float('inf'):
            return 0
        else:
            return min_distance

    def get_ramp_friction(self, up, down):
        # For down-ramps, friction should be above 1 to create acceleration based on steepness
        if self.last_ramp_radians > 0:
            # The steeper the ramp, the higher the value (more acceleration)
            ramp_steepness = math.cos(self.last_ramp_radians)
            return 1.0 + ramp_steepness * up
        # For up-ramps, friction should be below 1 to create decelaration based on steepness
        elif self.last_ramp_radians < 0:
            # The steeper the ramp, the higher the value (more deceleration)
            ramp_steepness = math.cos(self.last_ramp_radians)
            return 1.0 - ramp_steepness * down
        else:
            return None

    def get_friction_factor(self, velocity, angle_rad, base_friction_factor=0.95, velocity_scaling=0.005, gravity_effect=0.001):
        """
        Calculates a dynamic friction factor based on velocity and surface angle.

        Args:
            velocity (float or int): The current velocity.
            angle_rad (float): The angle of the surface in radians.
                               Positive for upwards incline (slowing down).
                               Negative for downwards incline (speeding up).
            base_friction_factor (float, optional): The base friction value to use.
                                                    Defaults to 0.95.
            velocity_scaling (float, optional): A small constant to control how
                                                quickly friction increases with speed.
                                                Defaults to 0.005.
            gravity_effect (float, optional): A constant to scale the effect of the
                                              surface angle on the friction factor.
                                              Defaults to 0.001.

        Returns:
            float: The dynamically calculated friction factor.
        """
        velocity = abs(velocity)

        # Calculate the base friction effect, which increases with velocity.
        friction_difference = (1 - base_friction_factor) * (velocity * velocity_scaling)

        # Calculate the effect of the angle.
        # We use sin(angle_rad) because the component of gravity parallel to
        # the surface is proportional to the sine of the angle.
        # A positive angle (upwards) will result in a positive sin(angle),
        # which subtracts from the friction factor, causing more deceleration.
        # A negative angle (downwards) will result in a negative sin(angle),
        # which adds to the friction factor, causing more acceleration.
        angle_effect = math.sin(-angle_rad) * gravity_effect * velocity

        # Combine the effects. The angle effect is subtracted because
        # we want an upwards incline (positive angle) to reduce the friction factor,
        # causing a greater deceleration (new_velocity = velocity * friction_factor).
        dynamic_friction = 1 - friction_difference - angle_effect

        # Ensure the friction factor doesn't go below a reasonable value.
        return max(0, dynamic_friction)

    def get_friction(self):
        base_friction_factor = None
        if self.current_action_state == 'Move_State':
            return self.get_friction_factor(self.vel.x, self.last_ramp_radians, 0.95)

        elif self.current_action_state == 'Crouch_State':
            if self.pressed_right:
                return self.get_friction_factor(self.vel.x, self.last_ramp_radians, 0.975)
            else:
                return 0.998

        if base_friction_factor is not None:
            return self.get_friction_factor(self.vel.x, self.last_ramp_radians, base_friction_factor)

        # fixed deceleration friction
        if self.current_action_state == 'Decel_State':
            return 0.995

        # no friction for all other states like jump, fall, etc.
        return 1

    def movement(self):
        # pow() ensures friction to be applied independent of framerate
        friction_factor = pow(self.get_friction(), config.delta_time)
        self.vel.x *= friction_factor

        # Cap vertical velocity
        if self.vel.y > config.MAX_FALL_VEL:
            self.vel.y = config.MAX_FALL_VEL

        # Now call the movement and acceleration functions
        accelerate(self, self.acceleration, config.GRAVITY, config.MAX_OVERAL_VEL)

        self.move_player()

    def move_player(self):
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
        self.functional_collisions()

    def state_events(self):
        if any(self.current_action_state == state for state in ['Move_State', 'Decel_State', 'Idle_State', 'Crouch_State']):
            self.start_height = self.pos.y

        if self.vel.y == 0 and (not self.crouching or self.can_uncrouch):

            if self.pressed_right and not self.pressed_down:
                self.action_states.on_event('move')

            if self.vel.x > 0 and not self.pressed_right and not self.pressed_down and not self.current_action_state == 'Idle_State':
                self.action_states.on_event('decel')

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State' and not self.pressed_down:
                self.vel.x = 0
                self.action_states.on_event('idle')


        if self.crouching and self.vel.x < 0.03:
            self.vel.x = 0

        # allow braking
        elif self.pressed_left and not self.pressed_right and not self.current_action_state == 'Plasma_State':
            self.vel.x -= 0.01

        if self.current_action_state != 'Crouch_State' and self.pressed_down:
            self.action_states.on_event('crouch')

    def collider_collisions(self, dx, dy):
        other_collider = self.shape.check_collisions(self.level.static_colliders)

        if other_collider is None:
            return

        if self.current_action_state == 'Plasma_State':
         self.vel.x -= 0.1

        if dx > 0:
            if self.current_action_state == 'Move_State' and not self.pressed_down and not self.pressed_right and not self.pressed_left and not self.pressed_up:
                self.action_states.on_event('decel')
            self.pos.x = other_collider.pos.x - self.shape.w
            self.vel.x = 0
        elif dx < 0:
            if self.current_action_state == 'Move_State' and not self.pressed_down and not self.pressed_right and not self.pressed_left and not self.pressed_up:
                self.action_states.on_event('decel')
            self.pos.x = other_collider.pos.x + other_collider.shape.w
            self.vel.x = 0
        elif dy > 0:
            if self.current_action_state == 'Fall_State':
                self.ground_touch_time = pygame.time.get_ticks()
                self.ground_touch_pos = Vector2(self.pos.x, self.pos.y)
                self.action_states.on_event('decel')
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

        # Set the player state to falling
        self.action_states.on_event('fall')

    def ramp_collisions(self):

        ramp_collider = self.shape.check_triangle_top_sides_collision(self.level.ramp_colliders)

        if ramp_collider is None:
            # launch when leaving a ramp
            if self.last_ramp_radians < 0:
                self.add_ramp_momentum()

            # no ramp collision
            self.last_ramp_radians = 0
            return

        # Get the relevant ramp start and end points
        x0 = ramp_collider[0].x  # base start x
        y0 = ramp_collider[0].y  # base start y
        x1 = ramp_collider[1].x  # top of ramp x
        y1 = ramp_collider[1].y  # top of ramp y

        # Remember an angle for momentum when leaving the ramp
        next_rad = math.atan2(x1 - x0, y1 - y0)

        # launch when sliding over the peak of a two-sided ramp
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

        # Set player's feet to ramp surface
        self.shape.pos.y = y_on_ramp - self.shape.h

        self.vel.y = 0

        self.action_states.on_event('ramp')

    def item_collisions(self):
        for item in self.level.items:
            if item.picked_up:
                if item.stay and item.respawn_at is not None and pygame.time.get_ticks() > item.respawn_at:
                    item.picked_up = False
                    item.respawn_at = None
                continue
            if item.pos.x - 10 <= self.pos.x + self.shape.w / 2 <= item.pos.x + 10 and item.pos.y - 10 <= self.pos.y + self.shape.h / 2 <= item.pos.y + 10:
                sounds.pickup.play()
                self.active_weapon = item.item_type
                if item.item_type == 'rocket':
                    self.has_rocket = True
                    self.rocket_ammo += item.ammo
                elif item.item_type == 'plasma':
                    self.has_plasma = True
                    self.plasma_ammo += item.ammo
                item.picked_up = True
                if item.stay:
                    item.respawn_at = pygame.time.get_ticks() + 3000
                self.animation.set_active_weapon()#

    def functional_collisions(self):
        portal = self.shape.check_center_collisions(self.level.portals, 20, 10)
        if portal is not None:
            portal.teleport(self)

        jump_pad = self.shape.check_center_collisions(self.level.jump_pads, 24, -30)
        if jump_pad is not None:
            jump_pad.jump(self)

        death = self.shape.check_collisions(self.level.death_colliders)
        if death is not None:
            self.player_states.on_event('dead')

    def walljump_collisions(self):
        wall_collider = self.shape.check_collisions(self.level.wall_colliders)

        return wall_collider is not None

    def plasma_climb_collisions(self):
        wall_collider = self.shape.check_center_collisions(self.level.wall_colliders)

        return wall_collider is not None

    def check_can_uncrouch(self):
        stand_rect = copy.copy(self.shape)
        stand_rect.pos = copy.copy(self.shape.pos)
        stand_rect.pos.y -= (HEIGHT - self.shape.h)
        stand_rect.h = HEIGHT
        for collider in self.level.static_colliders:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.shape.w >= 100:
                if stand_rect.overlaps(collider.shape):
                    return False

        return True

    def add_jump_velocity(self):
        ground_diff = pygame.time.get_ticks() - self.ground_touch_time
        diff = max(10, self.jump_diff, ground_diff)
        boost = round(1.75 / diff, 3)

        # enhance jump boost when not running
        if not self.pressed_right:
            boost *= 1.33

        self.acceleration = 0
        self.last_boost = round(boost * 1000)

        if self.vel.x < 0.2:
            self.vel.x = 0.15

        self.vel.y = config.JUMP_VELOCITY

        # Fix to allow jumping while colliding with a ramp
        if self.last_ramp_radians != 0:
            y_offset = abs(math.cos(self.last_ramp_radians) * (self.vel.x + 0.1) * 100)
            self.pos.y -= y_offset  # Apply the offset
            self.last_ramp_radians = 0

        self.vel.x += boost

    def add_jump_velocity_alt(self):

        #ground_diff = pygame.time.get_ticks() - self.ground_touch_time
        early_distance = 0 if self.jump_action_distance is None else self.jump_action_distance
        late_distance = 0 if (early_distance is not None and early_distance > 0) or self.ground_touch_pos is None else math.sqrt((self.pos.x - self.ground_touch_pos.x) ** 2 + (self.pos.y - self.ground_touch_pos.y) ** 2)

        print(f'late: {late_distance}, early: {early_distance}')

        self.ground_touch_pos = None
        self.jump_action_distance = 0

        boost = 0
        if early_distance + late_distance != 0:
            min_boost = 0.01
            max_boost = 1
            max_distance = 32
            curve = 3

            boost = max(0.0, min_boost + (max_boost - min_boost) * max(0.0, 1 - (late_distance + early_distance) / max_distance) ** curve) / 5

            if early_distance > 0:
                self.jumped_early = early_distance
                self.jumped_late = None
            elif late_distance > 0:
                self.jumped_early = None
                self.jumped_late = late_distance

            # enhance jump boost when not running
            if not self.pressed_right:
                boost *= 1.337

        self.acceleration = 0
        self.last_boost = round(boost * 1000)

        if self.vel.x < 0.2:
            self.vel.x = 0.15

        y_boost = config.JUMP_VELOCITY

        # Fix to allow jumping while colliding with a ramp
        if self.last_ramp_radians != 0:
            cos = math.cos(self.last_ramp_radians)
            #sin = math.sin(self.last_ramp_radians)
            #print(f'cos: {cos}, sin: {sin}')
            y_offset = abs(cos * (self.vel.x + 0.1) * 75)
            self.pos.y -= y_offset  # Apply the offset
            self.last_ramp_radians = 0


        self.vel.x += boost
        self.vel.y += y_boost

    def add_rocket_velocity(self, distance, angle_rad):
        if distance is not None:
            #if distance > 150:
            #    return

            vel_magnitude = 1 / (1 + 0.04 * distance)

            # Calculate x and y components of velocity
            vel_x =  vel_magnitude * math.cos(angle_rad)
            vel_y = vel_magnitude * math.sin(angle_rad)

            #print("distance", distance, "vel_mag", vel_magnitude, "vel_x", vel_x, "vel_y", vel_y)

            # add additional momentum when jumping from a ramp
            #if self.last_ramp_radians > 0:
            #    ramp_boost = 0.225 * (self.vel.x * math.sin(self.last_ramp_radians) + self.vel.x * math.cos(self.last_ramp_radians))
            #    vel_y -= ramp_boost
            #    self.last_ramp_radians = 0
            
            # Apply velocity components
            self.vel.x += vel_x
            self.vel.y += vel_y

            self.action_states.on_event('decel')

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
            print(__class__, pygame.time.get_ticks())
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
            elif event == 'ramp':
                return Player.Move_State()
            return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())

            owner_object.last_walljump = 0
            owner_object.animation.begin_jump()

            if random.choice([True, False]):
                sounds.jump1.play()
            else:
                sounds.jump2.play()

            owner_object.add_jump_velocity_alt()

        def update(self, owner_object):
            if owner_object.pressed_right and owner_object.vel.x < 0.1:
                owner_object.acceleration = 0.0005

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
            print(__class__, pygame.time.get_ticks())

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
            print(__class__, pygame.time.get_ticks())
            owner_object.animation.reset_anim()

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
            print(__class__, pygame.time.get_ticks())
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
            print(__class__, pygame.time.get_ticks())
            owner_object.last_ramp_radians = 0
            # allows moving forward when stuck in front of a wall
            #if owner_object.vel.x == 0:
            #    owner_object.vel.x = 0.02

        def update(self, owner_object):
            owner_object.acceleration = 0
            if owner_object.pressed_right and owner_object.vel.x < 0.1:
                owner_object.acceleration = 0.0005

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
            print(__class__, pygame.time.get_ticks())
            return

        def update(self, owner_object):
            owner_object.acceleration = config.PLAYER_ACCELERATION

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
            print(__class__, pygame.time.get_ticks())
            owner_object.acceleration = 0

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
            print(__class__, pygame.time.get_ticks())

            owner_object.pos.y += (HEIGHT - CROUCH_HEIGHT)
            owner_object.shape.h = CROUCH_HEIGHT
            owner_object.crouching = True

        def update(self, owner_object):
            owner_object.acceleration = 0
            if owner_object.vel.x == 0 and owner_object.pressed_right and owner_object.lifted_right:
                owner_object.vel.x = 0.1
                owner_object.lifted_right = False

        def on_exit(self, owner_object):
            owner_object.pos.y -= (HEIGHT - CROUCH_HEIGHT)
            owner_object.start_height = owner_object.pos.y
            owner_object.shape.h = HEIGHT
            owner_object.crouching = False


    class Dead_Player(State):
        """State when player is dead"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            else:
                return self

        def on_enter(self, owner_object):
            print(__class__, pygame.time.get_ticks())
            #owner_object.freeze_movement = True
            owner_object.freeze_input = True
            pygame.mixer.music.stop()
            sounds.death.play()

        def update(self, owner_object):
            self.death_timer += config.delta_time
            owner_object.vel.x = 0
            owner_object.vel.y = 0.1
            if self.death_timer > 300 * config.delta_time:
                self.death_timer = float("-inf")
                owner_object.level.reset()
                owner_object.reset()
                owner_object.action_states.on_event('idle')


WIDTH=32
HEIGHT=42
CROUCH_HEIGHT=32

P_SCALE    = 0.5
P_WIDTH    = 128
P_HEIGHT   = 128
P_WIDTH_S  = P_WIDTH  * P_SCALE
P_HEIGHT_S = P_HEIGHT * P_SCALE

DEAD_PLAYER   = (0    * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
IDLE          = (128  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
IDLE_PLASMA   = (128  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
IDLE_ROCKET   = (128  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
CROUCH        = (0    * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
CROUCH_PLASMA = (0    * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
CROUCH_ROCKET = (0    * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
SLIDE         = (0    * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
SLIDE_PLASMA  = (256  * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
SLIDE_ROCKET  = (128  * P_SCALE, 1280 * P_SCALE, P_WIDTH_S, P_HEIGHT_S)
PLASMA_CLIMB  = (640  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S)

RUN = [
   (0    * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 0    * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (0    * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 128  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

RUN_PLASMA = [
   (0    * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 384  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (0    * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 512  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

RUN_ROCKET = [
   (0    * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 768  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (0    * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (640  * P_SCALE, 896  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

WALLJUMP = [
   (256  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 256  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

WALLJUMP_PLASMA = [
   (256  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

WALLJUMP_ROCKET = [
   (256  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (384  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (512  * P_SCALE, 1024 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

SHOOT_PLASMA = [
   (640  * P_SCALE, 640  * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]

SHOOT_ROCKET = [
   (0    * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (128  * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
   (256  * P_SCALE, 1152 * P_SCALE, P_WIDTH_S, P_HEIGHT_S),
]
import copy, math, pygame, random, os

from src.Animation import Animation
from src.Decal import Decal
from src.Entity import Entity
from src.Rectangle import Rectangle
from src.StateMachine import StateMachine
from src.State import State
from src.Vector2 import Vector2
from src.utils import accelerate
from src.Projectile import Projectile
from src import sounds, config


class Player(Entity):
    def __init__(self, game):

        self.game = game

        self.CROUCH_OFF = 1  # reduce "physical" crouch height from sprite height
        self.CROUCH_HEIGHT = 32 - self.CROUCH_OFF

        self.P_SCALE = 0.5
        self.P_WIDTH = 128
        self.P_HEIGHT = 128
        self.P_WIDTH_S = self.P_WIDTH * self.P_SCALE
        self.P_HEIGHT_S = self.P_HEIGHT * self.P_SCALE

        self.WIDTH = 32
        self.HEIGHT = 42

        scale =  game.settings.get_scale()

        super(Player, self).__init__(Vector2(0, 0), Rectangle(Vector2(0, 0), self.WIDTH * scale, self.HEIGHT * scale))
        self.distance_to_ground = 0
        self.last_boost = 0
        self.acceleration = 0
        self.map = None
        self.last_walljump = 0
        self.last_ramp_radians = 0
        self.animation = Animation(self)
        self.action_states = StateMachine(self.Idle_State(), self)
        self.last_velocity = 0
        self.pressed_up = False
        self.pressed_left = False
        self.pressed_right = False
        self.released_right = False
        self.pressed_jump = False
        self.released_jump = True
        self.pressed_shoot = False
        self.pressed_down = False
        self.crouching = False

        self.freeze_movement = False
        self.freeze_input = False
        self.can_uncrouch = False
        self.flip_sprites = False
        self.jump_diff = float("inf")

        self.start_height = 0
        self.jump_pressed_at = None
        self.jump_action_distance = None
        self.jump_timing = float("-inf")
        self.ground_touch_pos = Vector2(0, 0)

        self.has_rocket = False
        self.rocket_ammo = 0
        self.last_rocket_time = 0

        self.has_plasma = False
        self.plasma_ammo = 0
        self.last_plasma_time = 0

        self.active_weapon = None
        self.last_weapon_switch = 0

        self.is_plasma_climbing = False
        self.plasma_cooldown = 92
        self.plasma_timer = self.plasma_cooldown
        self.rocket_cooldown = 1337
        self.rocket_timer = self.rocket_cooldown

        self.height = self.animation.sprite_sheet.get_height() * self.P_SCALE

    def reset(self):
        self.distance_to_ground = 0
        self.last_boost = 0
        self.acceleration = 0
        self.last_walljump = 0
        self.last_ramp_radians = 0
        self.animation = Animation(self)
        self.action_states = StateMachine(self.Idle_State(), self)
        self.last_velocity = 0
        self.pressed_up = False
        self.pressed_left = False
        self.pressed_right = False
        self.released_right = False
        self.pressed_jump = False
        self.released_jump = True
        self.pressed_shoot = False
        self.pressed_down = False
        self.crouching = False

        self.freeze_movement = False
        self.freeze_input = False
        self.can_uncrouch = False
        self.flip_sprites = False
        self.jump_diff = float("inf")

        self.start_height = 0
        self.jump_pressed_at = None
        self.jump_action_distance = None
        self.jump_timing = float("-inf")
        self.ground_touch_pos = Vector2(0, 0)

        self.has_rocket = False
        self.rocket_ammo = 0
        self.last_rocket_time = 0

        self.has_plasma = False
        self.plasma_ammo = 0
        self.last_plasma_time = 0

        self.active_weapon = None
        self.last_weapon_switch = 0

        self.is_plasma_climbing = False
        self.plasma_cooldown = 92
        self.plasma_timer = self.plasma_cooldown
        self.rocket_cooldown = 1337
        self.rocket_timer = self.rocket_cooldown
        self.vel = Vector2(0, 0)
        self.action_states = StateMachine(self.Fall_State(), self)
        self.shape.pos.x = self.map.player_start.x
        self.shape.pos.y = self.map.player_start.y

        #print("player reset")

    def set_map(self, map):
        self.map = map
        self.shape.pos = map.player_start

    def __getattr__(self, name):
        if name == 'current_action_state':
            return self.action_states.get_state()
        elif name == 'pos':
            return self.shape.pos
        return object.__getattribute__(self, name)

    def draw(self):

        scale = self.game.settings.get_scale()

        #if camera.contains(self.rect):
        view_pos_sprite = self.game.camera.to_view_space(
            Vector2(
                self.shape.pos.x - 16 * scale,
                self.shape.pos.y - (32 * scale if self.crouching else 21 * scale)
            )
        )

        if self.last_ramp_radians == 0:
            self.game.surface.blit(self.animation.current_sprite, (view_pos_sprite.x, view_pos_sprite.y))
        else:
            # 2. Rotate the sprite
            rotated_sprite = pygame.transform.rotate(self.animation.current_sprite, math.degrees(self.last_ramp_radians))

            # 3. Center the rotated sprite on the position
            rect = rotated_sprite.get_rect(center=(view_pos_sprite.x + self.animation.current_sprite.get_width() // 2, view_pos_sprite.y + self.animation.current_sprite.get_height() // 2))

            # 4. Blit the rotated sprite
            self.game.surface.blit(rotated_sprite, rect.topleft)

        # debug draw rect around player
        #self.shape.draw(self.game.surface, self.game.camera, 1)

    def input_wall_jump(self, v):
        if v:
            if pygame.time.get_ticks() - self.last_walljump > 1000 and self.walljump_collisions():
                self.last_walljump = pygame.time.get_ticks()
                self.action_states.on_event('walljump')

    def input_right(self, v):
        self.pressed_right = v
        if v and self.vel.x == 0 and self.current_action_state == 'Crouch_State':
            self.vel.x = 0.1 * self.game.settings.get_scale()

    def input_down(self, v):
        self.pressed_down = v
        if v:
            self.action_states.on_event('crouch')

    def input_up(self, v):
        self.pressed_up = v

    def input_jump(self, v):
        self.pressed_jump = v
        if v:
            self.released_jump = False
            if self.jump_pressed_at is None:
                self.jump_pressed_at = pygame.time.get_ticks()
                if not self.jump_action_distance and not self.last_ramp_radians:
                    self.jump_action_distance = self.distance_to_ground / self.game.settings.get_scale()
        else:
            self.jump_pressed_at = None
            self.pressed_jump = False
            self.released_jump = True

    def input_switch_weapon(self, v):
        if v and self.last_weapon_switch + 666 < pygame.time.get_ticks():
            if self.active_weapon == 'rocket' and self.has_plasma:
                self.active_weapon = 'plasma'
            elif self.active_weapon == 'plasma' and self.has_rocket:
                self.active_weapon = 'rocket'
            self.animation.set_active_weapon()
            self.last_weapon_switch = pygame.time.get_ticks()

    def update(self):

        self.can_uncrouch = self.crouching and self.check_can_uncrouch()
        self.distance_to_ground = self.get_distance_to_collider_below()

        self.plasma_timer = min(self.plasma_timer + config.delta_time, self.plasma_cooldown)
        self.rocket_timer = min(self.rocket_timer + config.delta_time, self.rocket_cooldown)

        # Trigger falling
        if self.vel.y > 0 and self.current_action_state != 'Plasma_State':
            self.action_states.on_event('fall')

        if self.pressed_jump and (not self.crouching or self.can_uncrouch):
            self.jump_diff = pygame.time.get_ticks() - self.jump_pressed_at
            if self.jump_diff < 333:
                self.action_states.on_event('jump')

        if not self.freeze_movement:
            self.state_events()
            self.action_states.update()
            self.movement()

        if self.pressed_shoot:
            self.shoot()

        else:
            if self.current_action_state == 'Plasma_State':
                self.action_states.on_event('fall')

        self.animation.animate()

    def shoot(self):
        if self.active_weapon == 'rocket':
            self.shoot_rocket()
        elif self.active_weapon == 'plasma':
            self.shoot_plasma()

    def shoot_rocket(self):
        scale = self.game.settings.get_scale()
        if self.rocket_timer >= self.rocket_cooldown:
            self.rocket_timer -= self.rocket_cooldown
            if self.rocket_ammo <= 0:
                sounds.weapon_empty.play()
            else:
                self.rocket_ammo -= 1
                sounds.rocket_launch.play()
                channel = sounds.rocket_fly.play(loops=-1)
                if self.pressed_down:
                    self.map.projectiles.append(Projectile('rocket', 1337000, self.pos.x + config.ROCKET_DOWN_OFFSET_X * scale, self.pos.y + config.ROCKET_DOWN_OFFSET_Y * scale, self.vel.x, self.vel.y + 1 * scale, 0.7 * scale, -0.0015 * scale, channel, ['ramp', 'static']))
                else:
                    self.map.projectiles.append(Projectile('rocket', 1337000, self.pos.x + 30 * scale, self.pos.y + 5 * scale, self.vel.x + 1 * scale, 0, 1.1 * scale, -0.00075 * scale, channel, ['ramp', 'static']))

    def shoot_plasma(self):
        scale = self.game.settings.get_scale()
        if self.plasma_timer >= self.plasma_cooldown:
            self.plasma_timer -= self.plasma_cooldown
            if self.plasma_ammo <= 0:
                sounds.weapon_empty.play()
            else:
                sounds.plasma.play()
                self.plasma_ammo -= 1
                if (self.pressed_down or self.pressed_left or self.pressed_up or self.pressed_right) and self.plasma_climb_collisions():
                    if self.pressed_left:
                        decal_offset = 5
                    elif self.pressed_right:
                        decal_offset = 30
                    else:
                        decal_offset = 15

                    self.action_states.on_event('plasma')
                    self.map.decals.append(Decal('plasma', 1000, self.pos.x + decal_offset * scale, self.pos.y + 5 * scale, center=True, fade_out=True))

                    if self.pressed_down:
                        if self.pressed_left or self.pressed_right:
                            self.vel.y -= 0.07 * scale
                        else:
                            self.vel.y -= 0.103 * scale
                        # add some extra velocity if climbing very slow
                        if self.vel.y > -0.15 * scale:
                            self.vel.y -= 0.015 * scale
                    elif self.pressed_up:
                        self.vel.y += 0.02 * scale

                    if self.pressed_left:
                        self.vel.x += 0.04 * scale
                    elif self.pressed_right:
                        self.vel.x -= 0.04 * scale
                else:
                    self.map.projectiles.append(Projectile('plasma', 10000, self.pos.x + 30 * scale, self.pos.y + 2 * scale, 1 + self.vel.x))

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
        for collider in self.map.static_colliders:
            # Only check colliders that are horizontally aligned with the player
            if collider.pos.x <= player_x <= collider.pos.x + collider.shape.w:
                # Only check colliders that are below the player
                if collider.pos.y > player_bottom_y:
                    distance = collider.pos.y - player_bottom_y
                    if distance < min_distance:
                        min_distance = distance


        # Check ramp colliders
        for collider in self.map.ramp_colliders:
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
                            if distance < min_distance:
                                min_distance = distance

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

    def get_friction_factor(self, velocity, angle_rad, gravity_effect, base_factor, velocity_scaling):
        """
        Calculates a dynamic friction factor based on velocity and surface angle.

        Args:
            velocity (float or int): The current velocity.
            angle_rad (float): The angle of the surface in radians.
                               Positive for upwards incline (slowing down).
                               Negative for downwards incline (speeding up).
            base_factor (float, optional): The base friction value to use.
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
        friction_difference = (1 - base_factor) * (velocity * velocity_scaling)

        # Calculate the effect of the angle.
        # We use sin(angle_rad) because the component of gravity parallel to
        # the surface is proportional to the sine of the angle.
        # A positive angle (upwards) will result in a positive sin(angle),
        # which subtracts from the friction factor, causing more deceleration.
        # A negative angle (downwards) will result in a negative sin(angle),
        # which adds to the friction factor, causing more acceleration.
        angle_effect = math.sin(angle_rad) * gravity_effect * velocity

        # Combine the effects. The angle effect is subtracted because
        # we want an upwards incline (positive angle) to reduce the friction factor,
        # causing a greater deceleration (new_velocity = velocity * friction_factor).
        dynamic_friction = 1 - friction_difference - angle_effect

        # Ensure the friction factor doesn't go below a reasonable value.
        return max(0, dynamic_friction)

    def get_friction(self):

        gravity_effect = config.FRICTION_GRAVITY_EFFECT
        base_factor = config.FRICTION_BASE_FACTOR
        velocity_scaling = config.FRICTION_VELOCITY_SCALING

        # no friction while mid-air
        if self.current_action_state == 'Jump_State' or self.current_action_state == 'Fall_State':
            base_factor = 1

        elif self.current_action_state == 'Decel_State':
            return 0.998

        elif self.current_action_state == 'Crouch_State':
            # When crouch-sliding, adjust gravity effect on friction
            if self.pressed_right:
                # to have less deceleration for up-ramps
                if self.last_ramp_radians > 0:
                    gravity_effect = 0.0007
                # and more acceleration for down-ramps
                elif self.last_ramp_radians < 0:
                    gravity_effect = 0.005
                else:
                    base_factor = 0.91
            # normal crouching decelerates quickly
            else:
                return 0.998

        return self.get_friction_factor(self.vel.x, self.last_ramp_radians, gravity_effect / self.game.settings.get_scale(), base_factor, velocity_scaling / self.game.settings.get_scale())

    def movement(self):
        # pow() ensures friction to be applied independent of framerate
        friction_factor = pow(self.get_friction(), config.delta_time)
        self.vel.x *= friction_factor

        scale = self.game.settings.get_scale()
        # Cap vertical velocity
        if self.vel.y > config.MAX_FALL_VEL * scale:
            self.vel.y = config.MAX_FALL_VEL * scale

        # Now call the movement and acceleration functions
        scale = self.game.settings.get_scale()
        accelerate(self, self.acceleration * scale, config.GRAVITY * scale, config.MAX_OVERAL_VEL * scale)

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


    def collider_collisions(self, dx, dy):

        # when currently colliding with a ramp, ignore static (rect) colliders
        # fixes weird warping, when running from a static collider onto a down-ramp
        if self.last_ramp_radians != 0:
            return

        other_collider = self.shape.check_collisions(self.map.static_colliders)

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
                self.ground_touch_pos = Vector2(self.pos.x, self.pos.y)
                self.action_states.on_event('decel')
            self.pos.y = other_collider.pos.y - self.shape.h
            self.vel.y = 0
        elif dy < 0:
            self.action_states.on_event('fall')
            self.pos.y = other_collider.pos.y + other_collider.shape.h
            self.vel.y = config.BOUNCE_VEL

    def launch_from_ramp(self):
        self.vel.y = -self.vel.x * math.tan(self.last_ramp_radians)
        self.action_states.on_event('fall')

    def ramp_collisions(self):

        # Get the line of the ramp we collided with (up or down)
        ramp_collider = self.shape.check_triangle_top_sides_collision(self.map.ramp_colliders)

        if ramp_collider is None:
            # launch when leaving a ramp
            if self.last_ramp_radians > 0:
                self.launch_from_ramp()

            # no ramp collision
            self.last_ramp_radians = 0
            return

        self.game.camera.stop_settling()

        # unordered points of the ramp line
        point0 = ramp_collider[0]
        point1 = ramp_collider[1]

        # determine which is the start and which is the end point
        if point0.x < point1.x:
            # point0 ist der left (start) point
            x_start, y_start = point0.x, point0.y
            x_end, y_end = point1.x, point1.y
        else:
            # point1 ist der left (start) point
            x_start, y_start = point1.x, point1.y
            x_end, y_end = point0.x, point0.y

        # get the angle from proper start and end points
        dy = y_end - y_start
        dx = x_end - x_start

        next_rad = -math.atan2(dy, dx)

        # launch when sliding over the peak of a two-sided ramp
        if self.last_ramp_radians > 0 > next_rad:
            self.launch_from_ramp()
            return

        # Remember for launching when leaving the ramp
        self.last_ramp_radians = next_rad

        # Calculate horizontal progress (progress ratio) across the ramp
        x = self.shape.pos.x + self.shape.w / 2  # Player center x
        progress = max(0, min(1, (x - x_start) / dx))  # Clamp to [0,1]

        # Linear interpolation from base y to top y
        y_on_ramp = (1 - progress) * y_start + progress * y_end

        # Set player's feet to ramp surface
        self.shape.pos.y = y_on_ramp - self.shape.h

        if not self.ground_touch_pos:
            self.ground_touch_pos = Vector2(self.pos.x, self.pos.y)

        self.vel.y = 0

        self.action_states.on_event('ramp')

    def item_collisions(self):
        for item in self.map.items:
            if item.picked_up:
                if item.stay and item.respawn_at is not None and pygame.time.get_ticks() > item.respawn_at:
                    item.picked_up = False
                    item.respawn_at = None
                continue
            if item.pos.x - item.width <= self.pos.x + self.shape.w / 2 <= item.pos.x + item.width and item.pos.y - item.height <= self.pos.y + self.shape.h / 2 <= item.pos.y + item.height:
                sounds.pickup.play()
                self.active_weapon = item.type
                if item.type == 'rocket':
                    self.has_rocket = True
                    self.rocket_ammo += item.ammo
                elif item.type == 'plasma':
                    self.has_plasma = True
                    self.plasma_ammo += item.ammo
                item.picked_up = True
                if item.stay:
                    item.respawn_at = pygame.time.get_ticks() + 3000
                self.animation.set_active_weapon()#

    def functional_collisions(self):

        scale = self.game.settings.get_scale()

        portal = self.shape.check_center_collisions(self.map.portals, 20 * scale, 10 * scale)
        if portal is not None:
            portal.teleport(self)

        jump_pad = self.shape.check_center_collisions(self.map.jump_pads, 10 * scale, -20 * scale)
        if jump_pad is not None:
            jump_pad.jump(self)

        death = self.shape.check_collisions(self.map.death_colliders)
        if death is not None:
            self.action_states.on_event('dead')

        if self.map.timer == 0 and self.map.start_line is not None:
            start_line = self.shape.check_collisions([self.map.start_line])
            if start_line is not None:
                self.map.start_timer()

        if self.map.timer != 0 and self.map.finish_line is not None:
            finish_line = self.shape.check_collisions([self.map.finish_line])
            if finish_line is not None:
                self.map.stop_timer()

    def walljump_collisions(self):
        wall_collider = self.shape.check_collisions(self.map.wall_colliders)

        return wall_collider is not None

    def plasma_climb_collisions(self):
        wall_collider = self.shape.check_center_collisions(self.map.wall_colliders)

        return wall_collider is not None

    def check_can_uncrouch(self):
        height = self.HEIGHT * self.game.settings.get_scale()
        stand_rect = copy.copy(self.shape)
        stand_rect.pos = copy.copy(self.shape.pos)
        stand_rect.pos.y -= (height - self.shape.h)
        stand_rect.h = height
        for collider in self.map.static_colliders:
            if collider.shape.overlaps(stand_rect):
                return False

        return True

    def calculate_distance(self, pos1, pos2):
        """Calculates the Euclidean distance between two points."""
        if pos1 is None or pos2 is None:
            return 0
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

    def add_jump_velocity(self):

        scale = self.game.settings.get_scale()

        # Determine if the jump was early or late
        if self.jump_action_distance is not None and self.jump_action_distance != float("inf"):
            self.jump_timing = -self.jump_action_distance
        else:
            late_jump_distance = None if self.ground_touch_pos is None else self.calculate_distance(self.pos, self.ground_touch_pos)
            if late_jump_distance is not None and late_jump_distance != float("inf"):
                self.jump_timing = late_jump_distance / scale

        # Reset jump tracking variables for the next jump
        self.ground_touch_pos = None
        self.jump_action_distance = None

        boost = 0
        if not self.pressed_down and not self.pressed_up and self.jump_timing:
            min_boost = 0.01
            max_boost = 1
            max_distance = 32
            curve = 3

            boost = max(0.0, min_boost + (max_boost - min_boost) * max(0.0, 1 - (abs(self.jump_timing)) / max_distance) ** curve) / 5

            # enhance jump boost when not running
            if not self.pressed_right:
                boost *= 1.337

            if self.vel.x < 0.2:
                self.vel.x = 0.15

        self.acceleration = 0
        self.last_boost = round(boost * 1000)

        y_boost = config.JUMP_VELOCITY

        # Fix jumping while colliding with a ramp by warping the player upwards
        # depending on the ramp angle and player speed.
        if self.last_ramp_radians > 0:
            eps = 10  # adjust so it's not infinite at 0
            self.pos.y -= 400 * scale * (1 / (abs(self.vel.x) + eps)) * math.tan(self.last_ramp_radians)
            self.last_ramp_radians = 0
        elif self.last_ramp_radians < 0:
            self.pos.y -= 3 * scale
            self.last_ramp_radians = 0


        self.vel.x += boost * scale
        self.vel.y += y_boost * scale

    def add_rocket_velocity(self, distance, angle_rad):
        if distance is not None:
            scale = self.game.settings.get_scale()
            #print(f'distance: {distance}, angle: {angle_rad}')
            vel_magnitude = 1 * scale / (1 * scale + 0.01 * scale * (distance / scale) ** 1.33)

            # Calculate x and y components of velocity
            vel_x = vel_magnitude * math.cos(angle_rad)
            vel_y = vel_magnitude * math.sin(angle_rad)

            #print("distance", distance, "angle", math.degrees(angle_rad), "vel_mag", vel_magnitude, "vel_x", vel_x, "vel_y", vel_y)

            # add additional momentum when jumping from a ramp
            #if self.last_ramp_radians > 0:
            #    ramp_boost = 0.225 * (self.vel.x * math.sin(self.last_ramp_radians) + self.vel.x * math.cos(self.last_ramp_radians))
            #    vel_y -= ramp_boost
            #    self.last_ramp_radians = 0
            
            # Apply velocity components

            self.vel.x += vel_x * scale
            self.vel.y += vel_y * scale

            self.action_states.on_event('fall')

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
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            return

        def update(self, owner_object):
            if owner_object.pressed_down:
                owner_object.action_states.on_event('crouch')

    class Jump_State(State):
        """State when jumping when spacebar input affects velocity"""

        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'ramp':
                return Player.Move_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            owner_object.last_walljump = 0
            owner_object.animation.begin_jump()

            if random.choice([True, False]):
                sounds.jump1.play()
            else:
                sounds.jump2.play()

            owner_object.game.camera.stop_settling()
            owner_object.game.map.decals.append(Decal(f'dash{random.choice([1, 2])}', 666, owner_object.pos.x, owner_object.pos.y + owner_object.shape.h, bottom=True, fade_out=True))
            owner_object.add_jump_velocity()

        def update(self, owner_object):
            scale = owner_object.game.settings.get_scale()
            if owner_object.pressed_right and owner_object.vel.x < 0.05 * scale:
                owner_object.acceleration = 0.0001 * scale

    class Walljump_State(State):
        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())

            if random.choice([True, False]):
                sounds.walljump1.play()
            else:
                sounds.walljump2.play()

            owner_object.vel.y = config.WALLJUMP_VELOCITY * owner_object.game.settings.get_scale()
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
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            owner_object.animation.reset_anim()

        def update(self, owner_object):
            if not owner_object.pressed_left and not owner_object.pressed_right and not owner_object.pressed_up and not owner_object.pressed_down:
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
            elif event == 'crouch':
                return Player.Crouch_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'ramp':
                return Player.Move_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            owner_object.last_ramp_radians = 0
            # allows moving forward when stuck in front of a wall
            #if owner_object.vel.x == 0:
            #    owner_object.vel.x = 0.02

        def update(self, owner_object):
            scale = owner_object.game.settings.get_scale()
            owner_object.acceleration = 0
            if owner_object.pressed_right and owner_object.vel.x < 0.1 * scale:
                owner_object.acceleration = 0.0005 * scale

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
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            return

        def update(self, owner_object):
            owner_object.acceleration = config.PLAYER_ACCELERATION
            if owner_object.pressed_down:
                owner_object.action_states.on_event('crouch')

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
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            owner_object.acceleration = 0

        def update(self, owner_object):
            if owner_object.pressed_down:
                owner_object.action_states.on_event('crouch')

    class Crouch_State(State):
        """State when player is crouching"""
        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'fall':
                return Player.Fall_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'idle':
                return Player.Idle_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            scale = owner_object.game.settings.get_scale()
            owner_object.pos.y += (owner_object.HEIGHT * scale - owner_object.CROUCH_HEIGHT * scale)
            owner_object.shape.h = owner_object.CROUCH_HEIGHT * scale
            owner_object.crouching = True

        def update(self, owner_object):
            owner_object.acceleration = 0

        def on_exit(self, owner_object):
            scale = owner_object.game.settings.get_scale()
            owner_object.pos.y -= (owner_object.HEIGHT * scale - owner_object.CROUCH_HEIGHT* scale)
            owner_object.start_height = owner_object.pos.y
            owner_object.shape.h = owner_object.HEIGHT* scale
            owner_object.crouching = False


    class Dead_State(State):
        """State when player is dead"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object):
            #print(__class__, pygame.time.get_ticks())
            #owner_object.freeze_movement = True
            owner_object.freeze_input = True
            sounds.death.play()

        def update(self, owner_object):
            self.death_timer += config.delta_time
            owner_object.vel.x = 0
            owner_object.vel.y = 0.1
            if self.death_timer > 300 * config.delta_time:
                self.death_timer = float("-inf")
                owner_object.game.map.reset()
                owner_object.reset()
                owner_object.action_states.on_event('idle')
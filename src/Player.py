import math, pygame, random, os
from src.Decal import Decal
from src.Rectangle import Rectangle
from src.SpriteAnim import SpriteAnim
from src.SpriteSheet import SpriteSheet
from src.StateMachine import StateMachine
from src.State import State
from src.Vector2 import Vector2
from src.Projectile import Projectile
from src import sounds, config

class Player(Rectangle):
    def __init__(self, game):
        super(Player, self).__init__()

        self.vel = Vector2(0, 0)
        self.game = game
        self.direction = 1
        self.visible_direction = 1
        self.anim = None
        self.distance_to_ground = 0
        self.last_boost = 0
        self.last_boost_time = None
        self.num_boost_ghosts = None
        self.boost_blur_elapsed = 0.0
        self.acceleration = 0
        self.map = None
        self.last_walljump = 0
        self.last_ramp_radians = 0
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
        self.was_flipped = False
        self.freeze_movement = False
        self.freeze_input = False
        self.can_uncrouch = False
        self.flip_sprites = False
        self.jump_diff = float("inf")
        self.jump_pressed_at = None
        self.jump_action_distance = None
        self.jump_timing = float("-inf")
        self.ground_touch_pos = None
        self.ground_collider = None
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
        self.previous_frame_height = 0

        self.action_states = StateMachine(self.Idle_State(), self)
        self.load_animations()

    def load_animations(self):
        scale = self.game.settings.get_scale()
        player_scale = scale/2
        crouch=(25 * player_scale, 0, 0, 0)

        sheet = SpriteSheet(os.path.join(config.assets_folder, 'graphics', 'player.png'), 128, 128, padding=(39, 2, 0, 10), scale=player_scale)
        self.anim = SpriteAnim(sheet)

        run_no_weapon = {'left': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)], 'right': [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]}
        self.anim.add('idle', 'no_weapon', [(2, 1)], loop=False)
        self.anim.add('dead', 'no_weapon', [(10, 5)], loop=False)
        self.anim.add('run', 'no_weapon', run_no_weapon, loop=True)
        self.anim.add('jump', 'no_weapon', run_no_weapon, loop=False)
        self.anim.add('wall_jump', 'no_weapon', [(2, 1), (2, 2), (2, 3), (2, 4)], loop=False, fps=12)
        self.anim.add('crouch', 'no_weapon', [(2, 0)], loop=False, padding=crouch)
        self.anim.add('slide', 'no_weapon', [(10, 0)], loop=False, padding=crouch)

        run_plasma = {'left': [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)], 'right': [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5)]}
        self.anim.add('idle', 'plasma', [(5, 1)], loop=False)
        self.anim.add('dead', 'plasma', [(10, 5)], loop=False)
        self.anim.add('run', 'plasma', run_plasma, loop=True)
        self.anim.add('jump', 'plasma', run_plasma, loop=False)
        self.anim.add('wall_jump', 'plasma', [(5, 2), (5, 3), (5, 4)], loop=False)
        self.anim.add('crouch', 'plasma', [(5, 0)], loop=False, padding=crouch)
        self.anim.add('slide', 'plasma', [(10, 2)], loop=False, padding=crouch)
        self.anim.add('plasma', 'plasma', [(5, 5)], loop=False, padding=crouch)

        run_rocket = {'left': [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5)], 'right': [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5)]}
        self.anim.add('idle', 'rocket', [(8, 1)], loop=False)
        self.anim.add('dead', 'rocket', [(10, 5)], loop=False)
        self.anim.add('run', 'rocket', run_rocket, loop=True)
        self.anim.add('jump', 'rocket', run_rocket, loop=False)
        self.anim.add('wall_jump', 'rocket', [(8, 2), (8, 3), (8, 4)], loop=False)
        self.anim.add('crouch', 'rocket', [(8, 0)], loop=False, padding=crouch)
        self.anim.add('slide', 'rocket', [(10, 1)], loop=False, padding=crouch)
        self.anim.add('aim_down', 'rocket', [(9, 2)], loop=False)

        self.anim.play('idle', self.visible_direction)

    def reset(self):
        self.vel = Vector2(0, 0)
        self.direction = 1
        self.visible_direction = 1
        self.distance_to_ground = 0
        self.last_boost = 0
        self.num_boost_ghosts = None
        self.boost_blur_elapsed = 0.0
        self.acceleration = 0
        self.last_walljump = 0
        self.last_ramp_radians = 0
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
        self.jump_pressed_at = None
        self.jump_action_distance = None
        self.jump_timing = float("-inf")
        self.ground_touch_pos = None
        self.ground_collider = None
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
        self.x = self.map.player_start.x
        self.y = self.map.player_start.y
        self.previous_frame_height = 0

        self.action_states = StateMachine(self.Idle_State(), self)
        self.anim.play('idle', self.visible_direction)

    def set_map(self, map):
        self.map = map
        self.x = map.player_start.x
        self.y = map.player_start.y

    def __getattr__(self, name):
        if name == 'current_action_state':
            return self.action_states.get_state()
        return object.__getattribute__(self, name)

    def draw(self):

        scale = self.game.settings.get_scale()


        view_pos_sprite = self.game.camera.to_view_space(self)

        frame, self.w, self.h = self.anim.get_frame(self.visible_direction)

        bbox_padding = (0, 5 * scale, 0, 5 * scale)

        self.w -= (bbox_padding[1] + bbox_padding[3])

        if self.previous_frame_height != self.h:
            self.y += self.previous_frame_height - self.h

        self.previous_frame_height = self.h

        blur_factor = self.last_boost / 64 * scale
        if self.last_ramp_radians == 0:
            self.motion_blur(view_pos_sprite, frame, blur_factor, bbox_padding)
            self.game.surface.blit(frame, (view_pos_sprite.x - bbox_padding[3], view_pos_sprite.y))

        else:
            rotation = math.degrees(self.last_ramp_radians)
            rotated_sprite = pygame.transform.rotate(frame, rotation)
            rect = rotated_sprite.get_rect(center=(view_pos_sprite.x + self.w // 2, view_pos_sprite.y + self.h // 2))
            self.motion_blur(Vector2(rect.topleft[0], rect.topleft[1]), rotated_sprite, blur_factor, bbox_padding)
            self.game.surface.blit(rotated_sprite, rect.topleft)

        # debug draw rect around player
        #pygame.draw.rect(self.game.surface, (0, 0, 0), (view_pos_sprite.x, view_pos_sprite.y, self.w, self.h), 2)

    def motion_blur(self, view_pos, sprite, blur_factor, bbox_padding):
        if self.num_boost_ghosts is not None:
            self.boost_blur_elapsed += config.delta_time
            duration = 420
            remaining_time = max(0.0, duration - self.boost_blur_elapsed)
            inverse_percentage = remaining_time / duration
            for i in range(self.num_boost_ghosts):
                ghost = sprite.copy()
                alpha = 92 / (i + 1) * inverse_percentage
                ghost.set_alpha(alpha)
                self.game.surface.blit(ghost, (view_pos.x - i * blur_factor * self.visible_direction - bbox_padding[3], view_pos.y))
            if self.boost_blur_elapsed >= duration:
                self.num_boost_ghosts = None
                self.boost_blur_elapsed = 0

    def input_wall_jump(self, key_pressed):
        if key_pressed:
            if pygame.time.get_ticks() - self.last_walljump > 1000 and self.walljump_collisions():
                self.last_walljump = pygame.time.get_ticks()
                self.action_states.on_event('walljump')

    def input_right(self, key_pressed):
        self.pressed_right = key_pressed
        if key_pressed:
            self.was_flipped = False
            self.visible_direction = 1
            if self.current_action_state == 'Crouch_State' and self.direction == 1:
                self.action_states.on_event('slide')

    def input_left(self, key_pressed):
        self.pressed_left = key_pressed
        if key_pressed:
            self.was_flipped = False
            self.visible_direction = -1
            if self.current_action_state == 'Crouch_State' and self.direction == -1:
                self.action_states.on_event('slide')

    def input_down(self, key_pressed):
        self.pressed_down = key_pressed
        if key_pressed:
            #if self.active_weapon == 'rocket' and (self.current_action_state == 'Fall_State' or self.current_action_state == 'Jump_State'):
            #    self.anim.play('aim_down', self.visible_direction)
            #else:
            self.anim.play('crouch', self.visible_direction)
            self.action_states.on_event('crouch')
        else:
            self.anim.previous(self.direction)

    def input_up(self, key_pressed):
        self.pressed_up = key_pressed

    def input_jump(self, key_pressed):
        self.pressed_jump = key_pressed
        if key_pressed:
            if self.jump_pressed_at is None:
                self.jump_pressed_at = pygame.time.get_ticks()
                if not self.jump_action_distance and not self.last_ramp_radians:
                    self.jump_action_distance = self.distance_to_ground / self.game.settings.get_scale()
        else:
            self.jump_pressed_at = None
            self.pressed_jump = False
            self.released_jump = True

    def input_switch_weapon(self, key_pressed):
        if key_pressed and self.last_weapon_switch + 666 < pygame.time.get_ticks():
            if self.active_weapon == 'rocket' and self.has_plasma:
                self.active_weapon = 'plasma'
                self.anim.group = 'plasma'
            elif self.active_weapon == 'plasma' and self.has_rocket:
                self.active_weapon = 'rocket'
                self.anim.group = 'rocket'
            #self.animation.set_active_weapon()
            self.last_weapon_switch = pygame.time.get_ticks()

    def update(self):

        self.can_uncrouch = self.crouching and self.check_can_uncrouch()
        self.distance_to_ground = self.get_distance_to_collider_below()

        self.plasma_timer = min(self.plasma_timer + config.delta_time, self.plasma_cooldown)
        self.rocket_timer = min(self.rocket_timer + config.delta_time, self.rocket_cooldown)

        #print("vely", self.vel.y)

        # Trigger falling
        if self.vel.y > 0 and self.current_action_state != 'Plasma_State':
            self.action_states.on_event('fall')

        if self.pressed_jump and self.released_jump and (not self.crouching or self.can_uncrouch):
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

        self.anim.update(config.delta_time, self.direction, self.visible_direction, self.speed_to_fps(abs(self.vel.x)))

    def speed_to_fps(self, speed, speed_min=0.01, speed_max=4.0, fps_min=5, fps_max=32, power=0.5):
        """
        Map player speed to animation FPS.
        - speed: player speed (0.1 = slow, 1 = medium, 4 = ultra fast)
        - fps_min: fps at slowest
        - fps_max: fps at fastest
        - power: curve shaping factor (0.5 = sqrt, 1 = linear, 2 = quadratic)
        """
        scale = self.game.settings.get_scale()

        # clamp speed to range
        s = max(speed_min * scale, min(speed * scale, speed_max * scale))
        # normalize 0..1
        norm = (s - speed_min * scale) / (speed_max * scale - speed_min * scale)
        # apply curve
        curved = norm ** power
        # scale to fps range
        return fps_min + (fps_max - fps_min) * curved

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
                    self.map.projectiles.append(Projectile('rocket', 1337000, self.x + config.ROCKET_DOWN_OFFSET_X * scale, self.y + config.ROCKET_DOWN_OFFSET_Y * scale, self.vel.x, self.vel.y + 1 * scale, 0.7 * scale, -0.0015 * scale, channel, ['ramp', 'static']))
                else:
                    self.map.projectiles.append(Projectile('rocket', 1337000, self.x + 30 * scale, self.y + 5 * scale, self.vel.x + 1 * scale * self.visible_direction, 0, 1.1 * scale, -0.00075 * scale, channel, ['ramp', 'static']))

    def shoot_plasma(self):
        scale = self.game.settings.get_scale()
        if self.plasma_timer >= self.plasma_cooldown:
            self.plasma_timer -= self.plasma_cooldown
            if self.plasma_ammo <= 0:
                sounds.weapon_empty.play()
            else:
                sounds.plasma.play()
                self.plasma_ammo -= 1
                if (self.pressed_down or self.pressed_up or self.pressed_left or self.pressed_right) and self.plasma_climb_collisions():
                    if self.game.settings.new_plasma:
                        x_offset = 0
                        if self.pressed_left:
                            x_offset = -3 * scale
                        elif self.pressed_right:
                            x_offset = 3 * scale

                        y_offset = 0
                        if self.pressed_up:
                            y_offset = -3 * scale
                        elif self.pressed_down:
                            y_offset = 3 * scale

                        self.action_states.on_event('plasma')
                        self.map.projectiles.append(Projectile('plasma', 1000, self.x - 0.5 * scale + x_offset, self.y + y_offset, self.vel.x, self.vel.y, collide_with=['wall']))
                    else:
                        if self.pressed_left:
                            decal_offset = 5
                        elif self.pressed_right:
                            decal_offset = 30
                        else:
                            decal_offset = 15

                        self.action_states.on_event('plasma')
                        self.map.decals.append(Decal('plasma', 1000, self.x + decal_offset * scale, self.y + 5 * scale, center=True, fade_out=True))
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
                    self.map.projectiles.append(Projectile('plasma', 10000, self.x + 30 * scale * self.direction, self.y + 2 * scale, self.vel.x + 3 * scale * self.direction))


    def get_distance_to_collider_below(self):
        """
        Returns the vertical distance to the closest line of all static_colliders and ramp_colliders
        that are directly below the player.

        Returns:
            float: The vertical distance to the closest collider below the player.
                  Returns float('inf') if no collider is found below the player.
        """

        if self.ground_collider is not None:
            return 0

        player_x = self.x + self.w / 2  # Player center x-coordinate
        player_bottom_y = self.y + self.h  # Player bottom y-coordinate

        min_distance = float('inf')

        # Check static colliders
        for rectangle in self.map.static_colliders:
            # Only check colliders that are horizontally aligned with the player
            if rectangle.x <= player_x <= rectangle.x + rectangle.w:
                # Only check colliders that are below the player
                if rectangle.y > player_bottom_y:
                    distance = rectangle.y - player_bottom_y
                    if distance < min_distance:
                        min_distance = distance


        # Check ramp colliders
        for triangle in self.map.ramp_colliders:
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
            print("steep up", ramp_steepness, up)
            return 1.0 + ramp_steepness * up
        # For up-ramps, friction should be below 1 to create decelaration based on steepness
        elif self.last_ramp_radians < 0:
            # The steeper the ramp, the higher the value (more deceleration)
            ramp_steepness = math.cos(self.last_ramp_radians)
            print("steep down", ramp_steepness, down)
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

        brake_factor = 1
        if (self.direction == 1 and self.pressed_left) or (self.direction == -1 and self.pressed_right):
            brake_factor = 0.993

        # no friction while mid-air
        if self.current_action_state == 'Jump_State' or self.current_action_state == 'Fall_State':
            base_factor = 1

        elif self.current_action_state == 'Decel_State':
            return 0.998 * brake_factor

        elif self.current_action_state == 'Crouch_State':
            return 0.998 * brake_factor
        elif self.current_action_state == 'Slide_State':
            # to have less deceleration for up-ramps
            print("rad", self.last_ramp_radians)
            if (self.last_ramp_radians > 0 and self.direction == 1) or (self.last_ramp_radians < 0 and self.direction == -1):
                gravity_effect = 0.0007
            # and more acceleration for down-ramps
            elif (self.last_ramp_radians < 0 and self.direction == 1) or (self.last_ramp_radians > 0 and self.direction == -1):
                gravity_effect = 0.005
            else:
                base_factor = 0.91

        return self.get_friction_factor(self.vel.x, self.last_ramp_radians, gravity_effect / self.game.settings.get_scale(), base_factor * brake_factor, velocity_scaling / self.game.settings.get_scale())


    def movement(self):
        scale = self.game.settings.get_scale()

        # Cap vertical velocity
        if self.vel.y > config.MAX_FALL_VEL * scale:
            self.vel.y = config.MAX_FALL_VEL * scale

        # Accelerate
        self.vel.x += self.acceleration * scale * config.delta_time

        #if self.distance_to_ground > 0:
        self.vel.y += config.GRAVITY * scale * config.delta_time

        # Apply friction
        self.vel.x *= pow(self.get_friction(), config.delta_time)

        # Move axes individually for proper collision detection
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)

        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        self.x += dx * config.delta_time
        self.y += dy * config.delta_time

        self.collider_collisions(dx, dy)
        self.ramp_collisions()
        self.item_collisions()
        self.functional_collisions()

    def state_events(self):
        if not self.was_flipped:
            if self.current_action_state == 'Plasma_State':
                if self.pressed_left and self.vel.x >= 0:
                    self.direction = 1
                elif self.pressed_right and self.vel.x <= 0:
                    self.direction = -1
            else:
                if (self.pressed_right or self.pressed_jump) and self.vel.x >= 0:
                    self.direction = 1
                elif (self.pressed_left or self.pressed_jump) and self.vel.x <= 0:
                    self.direction = -1

        if self.vel.y == 0 and (not self.crouching or self.can_uncrouch):

            if (self.pressed_right or self.pressed_left) and not self.pressed_down:
                self.action_states.on_event('move')

            if self.vel.x > 0 and not self.pressed_right and not self.pressed_down and not self.current_action_state == 'Idle_State':
                self.action_states.on_event('decel')

            elif self.vel.x < 0 and not self.pressed_left and not self.pressed_down and not self.current_action_state == 'Idle_State':
                self.action_states.on_event('decel')

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State' and not self.pressed_down:
                self.vel.x = 0
                self.action_states.on_event('idle')

        # air brake
        if self.current_action_state == 'Fall_State':
            # air accelerate
            if (self.vel.x >= 0 and self.pressed_right and not self.pressed_left) or (self.vel.x <= 0 and self.pressed_left and not self.pressed_right):
                scaling_factor = max(0.0, 1.0 - (abs(self.vel.x) / 0.3))
                acceleration_x = config.PLAYER_AIR_ACCEL * scaling_factor
                self.vel.x += acceleration_x * config.delta_time * self.direction

            # air brake
            elif self.vel.x > 0 and self.pressed_left and not self.pressed_right:
                self.vel.x -= config.PLAYER_AIR_BREAK * config.delta_time
                if self.vel.x < 0:
                    self.vel.x = 0

            elif self.vel.x < 0 and self.pressed_right and not self.pressed_left:
                self.vel.x += config.PLAYER_AIR_BREAK * config.delta_time
                if self.vel.x > 0:
                    self.vel.x = 0

        elif self.crouching and abs(self.vel.x) < 0.03:
            self.vel.x = 0

    def collider_collisions(self, dx, dy):

        # when currently colliding with a ramp, ignore static (rect) colliders
        # fixes weird warping, when running from a static collider onto a down-ramp
        if self.last_ramp_radians != 0:
            return

        index = self.collidelist(self.map.static_colliders)


        if index == -1:
            return

        other_collider = self.map.static_colliders[index]

        if dx > 0:
            #print("dx > 0")
            if self.current_action_state == 'Move_State' and not self.pressed_down and not self.pressed_right and not self.pressed_left and not self.pressed_up:
                self.action_states.on_event('decel')
            self.x = other_collider.x - self.w
            self.vel.x = 0
        elif dx < 0:
            #print("dx < 0")
            if self.current_action_state == 'Move_State' and not self.pressed_down and not self.pressed_right and not self.pressed_left and not self.pressed_up:
                self.action_states.on_event('decel')
            self.x = other_collider.x + other_collider.w
            self.vel.x = 0
        elif dy > 0:
            #print("dy > 0")
            if self.current_action_state == 'Fall_State':
                self.ground_touch_pos = Vector2(self.x, self.y)
                self.action_states.on_event('decel')
            self.ground_collider = other_collider
            self.y = other_collider.y - self.h
            self.vel.y = 0
        elif dy < 0:
            #print("dy < 0")
            self.action_states.on_event('fall')
            self.y = other_collider.y + other_collider.h
            self.vel.y = config.BOUNCE_VEL

    def launch_from_ramp(self, y_offset = 0, factor = 1.0):
        self.y -= y_offset
        self.vel.y = -abs(self.vel.x) * math.tan(self.last_ramp_radians * self.direction) * factor

        self.last_ramp_radians = 0

        print("launch from ramp", -abs(self.vel.x) * math.tan(self.last_ramp_radians * self.direction) * factor, y_offset)
        self.action_states.on_event('launch')

        return self.vel.y

    def ramp_collisions(self):

        if self.current_action_state == 'Launch_State':
            return

        # Get the line of the ramp we collided with (up or down)
        ramp_collider = self.check_triangle_top_sides_collision(self.map.ramp_colliders)

        if ramp_collider is None:
            # launch when leaving a ramp
            if (self.direction == 1 and self.last_ramp_radians > 0) or (self.direction == -1 and self.last_ramp_radians < 0):
                self.launch_from_ramp()

            # no ramp collision
            self.last_ramp_radians = 0
            return

        self.game.camera.stop_settling(self)

        # unordered points of the ramp line
        point0 = ramp_collider[0]
        point1 = ramp_collider[1]

        # determine which is the start and which is the end point
        if point0.x < point1.x:
            left_point = point0
            right_point = point1
        else:
            left_point = point1
            right_point = point0

        x_start, y_start = left_point.x, left_point.y
        x_end, y_end = right_point.x, right_point.y

        # get the angle from proper start and end points
        dy = y_end - y_start
        dx = x_end - x_start

        next_rad = -math.atan2(dy, dx) # WHY - ???

        #print(self.last_ramp_radians, next_rad)

        # launch when sliding over the peak of a two-sided ramp
        if (self.direction == 1 and self.last_ramp_radians > 0 > next_rad) or (self.direction == - 1 and self.last_ramp_radians < 0 < next_rad):
            self.launch_from_ramp()
            return

        # Remember for launching when leaving the ramp
        self.last_ramp_radians = next_rad

        # Calculate horizontal progress (progress ratio) across the ramp
        x = self.x + self.w / 2  # Player center x
        progress = max(0, min(1, (x - x_start) / dx))  # Clamp to [0,1]

        # Linear interpolation from base y to top y
        y_on_ramp = (1 - progress) * y_start + progress * y_end

        # Set player's feet to ramp surface
        self.y = y_on_ramp - self.h

        if not self.ground_touch_pos:
            self.ground_touch_pos = Vector2(self.x, self.y)

        self.vel.y = 0

        self.action_states.on_event('ramp')

    def item_collisions(self):
        for item in self.map.items:
            if item.picked_up:
                if item.stay and item.respawn_at is not None and pygame.time.get_ticks() > item.respawn_at:
                    item.picked_up = False
                    item.respawn_at = None
                continue
            if item.x - item.width <= self.x + self.w / 2 <= item.x + item.width and item.y - item.height <= self.y + self.h / 2 <= item.y + item.height:
                sounds.pickup.play()
                self.active_weapon = item.type
                self.anim.group = item.type
                if item.type == 'rocket':
                    self.has_rocket = True
                    self.rocket_ammo += item.ammo
                elif item.type == 'plasma':
                    self.has_plasma = True
                    self.plasma_ammo += item.ammo
                item.picked_up = True
                if item.stay:
                    item.respawn_at = pygame.time.get_ticks() + 3000
                #self.animation.set_active_weapon()#

    def functional_collisions(self):

        scale = self.game.settings.get_scale()

        for portal in self.map.portals:
            if portal.collidepoint(self.midbottom[0], self.midbottom[1]):
                portal.teleport(self)
                return

        for jump_pad in self.map.jump_pads:
            if jump_pad.collidepoint(self.midbottom[0], self.midbottom[1]):
                jump_pad.jump(self)
                return

        if self.collidelist(self.map.death_colliders) != -1:
            self.action_states.on_event('dead')

        if self.map.timer == 0 and self.map.start_line is not None:
            if self.colliderect(self.map.start_line) != -1:
                self.map.start_timer()

        if self.map.timer != 0 and self.map.finish_line is not None:
            if self.colliderect(self.map.finish_line) != -1:
                self.map.stop_timer()

    def walljump_collisions(self):
        return self.collidelist(self.map.wall_colliders) != -1

    def plasma_climb_collisions(self):
        for collider in self.map.wall_colliders:
            if collider.collidepoint(self.center[0], self.center[1]):
                return True

        return False

    def check_can_uncrouch(self):
        stand_rect = pygame.Rect(self.x, self.y - 24, self.w, self.h + 24)
        return stand_rect.collidelist(self.map.static_colliders) == -1

    def calculate_distance(self, pos1, pos2):
        """Calculates the Euclidean distance between two points."""
        if pos1 is None or pos2 is None:
            return 0
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

    def add_jump_velocity(self):

        scale = self.game.settings.get_scale()

        # Determine if the jump was early or late
        if self.jump_action_distance is not None and self.jump_action_distance != 0:
            self.jump_timing = -self.jump_action_distance
        else:
            late_jump_distance = None if self.ground_touch_pos is None else self.calculate_distance(self, self.ground_touch_pos)
            if late_jump_distance is not None and late_jump_distance != 0:
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

            if abs(self.vel.x) < 0.2:
                self.vel.x = 0.15 * self.visible_direction

        # launch from up-ramp
        if (self.last_ramp_radians > 0 and self.direction == 1) or (self.last_ramp_radians < 0 and self.direction == -1):
            self.launch_from_ramp(20 * scale, 0.42)

        # launch from down-ramp
        elif (self.last_ramp_radians < 0 and self.direction == 1) or (self.last_ramp_radians > 0 and self.direction == -1):
            # down-launch adds to the just boost
            boost += self.launch_from_ramp(20 * scale, 0.2)

        # give additional jump boost when moving backwards
        reverse_boost = 1
        if self.direction != self.visible_direction:
            reverse_boost = 2

        self.vel.x += boost * scale * self.visible_direction * reverse_boost
        self.vel.y += config.JUMP_VELOCITY * scale

        self.released_jump = False
        self.acceleration = 0
        self.last_boost = round(boost * 1000)
        self.num_boost_ghosts = math.ceil(11 * self.last_boost / 256)
        self.boost_blur_elapsed = 0

    def add_plasma_velocity(self, distance, angle_rad):
        scale = self.game.settings.get_scale()
        vel_magnitude = 0.1
        vel_x = vel_magnitude * math.cos(angle_rad)
        vel_y = vel_magnitude * math.sin(angle_rad)
        self.vel.x += vel_x * scale
        self.vel.y += vel_y * scale

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

            if self.distance_to_ground == 0:
                self.action_states.on_event('idle')
            else:
                self.action_states.on_event('fall')

            #self.anim.play('jump', self.visible_direction)

    class Idle_State(State):
        """State when on the ground and not moving"""
        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'decel':
                return Player.Move_State()
            #elif event == 'fall':
            #    return Player.Fall_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.anim.play('idle', player.visible_direction)
            return

        def update(self, player):
            if player.pressed_down:
                player.action_states.on_event('crouch')

    class Jump_State(State):
        """State when jumping when spacebar input affects velocity"""

        def on_event(self, event):
            if event == 'fall':
                return Player.Fall_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            #elif event == 'crouch':
            #    return Player.Crouch_State()
            elif event == 'ramp':
                return Player.Move_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())

            player.anim.play('jump', player.visible_direction)

            player.ground_collider = None
            player.last_walljump = 0

            if random.choice([True, False]):
                sounds.jump1.play()
            else:
                sounds.jump2.play()

            dash = f'dash{random.choice([1, 2])}'
            if player.direction == -1:
                dash = f'{dash}_left'

            player.game.map.decals.append(Decal(dash, 666, player.x, player.y + player.h, bottom=True, fade_out=True))
            player.add_jump_velocity()

        def update(self, player):
            pass

    class Walljump_State(State):

        def __init__(self):
            self.animation_finished = False

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

        def on_animation_finished(self):
            self.animation_finished = True

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            if random.choice([True, False]):
                sounds.walljump1.play()
            else:
                sounds.walljump2.play()

            player.anim.play('wall_jump', player.visible_direction, callback=self.on_animation_finished, reset=True)
            player.vel.y = config.WALLJUMP_VELOCITY * player.game.settings.get_scale()

        def can_exit(self, player):
            return self.animation_finished

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

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.anim.play('plasma', player.visible_direction)
            pass

        def update(self, player):
            if not player.pressed_left and not player.pressed_right and not player.pressed_up and not player.pressed_down:
                player.action_states.on_event('fall')

    class Fall_State(State):
        """State when in mid air but spacebar input does not affect velocity"""
        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'move':
                return Player.Move_State()
            #elif event == 'crouch':
            #    return Player.Crouch_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'ramp':
                return Player.Move_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.ground_collider = None
            pass

        def update(self, player):
            player.acceleration = 0

    class Launch_State(State):
        def __init__(self):
            self.launch_time = 0

        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            elif event == 'decel':
                return Player.Decel_State()
            elif event == 'move':
                return Player.Move_State()
            #elif event == 'crouch':
            #    return Player.Crouch_State()
            elif event == 'walljump':
                return Player.Walljump_State()
            elif event == 'ramp':
                return Player.Move_State()
            elif event == 'fall':
                return Player.Fall_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.last_ramp_radians = 0
            self.launch_time = 0

        def update(self, player):
            player.acceleration = 0
            self.launch_time += config.delta_time
            if self.launch_time > 100:
                player.action_states.on_event('fall')

    class Move_State(State):
        """State when moving on the ground and not breaking or decelerating"""
        def on_event(self, event):
            if event == 'decel':
                return Player.Decel_State()
            #elif event == 'fall':
            #    return Player.Fall_State()
            elif event == 'jump':
                return Player.Jump_State()
            elif event == 'launch':
                return Player.Launch_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            #elif event == 'idle':
            #    return Player.Idle_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.anim.play('run', player.visible_direction)
            return

        def update(self, player):
            player.acceleration = config.PLAYER_ACCELERATION * player.direction
            if player.pressed_down:
                player.action_states.on_event('crouch')

    class Decel_State(State):
        """State when moving when there is no longer any input"""
        def on_event(self, event):
            if event == 'idle':
                return Player.Idle_State()
            elif event == 'move':
                return Player.Move_State()
            #elif event == 'fall':
            #    return Player.Fall_State()
            elif event == 'launch':
                return Player.Launch_State()
            elif event == 'jump':
                return Player.Jump_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            if not player.pressed_down:
                player.anim.play('run', player.visible_direction)
            player.acceleration = 0

        def update(self, player):
            if player.pressed_down:
                player.action_states.on_event('crouch')

    class Crouch_State(State):
        """State when player is crouching"""

        def on_event(self, event):
            if event == 'jump':
                return Player.Jump_State()
            elif event == 'decel':
                return Player.Decel_State()
            # elif event == 'fall':
            # d    return Player.Fall_State()
            elif event == 'launch':
                return Player.Launch_State()
            elif event == 'slide':
                return Player.Slide_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'idle':
                return Player.Idle_State()
            elif event == 'plasma':
                return Player.Plasma_State()
            elif event == 'dead':
                return Player.Dead_State()
            return self

        def can_enter(self, player):
            return True

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.anim.play('crouch', player.visible_direction)
            player.crouching = True
            player.acceleration = 0

        def update(self, player):
            if (player.direction == 1 and player.pressed_right) or (player.direction == -1 and player.pressed_left):
                player.action_states.on_event('slide')

        def on_exit(self, player):
            player.crouching = False

    class Slide_State(State):
        """State when player is crouching"""
        def on_event(self, event):
            if event == 'decel':
                return Player.Decel_State()
            #elif event == 'fall':
            #d    return Player.Fall_State()
            elif event == 'launch':
                return Player.Launch_State()
            elif event == 'move':
                return Player.Move_State()
            elif event == 'jump':
                return Player.Jump_State()
            elif event == 'dead':
                return Player.Dead_State()
            elif event == 'crouch':
                return Player.Crouch_State()
            return self
        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            player.anim.play('slide', player.visible_direction)
            player.crouching = True
            if player.vel.x == 0:
                player.vel.x = 0.05 * player.visible_direction * player.game.settings.get_scale()

        def update(self, player):
            if not player.pressed_right and not player.pressed_left:
                player.action_states.on_event('crouch')

        def on_exit(self, player):
            player.crouching = False

    class Dead_State(State):
        """State when player is dead"""
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, player):
            #print(__class__, pygame.time.get_ticks())
            #player.freeze_movement = True
            player.freeze_input = True
            sounds.death.play()
            player.anim.play('dead', player.visible_direction)

        def update(self, player):
            self.death_timer += config.delta_time
            player.vel.x = 0
            player.vel.y = 0.1
            if self.death_timer > 300 * config.delta_time:
                self.death_timer = float("-inf")
                player.game.map.reset()
                player.reset()
                player.action_states.on_event('idle')
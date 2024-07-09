import math
import random

import pygame.sprite
from pygame.math import Vector2 as vector

from src.sprites import Sprite
from src.settings import settings
from src.timer import Timer


class SpikeBall(Sprite):
    """Spike ball that moves in semicircular directions, damage player"""
    def __init__(self, pos, surface, group, radius, speed, start_angle, end_angle,
                 pos_z=settings.LAYERS_DEPTH["main"]):
        """Create the spike ball"""
        # Center of the spike
        self.center = pos
        # It's speed
        self.speed = speed

        # Start, current and end angles of the spike ball
        self.start_angle = start_angle
        self.angle = start_angle
        self.end_angle = end_angle

        # If angle is specified as -1, do set the circular flag to True,
        # otherwise don't do full circular movement
        self.circular = True if self.end_angle == -1 else False

        # Radius of the spike ball movement
        self.radius = radius
        # Direction of it
        self.direction = 1

        # Calculate the horizontal and vertical position based off trigonometry rules
        pos_x = self.center[0] + math.cos(math.radians(self.angle)) * self.radius
        pos_y = self.center[1] + math.sin(math.radians(self.angle)) * self.radius
        # Initialize the parent sprite with them
        super().__init__((pos_x, pos_y), surface, group, pos_z)

    def update(self, delta_time):
        """Update spike ball"""
        # Get its new angle
        self.angle += self.direction * self.speed * delta_time

        # Set the direction based off the type of movement
        if not self.circular:
            # If current angle exceeded the end one, set it in the direction of the start angle
            if self.angle >= self.end_angle:
                self.direction = -1
            # Otherwise, if it is lower than the start angle, set it to go near the end one
            if self.angle < self.start_angle:
                self.direction = 1

        # Recalculate the positions
        pos_x = self.center[0] + math.cos(math.radians(self.angle)) * self.radius
        pos_y = self.center[1] + math.sin(math.radians(self.angle)) * self.radius

        # Set the new position of the rectangle
        self.rect.center = (pos_x, pos_y)


class Tooth(pygame.sprite.Sprite):
    """Tooth enemy, that runs around"""
    def __init__(self, pos, frames, group, collision_sprites):
        """Initialize the tooth enemy"""
        super().__init__(group)
        # Prepare the animation variables
        self.frames = frames
        self.frame = 0

        # Get the image based off the current frame and a rectangle of the Tooth
        self.image = self.frames[self.frame]
        self.rect = self.image.get_frect(topleft=pos)

        # Choose a random starting direction of his movement
        self.direction = random.choice((-1, 1))
        # His speed
        self.speed = 220

        # His depth position
        self.pos_z = settings.LAYERS_DEPTH["main"]

        # Rectangles of sprites that he can collide with
        self.collision_rects = [sprite.rect for sprite in collision_sprites]

    def update(self, delta_time):
        """Update the Tooth"""
        # Move the Tooth
        self._move(delta_time)

        # Animate him
        self._animate(delta_time)

    def _animate(self, delta_time):
        """Animate the enemy"""
        # Increase the current frame and set it as the next image
        self.frame += settings.ANIMATION_SPEED * delta_time
        # Make sure to not pass the number of frames
        self.image = self.frames[int(self.frame % len(self.frames))]

        # Flip the image horizontally if he is moving left
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def _move(self, delta_time):
        """Move and change direction of the Tooth"""
        # Move him
        self.rect.x += self.direction * self.speed * delta_time

        # Get his bottom edge rectangles, to calculate collisions
        bottom_left_rect = pygame.FRect(self.rect.bottomleft, (-1, 1))
        bottom_right_rect = pygame.FRect(self.rect.bottomright, (1, 1))

        # If he moves left and there the floor ends, change his direction
        if bottom_left_rect.collidelist(self.collision_rects) < 0 and self.direction < 0:
            self.direction *= -1

        # Do the same for the right direction
        if bottom_right_rect.collidelist(self.collision_rects) < 0 < self.direction:
            self.direction *= -1


class Shell(pygame.sprite.Sprite):
    """Shell enemy that player can stand on and it shoots him"""
    def __init__(self, pos, frames, group, flip, player):
        """Prepare the shell enemy"""
        super().__init__(group)

        # If the shell points left, flip it
        if flip:
            self.frames = {}
            # Go through each animation type
            for animation_type, surfaces in frames.items():
                self.frames[animation_type] = []
                # Go through each of the images
                for surface in surfaces:
                    # Flip them horizontally and append to the frames list of this specific animation type
                    self.frames[animation_type].append(pygame.transform.flip(surface, True, False))

            # Set the projectile direction to the left
            self.projectile_direction = -1

        # Otherwise just set the frames normally
        else:
            self.frames = frames
            # Set projectile direction to right
            self.projectile_direction = 1

        # The current frame
        self.frame = 0

        # Current state of the shell
        self.state = "idle"

        # Get its image based off state and frame, save the rectangle
        self.image = self.frames[self.state][self.frame]
        self.rect = self.image.get_frect(topleft=pos)
        # Get the last rectangle for collisions (it's in the collision group, which requires that)
        self.last_rect = self.rect.copy()

        # Depth position
        self.pos_z = settings.LAYERS_DEPTH["main"]

        # Get the player's reference
        self.player = player

        # Attack cooldown timer
        self.attack_timer = Timer(2500)
        # Shoot flag
        self.shoot = False

    def update(self, delta_time):
        """Update the shell enemy"""
        # Update the attack cooldown timer
        self.attack_timer.update()

        # Change state of the shell if player is near
        self._set_state()

        # Animate the shell
        self._animate(delta_time)

    def _set_state(self):
        """Set state of the shell"""
        # Get player's and shell's positions for range calculations
        player_pos = vector(self.player.hitbox_rect.center)
        shell_pos = vector(self.rect.center)

        # Flag that indicates that player is in range of the shell (distance between them is lower than 500)
        near = shell_pos.distance_to(player_pos) < 500
        # Player is on the vertical level of the shell flag (around 40 pixels difference is acceptable)
        same_level = abs(shell_pos.y - player_pos.y) < 40
        # Set the player in front flag to True if shell shoots to the left and player is on the left
        if self.projectile_direction < 0:
            in_front = shell_pos.x > player_pos.x
        # Otherwise, if player is on the right while it shoots right, set it too
        else:
            in_front = shell_pos.x < player_pos.x

        print(near, same_level, in_front)

        # If player is near the shell, at around the same vertical position and is in front of the shell
        if near and same_level and in_front:
            # If cooldown isn't on, attack
            if not self.attack_timer.active:
                # Change the state to attack
                self.state = "fire"
                # Reset the frames, for clean attack animation
                self.frame = 0

                # Start the attack cooldown
                self.attack_timer.start()

    def _animate(self, delta_time):
        """Animate the shell"""
        # Increase current frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # Set the frame of the shell to the current one, make sure it doesn't go out of bounds
        if self.frame < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame)]

            # If the shell is attacking, didn't shoot already, and it's the third frame of animation
            if self.state == "fire" and not self.shoot and int(self.frame) == 3:
                print("SHOOT")
                # Make the shell shoot
                self.shoot = True

        # If the animation ended restart it
        else:
            # Reset the frame
            self.frame = 0
            # If enemy just shot, set its state back to idle
            if self.state == "fire":
                self.state = "idle"
                # Set shoot flag to False
                self.shoot = False


class Pearl(pygame.sprite.Sprite):
    """Pearl shot by the shell enemy"""
    def __init__(self, pos, surface, group, speed, direction):
        """Initialize the pearl projectile"""
        super().__init__(group)

        # Set image of the pearl and get its rectangle, center it in the given position
        self.image = surface
        self.rect = self.image.get_frect(center=pos)

        # Speed and direction of the projectile
        self.speed = speed
        self.direction = direction

        # Its depth position
        self.pos_z = settings.LAYERS_DEPTH["main"]

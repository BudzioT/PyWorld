import math
import random

import pygame.sprite

from src.sprites import Sprite
from src.settings import settings


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
    def __init__(self, pos, frames, group, flip):
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

        # Otherwise just set the frames normally
        else:
            self.frames = frames

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

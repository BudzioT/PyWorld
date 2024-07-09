import random

import pygame.sprite
from pygame.math import Vector2 as vector

from src.settings import settings


class Sprite(pygame.sprite.Sprite):
    """General sprite class"""
    def __init__(self, pos, surface=pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE)), group=None,
                 pos_z=settings.LAYERS_DEPTH["main"]):
        """Prepare the sprite"""
        super().__init__(group)

        # Get the surface
        self.image = surface

        # Get its rectangle as float for precision
        self.rect = self.image.get_frect(topleft=pos)
        # Store a copy of it for collisions
        self.last_rect = self.rect.copy()

        # Depth position of the sprite
        self.pos_z = pos_z


class AnimatedSprite(Sprite):
    """Sprite that is animated"""
    def __init__(self, pos, frames, group, pos_z=settings.LAYERS_DEPTH["main"], animation_speed=8, ):
        """Initialized the animated sprite"""
        # Animation frames
        self.frames = frames
        # Current frame
        self.frame = 0

        # Initialize the parent Sprite with the first frame
        super().__init__(pos, self.frames[self.frame], group, pos_z)

        # Speed of the animation
        self.animation_speed = animation_speed

    def _animate(self, delta_time):
        """Animate the sprite"""
        # Increase the current frame
        self.frame += self.animation_speed * delta_time
        # Update the image based off the frame
        self.image = self.frames[int(self.frame % len(self.frames))]

    def update(self, delta_time):
        """Update the animation"""
        self._animate(delta_time)


class MovingSprite(AnimatedSprite):
    """Sprite that can move"""
    def __init__(self, start_pos, end_pos, frames, direction, speed, group, flip=False):
        """Initialize the sprite"""
        # Initialize the general sprite
        super().__init__(start_pos, frames, group)

        # Set its correct position
        if direction == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos

        # Get sprite's position
        self.start_pos = start_pos
        self.end_pos = end_pos

        # Move flag
        self.move = True
        # The image needs to be flipped flag
        self.flip = flip

        # Dictionary that manages flip directions
        self.flip_directions = {'x': False, 'y': False}

        # Set its speed
        self.speed = speed

        # Store the direction vector depending on the axis
        self.direction = vector(1, 0) if direction == 'x' else vector(0, 1)
        # Store the sprite movement type
        self.move_type = direction

    def update(self, delta_time):
        """Update the moving sprite"""
        # Update the last rectangle
        self.last_rect = self.rect.copy()

        # Move the sprite
        self.rect.topleft += self.direction * self.speed * delta_time
        # Bounce it if needed
        self._bounce()

        # Anime the sprite
        self._animate(delta_time)
        # Flip the image when in need
        self._flip()

    def _flip(self):
        """Flip the animation if needed"""
        # Flip the image when flag is true, by using the prepared dictionary
        if self.flip:
            self.image = pygame.transform.flip(self.image, self.flip_directions['x'], self.flip_directions['y'])

    def _bounce(self):
        """Bounce the sprite when reaching starting and ending positions"""
        # If the direction is horizontal, handle horizontal bouncing
        if self.move_type == 'x':
            # If sprite is at its end position, change its direction
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            # If sprite is at its start position, change its direction too
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            # Flip the sprite horizontally
            self.flip_directions['x'] = True if self.direction.x < 0 else False

        # Otherwise handle vertical bouncing
        else:
            # Bounce off the end position
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            # Bounce off the start position
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            # Flip the sprite vertically
            self.flip_directions['y'] = True if self.direction.y > 0 else False


class Item(AnimatedSprite):
    """Sprite representing an item"""
    def __init__(self, pos, frames, group, item_type, data):
        """Prepare the item"""
        super().__init__(pos, frames, group)

        # Data of the game
        self.data = data

        # Center the item
        self.rect.center = pos

        # Get item's type
        self.item_type = item_type

    def collect(self):
        """Collect the item's boost"""
        # If it's a silver coin, add one coin to the current amount
        if self.item_type == "silver":
            self.data.coins += 1
        # If it's a golden coin, add 5 coins
        elif self.item_type == "gold":
            self.data.coins += 2
        # Diamond - add 5
        elif self.item_type == "diamond":
            self.data.coins += 5
        # Skull - add 20
        elif self.item_type == "skull":
            self.data.coins += 20

        # If the item is a potion, add one more health to the player, if it hasn't exceeded 5
        if self.item_type == "potion":
            if self.data.health < 5:
                self.data.health += 1
            # If player already has maximum number of lives, give him 10 coins
            else:
                self.data.coins += 10


class Cloud(Sprite):
    """Cloud that moves"""
    def __init__(self, pos, surface, group, pos_z=settings.LAYERS_DEPTH["clouds"]):
        """Initialize the cloud"""
        super().__init__(pos, surface, group, pos_z)

        # Choose a random cloud speed
        self.speed = random.randint(50, 120)
        # Cloud's direction
        self.direction = -1

        # Center the cloud
        self.rect.midbottom = pos

    def update(self, delta_time):
        """Update the cloud's position"""
        # Move the cloud
        self.rect.x += self.direction * self.speed * delta_time

        # If cloud behind the left border of the game, delete it
        if self.rect.right <= 0:
            self.kill()

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


class Node(pygame.sprite.Sprite):
    """Class representing a node in the overworld"""
    def __init__(self, pos, surface, group, level, data, paths):
        """Initialize the node"""
        super().__init__(group)
        # Get the image
        self.image = surface
        # Get surface's rectangle, set it to the center tile position from the given one
        self.rect = self.image.get_frect(center=(pos[0] + settings.TILE_SIZE / 2,
                                                 pos[1] + settings.TILE_SIZE / 2))
        # Set the depth position as path
        self.pos_z = settings.LAYERS_DEPTH["path"]

        # Game's data
        self.data = data

        # Save the node's level
        self.level = level
        # Paths to the node
        self.paths = paths

    def can_move(self, direction):
        """Return if the node has an available path in the given direction"""
        if direction in list(self.paths.keys()):
            return True
        return False


class Icon(pygame.sprite.Sprite):
    """Icon on the overworld map"""
    def __init__(self, pos, frames, group):
        """Initialize the icon"""
        super().__init__(group)

        # Icon flag
        self.icon = True

        # Store the frames and the current one
        self.frames = frames
        self.frame = 0
        # Current icon's state
        self.state = "idle"

        # Path the player's on
        self.path = None

        # Direction of the player's movement
        self.direction = vector()
        # His depth position
        self.pos_z = settings.LAYERS_DEPTH["main"]

        # Speed
        self.speed = 400

        # Set the image from the current state and frame
        self.image = self.frames[self.state][self.frame]

        # Get the rectangle and center in the given position
        self.rect = self.image.get_frect(center=pos)

    def move(self, path):
        """Move the player through the given path"""
        # Center the player on the first point of the path
        self.rect.center = path[0]

        # Copy the rest of the path points
        self.path = path[1:]

        # Find the path
        (self._find_path())

    def _find_path(self):
        """Find and move the player through the current path"""
        # If there is a path, handle the movement
        if self.path:
            print(self.path)
            # If the player's horizontal position is equal to the first point's horizontal position,
            # move vertically
            if self.rect.centerx == self.path[0][0]:
                # Move the player down if the path goes down, or up if it goes up
                self.direction = vector(0, 1 if self.path[0][1] > self.rect.centery else -1)

            # Otherwise move horizontally
            else:
                # Go in the direction of the path
                self.direction = vector(1 if self.path[0][0] > self.rect.centerx else -1, 0)

        # If there isn't any path, stay in place
        else:
            self.direction = vector()

    def update(self, delta_time):
        """Update the player"""
        # If there is a path that player's on, move him
        if self.path:
            # Check collisions with point and find a new path if needed
            self._point_collisions()

            # Move the player
            self.rect.center += self.direction * self.speed * delta_time

    def _point_collisions(self):
        """Check and handle collisions with path points"""
        # If player is moving down, and he moves to the end of the path
        if self.direction.y == 1 and self.rect.centery >= self.path[0][1]:
            # Center him at the end of it
            self.rect.centery = self.path[0][1]
            # Delete the path he was on
            del self.path[0]

            # Find the next path
            self._find_path()

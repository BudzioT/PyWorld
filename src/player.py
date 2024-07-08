import pygame
from pygame.math import Vector2 as vector


class Player(pygame.sprite.Sprite):
    """The player character of the game"""
    def __init__(self, pos, group, collision_sprites):
        """Initialize the player"""
        super().__init__(group)

        # Get player's image
        self.image = pygame.Surface((48, 56))
        # Fill it in red temporary
        self.image.fill("red")

        # Get his rectangle
        self.rect = self.image.get_frect(topleft=pos)
        # Copy his last rectangle (for better collisions)
        self.last_rect = self.rect.copy()

        # Vector of direction of the player
        self.direction = vector()
        # His speed
        self.speed = 200

        # Sprites that player can collide with
        self.collision_sprites = collision_sprites

    def update(self, delta_time):
        """Update the player"""
        # Handle input
        self._input()
        # Move him
        self._move(delta_time)

    def _input(self):
        """Get player's related input"""
        # Store last player's rectangle
        self.last_rect = self.rect.copy()

        # Get the keys pressed
        keys = pygame.key.get_pressed()

        # Create a vector to store his new direction
        new_direction = vector(0, 0)

        # If user's pressed left, change player's direction to the left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_direction.x -= 1
        # Move to the right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_direction.x += 1

        # Save new direction, normalize it for only speed variable to influence the speed of player
        if new_direction:
            self.direction = new_direction.normalize()
        # Only normalize it if movement was done (can't normalize vector with a length of 0)
        else:
            self.direction = new_direction

    def _move(self, delta_time):
        """Move the player"""
        # Move the player horizontally
        self.rect.x += self.direction.x * self.speed * delta_time
        # Check and handle horizontal collisions
        self._check_collisions("horizontal")

        # Move him vertically and handle vertical collisions
        self.rect.y += self.direction.y * self.speed * delta_time
        self._check_collisions("vertical")

    def _check_collisions(self, direction):
        """Check and handle collisions"""
        # Go through each sprite that can collide
        for sprite in self.collision_sprites:
            # If there is a collision, handle it
            if sprite.rect.colliderect(self.rect):
                # Handle horizontal collisions if requested
                if direction == "horizontal":
                    # If player collides with object to the right and was to the right of it in the last frame
                    if self.rect.left <= sprite.rect.right and self.last_rect.left >= sprite.last_rect.right:
                        # Hug him to it
                        self.rect.left = sprite.rect.right

                    # Do the same for the left side
                    if self.rect.right >= sprite.rect.left and self.last_rect.right <= sprite.last_rect.left:
                        self.rect.right = sprite.rect.left

                # Otherwise handle vertical collisions
                else:
                    pass

import pygame
from pygame.math import Vector2 as vector


class Player(pygame.sprite.Sprite):
    """The player character of the game"""
    def __init__(self, pos, group, collision_sprites):
        """Initialize the player"""
        super().__init__(group)

        # Grab game's surface
        self.surface = pygame.display.get_surface()

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
        # Gravity affecting him
        self.gravity = 1350

        # Jump flag
        self.jump = False
        # Jump height
        self.jump_power = 800

        # Collisions with surface that affect jumping, sliding
        self.collisions = {"down": False, "left": False, "right": False}

        # Sprites that player can collide with
        self.collision_sprites = collision_sprites

    def update(self, delta_time):
        """Update the player"""
        # Handle input
        self._input()
        # Check for collision contacts
        self._check_contact()
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

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump = True

        # Save new horizontal direction, normalize it for only speed variable to influence the speed of player
        if new_direction.x:
            self.direction.x = new_direction.normalize().x
        # Only normalize it if movement was done (can't normalize vector with a length of 0)
        else:
            self.direction.x = new_direction.x

    def _move(self, delta_time):
        """Move the player"""
        # Move the player horizontally
        self.rect.x += self.direction.x * self.speed * delta_time
        # Check and handle horizontal collisions
        self._check_collisions("horizontal")

        # Check if player is wall sliding (isn't on the floor but touches left or right wall)
        if not (self.collisions["down"]) and any((self.collisions["left"], self.collisions["right"])):
            # Reset the direction
            self.direction.y = 0
            # Set it to falling slowly
            self.rect.y += self.gravity / 10 * delta_time

        # Otherwise apply normal gravity
        else:
            print("A")
            # Apply gravity to the direction
            self.direction.y += self.gravity / 2 * delta_time
            # Move him vertically
            self.rect.y += self.direction.y * delta_time
            # Change the direction again
            self.direction.y += self.gravity / 2 * delta_time

        # Handle player's jumping when the jump flag is true
        if self.jump:
            # If player has down collision, meaning he is standing on something, allow him to jump
            if self.collisions["down"]:
                self.direction.y = -self.jump_power
            # Disable multi-jumping
            self.jump = False

        # Check for vertical collisions
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
                    # Check for top collision, don't allow the player to pass through the collision sprite
                    if self.rect.top <= sprite.rect.bottom and self.last_rect.top >= sprite.last_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    # Check for bottom collision, make the player stand on the other sprite
                    if self.rect.bottom >= sprite.rect.top and self.last_rect.bottom <= sprite.last_rect.top:
                        self.rect.bottom = sprite.rect.top

                    # Reset the vertical direction, so the gravity doesn't increase constantly
                    self.direction.y = 0

    def _check_contact(self):
        """Check for contacts with tiles"""
        # Get the player's bottom rectangle for bottom collisions
        down_rect = pygame.Rect(self.rect.bottomleft, (self.rect.width, 2))
        # Get the wall rectangles too
        right_rect = pygame.Rect(self.rect.topright + vector(0, self.rect.height / 4), (2, self.rect.height / 2))
        left_rect = pygame.Rect(self.rect.topleft + vector(-2, self.rect.height / 4), (2, self.rect.height / 2))

        # Draw rectangles for visualization
        pygame.draw.rect(self.surface, "pink", down_rect)
        pygame.draw.rect(self.surface, "yellow", right_rect)
        pygame.draw.rect(self.surface, "yellow", left_rect)

        # Check if there were any collisions with collide-able sprites
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # If there were any with player's bottom rectangle, set down collisions flag to True
        if down_rect.collidelist(collide_rects) >= 0:
            self.collisions["down"] = True
        # Otherwise set it to False
        else:
            self.collisions["down"] = False

        # Check and set right collisions
        self.collisions["right"] = True if right_rect.collidelist(collide_rects) >= 0 else False
        # Check and set left ones
        self.collisions["left"] = True if left_rect.collidelist(collide_rects) >= 0 else False

        print(self.collisions)

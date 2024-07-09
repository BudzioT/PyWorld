import math

import pygame
from pygame.math import Vector2 as vector

from src.timer import Timer
from src.utilities import utilities
from src.settings import settings


class Player(pygame.sprite.Sprite):
    """The player character of the game"""
    def __init__(self, pos, frames, group, collision_sprites, semi_collision_sprites, data):
        """Initialize the player"""
        super().__init__(group)

        # Grab game's surface
        self.surface = pygame.display.get_surface()

        # Game's data
        self.data = data

        # Save the player animation frames, set the current frame
        self.frames = frames
        self.frame = 0

        # His current state
        self.state = "idle"
        # Flip player horizontally flag
        self.flip = False

        # Attack flag
        self.attack = False

        # Get player's image
        self.image = self.frames[self.state][self.frame]

        # Get his rectangle
        self.rect = self.image.get_frect(topleft=pos)
        # Get his hitbox rectangle
        self.hitbox_rect = self.rect.inflate(-76, -36)

        # Copy his last rectangle (for better collisions)
        self.last_rect = self.hitbox_rect.copy()

        # Player's depth position
        self.pos_z = settings.LAYERS_DEPTH["main"]

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

        # Player timers
        self.timers = {
            "wall_jump": Timer(500),
            "block_wall_jump": Timer(300),
            "platform_skip": Timer(100),
            "attack": Timer(600),
            "hit": Timer(450)
        }

        # Collisions with surface that affect jumping, sliding
        self.collisions = {"down": False, "left": False, "right": False}

        # Sprites that player can collide with
        self.collision_sprites = collision_sprites
        # Semi collisions sprites, that player can only collide with on top of them
        self.semi_collision_sprites = semi_collision_sprites

        # Platform that player's on
        self.platform = None

    def update(self, delta_time):
        """Update the player"""
        # Store last player's rectangle
        self.last_rect = self.hitbox_rect.copy()

        # Update time on timers
        self._update_timers()

        # Handle input
        self._input()

        # Move him
        self._move(delta_time)
        # Move him when he's on moving platform
        self._move_platform(delta_time)

        # Check for collision contacts
        self._check_contact()

        # Update player's state
        self._update_state()
        # Animate him
        self._animate(delta_time)

        # Flicker the player if he was hit
        self._flicker()

    def _input(self):
        """Get player's related input"""
        # Get the keys pressed
        keys = pygame.key.get_pressed()

        # Create a vector to store his new direction
        new_direction = vector(0, 0)

        if not self.timers["wall_jump"].active:
            # If user's pressed left, change player's direction to the left
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                new_direction.x -= 1
                # Flip the player, so he's facing left
                self.flip = True
            # Move to the right
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                new_direction.x += 1
                # Reset the flip flag
                self.flip = False
            # Skip through the platform
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.timers["platform_skip"].start()

            # Attack on K or X pressed
            if keys[pygame.K_k] or keys[pygame.K_x]:
                self._attack()

            # Save new horizontal direction, normalize it for only speed variable to influence the speed of player
            if new_direction.x:
                self.direction.x = new_direction.normalize().x
            # Only normalize it if movement was done (can't normalize vector with a length of 0)
            else:
                self.direction.x = new_direction.x

        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump = True

    def _move(self, delta_time):
        """Move the player"""
        # Move the player horizontally
        self.hitbox_rect.x += self.direction.x * self.speed * delta_time
        # Check and handle horizontal collisions
        self._check_collisions("horizontal")

        # Check if player is wall sliding (isn't on the floor but touches left or right wall)
        if not self.collisions["down"] and any((self.collisions["left"], self.collisions["right"]))\
                and not self.timers["block_wall_jump"].active:
            # Reset the direction
            self.direction.y = 0
            # Set it to falling slowly
            self.hitbox_rect.y += self.gravity / 10 * delta_time

        # Otherwise apply normal gravity
        else:
            # Apply gravity to the direction
            self.direction.y += self.gravity / 2 * delta_time
            # Move him vertically
            self.hitbox_rect.y += self.direction.y * delta_time
            # Change the direction again
            self.direction.y += self.gravity / 2 * delta_time

        # Handle player's jumping when the jump flag is true
        if self.jump:
            # If player has down collision, meaning he is standing on something, allow him to jump
            if self.collisions["down"]:
                self.direction.y = -self.jump_power

                # Start the timer to bloc him from wall jumping
                self.timers["block_wall_jump"].start()
                # Move the player up a little, so the moving platforms doesn't absorb the player
                self.hitbox_rect.bottom -= 1

            # If player touches the wall in air and there isn't a wall jump block time, allow him to jump
            elif (any((self.collisions["left"], self.collisions["right"]))
                  and not self.timers["block_wall_jump"].active):
                # Start the wall jump timer
                self.timers["wall_jump"].start()

                # Increase player's direction to the top, save it to the rectangle
                self.direction.y = -self.jump_power
                # Apply negative to the current direction
                self.direction.x = 1 if self.collisions["left"] else -1

            # Disable multi-jumping
            self.jump = False

        # Check for vertical collisions
        self._check_collisions("vertical")
        # Check for semi collisions
        self._check_semi_collisions()

        # Update player's position based off the hitboxes
        self.rect.center = self.hitbox_rect.center

    def _check_collisions(self, direction):
        """Check and handle collisions"""
        # Go through each sprite that can collide
        for sprite in self.collision_sprites:
            # If there is a collision, handle it
            if sprite.rect.colliderect(self.hitbox_rect):
                # Handle horizontal collisions if requested
                if direction == "horizontal":
                    # If player collides with object to the right and was to the right of it in the last frame
                    if (self.hitbox_rect.left <= sprite.rect.right and int(self.last_rect.left)
                            >= int(sprite.last_rect.right)):
                        # Hug him to it
                        self.hitbox_rect.left = sprite.rect.right

                    # Do the same for the left side
                    if (self.hitbox_rect.right >= sprite.rect.left and int(self.last_rect.right)
                            <= int(sprite.last_rect.left)):
                        self.hitbox_rect.right = sprite.rect.left

                # Otherwise handle vertical collisions
                else:
                    # Check for top collision, don't allow the player to pass through the collision sprite
                    if (self.hitbox_rect.top <= sprite.rect.bottom and int(self.last_rect.top)
                            >= int(sprite.last_rect.bottom)):
                        self.hitbox_rect.top = sprite.rect.bottom
                        # If platform that player's collides with is moving, push him down a little, so he doesn't
                        # Stick to it
                        if hasattr(sprite, "move"):
                            self.hitbox_rect.top += 6

                    # Check for bottom collision, make the player stand on the other sprite
                    if (self.hitbox_rect.bottom >= sprite.rect.top and int(self.last_rect.bottom)
                            <= int(sprite.last_rect.top)):
                        self.hitbox_rect.bottom = sprite.rect.top

                    # Reset the vertical direction, so the gravity doesn't increase constantly
                    self.direction.y = 0

    def _check_semi_collisions(self):
        """Check semi collisions with player"""
        if not self.timers["platform_skip"].active:
            # Go through each semi collision sprites
            for sprite in self.semi_collision_sprites:
                # Check if they collide with the player
                if sprite.rect.colliderect(self.hitbox_rect):
                    # If so, let the player stay on them
                    if (self.hitbox_rect.bottom >= sprite.rect.top and int(self.last_rect.bottom)
                            <= int(sprite.last_rect.top)):
                        self.hitbox_rect.bottom = sprite.rect.top

                        if self.direction.y > 0:
                            self.direction.y = 0

    def _check_contact(self):
        """Check for contacts with tiles"""
        # Get the player's bottom rectangle for bottom collisions
        down_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        # Get the wall rectangles too
        right_rect = pygame.Rect(self.hitbox_rect.topright + vector(0, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))
        left_rect = pygame.Rect(self.hitbox_rect.topleft + vector(-2, self.hitbox_rect.height / 4), (2, self.hitbox_rect.height / 2))

        # Check if there were any collisions with collide-able sprites
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        # Check for semi collide sprites and get their rectangles
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]

        # If there were any with player's bottom rectangle, set down collisions flag to True
        self.collisions["down"] = True if (down_rect.collidelist(collide_rects) >= 0
                                           or down_rect.collidelist(semi_collide_rect) >= 0
                                           and self.direction.y >= 0) else False

        # Check and set right collisions
        self.collisions["right"] = True if right_rect.collidelist(collide_rects) >= 0 else False
        # Check and set left ones
        self.collisions["left"] = True if left_rect.collidelist(collide_rects) >= 0 else False

        # Reset the platform that player's on
        self.platform = None
        # Add the collision sprites to the semi collision ones
        all_sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()

        # Go through each colliding sprite that has the attribute move (platforms do)
        for sprite in [sprite for sprite in all_sprites if hasattr(sprite, "move")]:
            # If this sprite collides with player, set his platform to this one
            if sprite.rect.colliderect(down_rect):
                self.platform = sprite

    def _attack(self):
        """Make the player attack"""
        # If the attack cooldown passed, handle the attack action
        if not self.timers["attack"].active:
            # Set the attack flag
            self.attack = True
            # Set the frame to the first one
            self.frame = 0

            # Activate the attack cooldown
            self.timers["attack"].start()

    def _move_platform(self, delta_time):
        """Move when player's on the platform"""
        # If player's on the platform, move him with it
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * delta_time

    def _update_timers(self):
        """Update all the timers"""
        for timer in self.timers.values():
            timer.update()

    def handle_damage(self):
        """Handle getting damage"""
        # If the hit cooldown has passed
        if not self.timers["hit"].active:
            # Reduce the player's health
            self.data.health -= 1

            # Start the cooldown again
            self.timers["hit"].start()

    def _flicker(self):
        """Flicker the player's image"""
        # If player was hit, make him flicker and if current sinus is greater than 0 (for flicker effect)
        if self.timers["hit"].active and math.sin(pygame.time.get_ticks() / 30) >= 0:
            # Create a white mask in the player's shape
            mask_surface = pygame.mask.from_surface(self.image).to_surface()
            # Hide the black borders
            mask_surface.set_colorkey("black")
            # Apply it to the image
            self.image = mask_surface

    def _update_state(self):
        """Update the player's state"""
        # If player is on the ground set the idle animation or the run one
        if self.collisions["down"]:
            # If he attacks on floor, set the attack animation
            if self.attack:
                self.state = "attack"
            else:
                # If player's horizontal direction isn't equal to 0, set his state to run
                self.state = "idle" if self.direction.x == 0 else "run"

        else:
            # If he attacks in the air, set the proper action
            if self.attack:
                self.state = "air_attack"
            else:
                # If player is in the air, and he touches a wall, set his state to wall sliding
                if any((self.collisions["left"], self.collisions["right"])):
                    self.state = "wall"
                # Otherwise if he's vertical direction drops, set it to fall and if not, to jump
                else:
                    self.state = "jump" if self.direction.y < 0 else "fall"

    def _animate(self, delta_time):
        """Animate the player"""
        # Increase the current frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # If player is attacking and his animation passed, set it back to idle
        if self.state == "attack" and self.frame >= len(self.frames[self.state]):
            self.state = "idle"

        # Change player's image based off the frame
        self.image = self.frames[self.state][int(self.frame % len(self.frames[self.state]))]

        # If player is facing left, flip his image horizontally
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        # If player is attacking and the frames ended, set the attack flag back to False
        if self.attack and self.frame >= len(self.frames[self.state]):
            self.attack = False

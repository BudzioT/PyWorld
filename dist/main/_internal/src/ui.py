import random

import pygame

from src.settings import settings
from src.sprites import AnimatedSprite
from src.timer import Timer


class UI:
    """User's interface class"""
    def __init__(self, frames, font):
        """Initialize the user's interface"""
        # Main surface
        self.surface = pygame.display.get_surface()

        # Sprites to help visualise items
        self.sprites = pygame.sprite.Group()

        # Font used in UI
        self.font = font

        # Health frames
        self.health_frames = frames["health"]
        # Width of them
        self.health_surface_width = self.health_frames[0].get_width()
        # Padding
        self.health_padding = 10

        # Current amount of coins
        self.coin_amount = 0
        # Coin surface
        self.coin_surface = frames["coin"]

        # Coin duration timer
        self.coin_duration = Timer(1000)

    def update(self, delta_time):
        """Update the user's interface icons and text"""
        # Update coin timer
        self.coin_duration.update()

        # Update all the sprites
        self.sprites.update(delta_time)

        # Draw the sprites
        self.sprites.draw(self.surface)
        # Draw all text
        self._show_text()

    def create_hearts(self, count):
        """Create hearts to indicate player's lives"""
        # Destroy the old hearts (to refresh the count)
        for heart in self.sprites:
            heart.kill()

        # Create given amount of hearts
        for heart_num in range(count):
            # Start with a left and top margin of 10, make them placed nicely
            pos_x = 10 + heart_num * (self.health_surface_width + self.health_padding)
            pos_y = 10
            # Create the heart
            Heart((pos_x, pos_y), self.health_frames, self.sprites)

    def _show_text(self):
        """Show all UI texts"""
        # Show the text, if coin timer is active
        if self.coin_duration.active:
            # Render the text
            text_surface = self.font.render(str(self.coin_amount), False, "#32423D")
            # Get its rectangle, set its position to top left with a little margin
            text_rect = text_surface.get_frect(topleft=(16, 34))

            # Blit the text
            self.surface.blit(text_surface, text_rect)

            # Create rectangle for displaying coin surface
            coin_rect = self.coin_surface.get_frect(center=text_rect.bottomleft)
            # Display the coin surface
            self.surface.blit(self.coin_surface, coin_rect)

    def update_coins(self, amount):
        """Update amount of coins currently displayed"""
        # Update the amount
        self.coin_amount = amount
        # Activate the coins duration timer
        self.coin_duration.start()


class Heart(AnimatedSprite):
    """Class representing a heart used to show player's health"""
    def __init__(self, pos, frames, group):
        """Create heart properties"""
        super().__init__(pos, frames, group)

        # Animation active flag
        self.active = False

    def _animate(self, delta_time):
        """Animate the heart"""
        # Increase frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # If animation hasn't ended, play the current frame
        if self.frame < len(self.frames):
            self.image = self.frames[int(self.frame)]

        # Otherwise deactivate it and reset the current frame
        else:
            self.active = False
            self.frame = 0

    def update(self, delta_time):
        """Update the heart"""
        # If heart animation is active, animate it
        if self.active:
            self._animate(delta_time)

        # Otherwise activate it at random
        else:
            if random.randint(0, 500) == 1:
                self.active = True

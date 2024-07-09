import pygame.sprite
from pygame.math import Vector2 as vector

from src.settings import settings


class Sprites(pygame.sprite.Group):
    """Group of all sprites"""
    def __init__(self):
        """Initialize the sprite group"""
        super().__init__()
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Offset of the camera
        self.offset = vector()

    def draw(self, target_pos):
        """Draw the sprites"""
        # Update the offset of the camera
        self.offset.x = -(target_pos[0] - settings.WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - settings.WINDOW_HEIGHT / 2)

        # Go through each of sprites, sort them by depth, for proper drawing
        for sprite in sorted(self, key=lambda element: element.pos_z):
            # Calculate the offset of this specific sprite
            offset = sprite.rect.topleft + self.offset
            # Blit them
            self.surface.blit(sprite.image, offset)

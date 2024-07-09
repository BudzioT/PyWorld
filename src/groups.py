import pygame.sprite
from pygame.math import Vector2 as vector

from src.settings import settings


class Sprites(pygame.sprite.Group):
    """Group of all sprites"""
    def __init__(self, level_width, level_height, bg_tile=None):
        """Initialize the sprite group"""
        super().__init__()
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Get dimensions from the level in pixels
        self.width = level_width * settings.TILE_SIZE
        self.height = level_height * settings.TILE_SIZE

        # If the level has a background, draw the background tiles

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

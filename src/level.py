import pygame

from src.settings import settings
from src.sprites import Sprite


class Level:
    """Level of the game"""
    def __init__(self, level_map):
        """Initialize the level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # All sprites group
        self.sprites = pygame.sprite.Group()

        # Initialize the level's map
        self._initialize(level_map)

    def run(self):
        """Run the level"""
        self._update_surface()

    def _update_surface(self):
        """Update level's surface"""
        # Clean the surface
        self.surface.fill("gray")

        # Draw all sprites
        self.sprites.draw(self.surface)

    def _initialize(self, level_map):
        """Initialize the map"""
        print(level_map)

        # Go through each terrain tiles and get its position as well as the surface
        for pos_x, pos_y, surface in level_map.get_layer_by_name("Terrain").tiles():
            print(pos_x, pos_y, surface)
            # Create a new sprite with this data, convert the position from tiles to pixels
            Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface, self.sprites)

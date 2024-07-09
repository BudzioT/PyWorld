import pygame

from src.settings import settings
from src.sprites import Sprite


class OverWorld:
    """Class representing game's overworld map"""
    def __init__(self, overworld_map, data, frames):
        """Initialize the overworld"""
        # Get game's surface
        self.surface = pygame.display.get_surface()

        # Save the game's data
        self.data = data

        # All sprites
        self.sprites = pygame.sprite.Group()

        # Create the overworld
        self._initialize(overworld_map, frames)

    def _initialize(self, overworld_map, frames):
        """Initialize and create the overworld map"""

        # Get the tiles and place them
        for tile in ["main", "top"]:
            # Go through each tile of that kind
            for pos_x, pos_y, surface in overworld_map.get_layer_by_name(tile).tiles():
                # Create and place it
                Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface, self.sprites,
                       settings.LAYERS_DEPTH["bg_tiles"])

    def run(self, delta_time):
        """Run the overworld"""
        # Update the positions
        self._update_positions(delta_time)

        # Draw all the game elements
        self._update_surface()

    def _update_positions(self, delta_time):
        """Update positions of the game elements"""
        # Update all sprites
        self.sprites.update(delta_time)

    def _update_surface(self):
        """Update the surface"""
        # Draw the sprites
        self.sprites.draw(self.surface)

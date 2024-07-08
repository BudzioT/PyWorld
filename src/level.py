import pygame

from src.settings import settings
from src.sprites import Sprite
from src.player import Player


class Level:
    """Level of the game"""
    def __init__(self, level_map):
        """Initialize the level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # All sprites group
        self.sprites = pygame.sprite.Group()
        # Sprites that collide
        self.collision_sprites = pygame.sprite.Group()

        # Initialize the level's map
        self._initialize(level_map)

    def run(self, delta_time):
        """Run the level"""
        # Update the level elements
        self._update_pos(delta_time)

        # Draw things
        self._update_surface()

    def _update_surface(self):
        """Update level's surface"""
        # Clean the surface
        self.surface.fill("gray")

        # Draw all sprites
        self.sprites.draw(self.surface)

    def _update_pos(self, delta_time):
        """Update position of all level elements"""
        # Update all the sprites
        self.sprites.update(delta_time)

    def _initialize(self, level_map):
        """Initialize the map"""

        # Go through each terrain tiles and get its position as well as the surface
        for pos_x, pos_y, surface in level_map.get_layer_by_name("Terrain").tiles():
            # Create a new sprite with this data, convert the position from tiles to pixels
            Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface,
                   (self.sprites, self.collision_sprites))

        # Get every object from the map file
        for obj in level_map.get_layer_by_name("Objects"):
            # If this object is a player, create him
            if obj.name == "player":
                Player((obj.x, obj.y), self.sprites, self.collision_sprites)

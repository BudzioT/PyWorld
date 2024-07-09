import random

import pygame

from src.settings import settings
from src.sprites import Sprite, AnimatedSprite, Node, Icon
from src.groups import WorldSprites


class OverWorld:
    """Class representing game's overworld map"""
    def __init__(self, overworld_map, data, frames):
        """Initialize the overworld"""
        # Get game's surface
        self.surface = pygame.display.get_surface()

        # Save the game's data
        self.data = data

        # All sprites
        self.sprites = WorldSprites(data)

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

        # Fill the map with water
        for row in range(overworld_map.height):
            for column in range(overworld_map.width):
                # Create an animated water sprite
                AnimatedSprite((column * settings.TILE_SIZE, row * settings.TILE_SIZE), frames["water"],
                               self.sprites, settings.LAYERS_DEPTH["bg"])

        # Place objects
        for obj in overworld_map.get_layer_by_name("Objects"):
            # If object is a palm, place it as an animated sprite with a random animation speed
            if obj.name == "palm":
                AnimatedSprite((obj.x, obj.y), frames["palm"], self.sprites, settings.LAYERS_DEPTH["main"],
                               random.randint(3, 6))
            # Otherwise place the grass in the background details depth or other objects in background tiles layer
            else:
                pos_z = settings.LAYERS_DEPTH[f'{"bg_details" if obj.name == "grass" else "bg_tiles"}']
                Sprite((obj.x, obj.y), obj.image, self.sprites, pos_z)

        # Create nodes and the player
        for node in overworld_map.get_layer_by_name("Nodes"):

            if node.name == "Node" and node.properties["stage"] == self.data.level:
                self.icon = Icon((node.x + settings.TILE_SIZE / 2, node.y + settings.TILE_SIZE / 2),
                                 frames["icon"], self.sprites)

            # If object is a node, create it with the given level property
            if node.name == "Node":
                Node((node.x, node.y), frames["path"]["node"], self.sprites, node.properties["stage"],
                     self.data)

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
        self.sprites.draw(self.icon.rect.center)

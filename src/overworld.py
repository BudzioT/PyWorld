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
        # Group of node sprites
        self.node_sprites = pygame.sprite.Group()

        # Create the overworld
        self._initialize(overworld_map, frames)

        # Current node the player's on (initialized to 0)
        self.node = [node for node in self.node_sprites if node.level == 0][0]

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

        # Get the paths
        # Prepare the paths dictionary
        self.paths = {}
        # Search through every path in the overworld
        for path in overworld_map.get_layer_by_name("Paths"):
            positions = []
            # Go through each point in the path and append it to the point positions list
            for point in path.points:
                positions.append((int(point.x + settings.TILE_SIZE / 2), int(point.y + settings.TILE_SIZE / 2)))

            # Save the start and the end of path
            start = path.properties["start"]
            end = path.properties["end"]

            # Set the path's end properties
            self.paths[end] = {"pos": positions, "start": start}

        # Create nodes and the player
        for node in overworld_map.get_layer_by_name("Nodes"):

            # If object is a node and its stage is current level
            if node.name == "Node" and node.properties["stage"] == self.data.level:
                # Draw the player icon there
                self.icon = Icon((node.x + settings.TILE_SIZE / 2, node.y + settings.TILE_SIZE / 2),
                                 frames["icon"], self.sprites)

            # If object is a node, create it with the given level property
            if node.name == "Node":
                # Get all the available paths to the node
                available_paths = {direction: value for direction, value in node.properties.items()
                                   if direction in ("left", "right", "up", "down")}

                # Create the node, pass it its level and the paths to it
                Node((node.x, node.y), frames["path"]["node"], (self.sprites, self.node_sprites),
                     node.properties["stage"], self.data, available_paths)

    def run(self, delta_time):
        """Run the overworld"""
        # Check and handle the input
        self._handle_input()

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

    def _handle_input(self):
        """Check and handle input"""
        # Get the pressed keys
        keys = pygame.key.get_pressed()

        # If there is a current node
        if self.node:
            # If user pressed down and node has a path down
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.node.can_move("down"):
                self._move_player("down")

    def _move_player(self, direction):
        """Move the player in the overworld"""
        # Get the path's key, change it to int (it's a string)
        path_key = int(self.node.paths[direction][0])
        # See if the path reverses (it has the 'r' character on the end)
        path_reverse = True if self.node.paths[direction][-1] == 'r' else False

        # Get the path points by the earlier got key, if the path isn't reversed
        if not path_reverse:
            path = self.paths[path_key]["pos"][:]
        # Otherwise get them reversed
        else:
            path = self.paths[path_key]["pos"][::-1]

        # Finally move the player through the generated path
        self.icon.move(path)

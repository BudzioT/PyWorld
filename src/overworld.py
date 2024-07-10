import random

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.sprites import Sprite, AnimatedSprite, Node, Icon, PathSprite
from src.groups import WorldSprites


class OverWorld:
    """Class representing game's overworld map"""
    def __init__(self, overworld_map, data, frames, switch):
        """Initialize the overworld"""
        # Get game's surface
        self.surface = pygame.display.get_surface()

        # Save the game's data
        self.data = data

        # Function to switch to a level
        self.switch = switch

        # All sprites
        self.sprites = WorldSprites(data)
        # Group of node sprites
        self.node_sprites = pygame.sprite.Group()

        # Create the overworld
        self._initialize(overworld_map, frames)

        # Current node the player's on (initialized to 0)
        self.node = [node for node in self.node_sprites if node.level == 0][0]

        # Get path frames
        self.path_frames = frames["path"]
        # Create paths
        self._create_path()

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
        # Get and change the current node
        self._change_node()

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

        # If there is a current node and player isn't on the path already
        if self.node and not self.icon.path:
            # If user pressed down and node has a path down
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.node.can_move("down"):
                self._move_player("down")
            # If user pressed up, move him that way if possible
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.node.can_move("up"):
                self._move_player("up")

            # Handle left movement
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.node.can_move("left"):
                self._move_player("left")
            # Right movement
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.node.can_move("right"):
                self._move_player("right")

            # On SPACE or RETURN, go to the level and store the last level
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.data.level = self.node.level
                self.switch("level")

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

    def _change_node(self):
        """Change the node of the player to the one he's on"""
        # All nodes player collides with
        nodes = pygame.sprite.spritecollide(self.icon, self.node_sprites, False)

        # If there were any collided nodes
        if nodes:
            # Set the player to the one he's on
            self.node = nodes[0]

    def _create_path(self):
        """Create the paths"""
        # Get the nodes in tiles (grid positions)
        nodes = {node.level: vector(node.grid_pos) for node in self.node_sprites}
        path_tiles = {}

        # Go through each path
        for path_id, data in self.paths.items():
            # Get the position of path
            path_pos = data["pos"]
            # Get the start node from it, save the current path node in the end node too
            start_node = nodes[data["start"]]
            end_node = nodes[path_id]

            # Save the first path
            path_tiles[path_id] = [start_node]

            # Go through each path position
            for index, points in enumerate(path_pos):
                # If current path has a start and end point
                if index < len(path_pos) - 1:
                    # Get them
                    start = vector(points)
                    end = vector(path_pos[index + 1])

                    # Get direction of the path, convert it to tiles
                    path_direction = (end - start) / settings.TILE_SIZE
                    # Save the starting tile
                    start_tile = vector(int(start[0] / settings.TILE_SIZE), int(start[1] / settings.TILE_SIZE))

                    # If there is vertical direction
                    if path_direction.y:
                        # Check if the path goes up or down
                        direction_y = 1 if path_direction.y > 0 else - 1

                        # Go through every next vertical tile in the current path
                        for pos_y in range(direction_y, int(path_direction.y) + direction_y, direction_y):
                            # Append the tile to the dictionary
                            path_tiles[path_id].append(start_tile + vector(0, pos_y))

                    # Otherwise, if there is a horizontal direction
                    if path_direction.x:
                        # Check if it goes left or right
                        direction_x = 1 if path_direction.x > 0 else -1

                        # Check every next horizontal tile and append it to the path tiles dictionary
                        for pos_x in range(direction_x, int(path_direction.x) + direction_x, direction_x):
                            path_tiles[path_id].append(start_tile + vector(pos_x, 0))
            # Append the end node
            path_tiles[path_id].append(end_node)

        # Go through each path tile that was created
        for path_id, path in path_tiles.items():
            # Check and place every path tile
            for index, tile in enumerate(path):
                # Ignore the first and last tile
                if 0 < index < len(path) - 1:
                    # Get the previous and next tile
                    previous_tile = path[index - 1] - tile
                    next_tile = path[index + 1] - tile

                    # If previous tile and next are on the vertical axes, give the proper surface
                    if previous_tile.x == next_tile.x:
                        surface = self.path_frames["vertical"]

                    # If they are horizontal, place the horizontal path
                    elif previous_tile.y == next_tile.y:
                        surface = self.path_frames["horizontal"]

                    # Otherwise there is a corner
                    else:
                        # Create a top left corner tile if needed
                        if (previous_tile.x == -1 and next_tile.y == -1
                                or previous_tile.y == -1 and next_tile.x == -1):
                            surface = self.path_frames["tl"]
                        # Create a bottom right one
                        elif (previous_tile.x == 1 and next_tile.y == 1
                              or previous_tile.y == 1 and next_tile.x == 1):
                            surface = self.path_frames["br"]
                        # Bottom left
                        elif (previous_tile.x == -1 and next_tile.y == 1
                              or previous_tile.y == 1 and next_tile.x == -1):
                            surface = self.path_frames["bl"]
                        # Top right
                        elif (previous_tile.x == 1 and next_tile.y == -1
                              or previous_tile.y == -1 and next_tile.x == 1):
                            surface = self.path_frames["tr"]
                        # Otherwise, create placeholder horizontal tile, something went wrong
                        else:
                            surface = self.path_frames["horizontal"]

                    # Create the tile
                    PathSprite((tile.x * settings.TILE_SIZE, tile.y * settings.TILE_SIZE), surface,
                               self.sprites, path_id)

from random import uniform

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.sprites import Sprite, MovingSprite, AnimatedSprite
from src.player import Player
from src.groups import Sprites


class Level:
    """Level of the game"""
    def __init__(self, level_map, level_frames):
        """Initialize the level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # All sprites group
        self.sprites = Sprites()
        # Sprites that collide
        self.collision_sprites = pygame.sprite.Group()
        # Semi collision sprites
        self.semi_collision_sprites = pygame.sprite.Group()
        # Sprites that deal damage
        self.damage_sprites = pygame.sprite.Group()

        # Initialize the level's map
        self._initialize(level_map, level_frames)

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
        self.sprites.draw(self.player.hitbox_rect)

    def _update_pos(self, delta_time):
        """Update position of all level elements"""
        # Update all the sprites
        self.sprites.update(delta_time)

    def _initialize(self, level_map, level_frames):
        """Initialize the map"""

        # Go through each layer and import it
        for layer in ["BG", "Terrain", "FG", "Platforms"]:
            # Group list depending on the layer
            groups = [self.sprites]

            # If tile is a terrain, give it just collision group
            if layer == "Terrain":
                groups.append(self.collision_sprites)
            # If it's a platform, make it semi collide-able
            elif layer == "Platforms":
                groups.append(self.semi_collision_sprites)

            # Check for depth position based off layer type
            # If it's a background tile, set it as one
            if layer == "BG":
                pos_z = settings.LAYERS_DEPTH["bg_tiles"]
            # Set foreground as background
            elif layer == "FG":
                pos_z = settings.LAYERS_DEPTH["bg_tiles"]
            # Otherwise just set it as main
            else:
                pos_z = settings.LAYERS_DEPTH["main"]

            # Get every tile of the layer, place it on the map
            for pos_x, pos_y, surface in level_map.get_layer_by_name(layer).tiles():
                # Create the tile
                Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE),
                       surface, groups, pos_z)

        # Go through each terrain tiles and get its position as well as the surface
        for pos_x, pos_y, surface in level_map.get_layer_by_name("Terrain").tiles():
            # Create a new sprite with this data, convert the position from tiles to pixels
            Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface,
                   (self.sprites, self.collision_sprites))

        # Get background details from the file
        for obj in level_map.get_layer_by_name("BG details"):
            # If object is static (doesn't have any animation), just create a normal sprite for it
            if obj.name == "static":
                Sprite((obj.x, obj.y), obj.image, self.sprites, settings.LAYERS_DEPTH["bg_tiles"])
            # Otherwise create animated ones
            else:
                AnimatedSprite((obj.x, obj.y), level_frames[obj.name], self.sprites,
                               settings.LAYERS_DEPTH["bg_tiles"])
                # If it was a candle, draw a light on top of it and move it back and up a little, to center it
                if obj.name == "candle":
                    AnimatedSprite((obj.x, obj.y) + vector(-20, -20), level_frames["candle_light"], self.sprites,
                                   settings.LAYERS_DEPTH["bg_tiles"])

        # Get every object from the map file
        for obj in level_map.get_layer_by_name("Objects"):
            # If this object is a player, create him
            if obj.name == "player":
                self.player = Player((obj.x, obj.y), level_frames["player"], self.sprites,
                                     self.collision_sprites, self.semi_collision_sprites)
            # Otherwise, if the object is some tile
            else:
                # Create a barrel or a crate, which aren't animated
                if obj.name in ("barrel", "crate"):
                    Sprite((obj.x, obj.y), obj.image, (self.sprites, self.collision_sprites))
                # Otherwise load frames of an object
                else:
                    # Import all object frames beside palms
                    if "palm" not in obj.name:
                        # Grab the frames from assets
                        frames = level_frames[obj.name]
                    # Import palms based off object name (there are many kinds of them)
                    else:
                        frames = level_frames["palms"][obj.name]

                    # Check if there are any inverted spikes
                    if obj.name == "floor_spike" and obj.properties["inverted"]:
                        # Invert all the frames
                        frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                    # Prepare list of groups
                    groups = [self.sprites]
                    # If the object is a small or a large palm, make it semi collide-able too
                    if obj.name in ("palm_small", "palm_large"):
                        groups.append(self.semi_collision_sprites)
                    # If object is a saw or floor spikes, append a damage group to it, to make them deal damage
                    if obj.name in ("saw", "floor_spike"):
                        groups.append(self.damage_sprites)

                    # Set the depth position based off the object name
                    # If object has background in name, change it to the background depth level
                    if "bg" in obj.name:
                        pos_z = settings.LAYERS_DEPTH["bg_details"]
                    # Otherwise set it as main one
                    else:
                        pos_z = settings.LAYERS_DEPTH["main"]

                    # Choose an animation speed, if the object is a palm, increment change it a little
                    if "palm" not in obj.name:
                        animation_speed = settings.ANIMATION_SPEED
                    else:
                        animation_speed = settings.ANIMATION_SPEED + uniform(-1, 1)

                    # Create an animated sprite
                    AnimatedSprite((obj.x, obj.y), frames, groups, pos_z, animation_speed)

        # Objects that can move
        for obj in level_map.get_layer_by_name("Moving Objects"):
            if obj.name == "spike":
                pass
            else:
                # Animation frames of moving objects
                frames = level_frames[obj.name]

                # If object is a platform, set it to semi collide-able one
                if obj.properties["platform"]:
                    groups = (self.sprites, self.semi_collision_sprites)
                # Otherwise make it a sprite that attacks the player
                else:
                    groups = (self.sprites, self.damage_sprites)

                # If its width is greater than its height, it is a horizontal-moving platform
                if obj.width > obj.height:
                    direction = 'x'
                    # Calculate middle horizontal start and end position of the platform
                    start_pos = (obj.x, obj.y + obj.height / 2)
                    end_pos = (obj.x + obj.width, obj.y + obj.height / 2)
                # Otherwise it's a vertical one
                else:
                    direction = 'y'
                    # Get the middle vertical start and end position of the platform
                    start_pos = (obj.x + obj.width / 2, obj.y)
                    end_pos = (obj.x + obj.width / 2, obj.y + obj.height)
                # Save speed from platform's properties
                speed = obj.properties["speed"]

                # Create the moving platform sprite
                MovingSprite(start_pos, end_pos, frames, direction, speed, groups)

                # If it's a saw, draw its path
                if obj.name == "saw":
                    # If it moves horizontally, handle it that way
                    if direction == 'x':
                        # Save saw's vertical position, it stays the same
                        pos_y = start_pos[1]
                        # Save the left and right side of saw's track
                        left = int(start_pos[0])
                        right = int(end_pos[0])
                        # Create the path
                        

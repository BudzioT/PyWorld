from random import uniform

import pygame
from pygame.math import Vector2 as vector

from src.settings import settings
from src.sprites import Sprite, MovingSprite, AnimatedSprite, Item
from src.player import Player
from src.groups import Sprites
from src.enemies import SpikeBall
from src.enemies import Tooth, Shell, Pearl
from src.particle import Particle


class Level:
    """Level of the game"""
    def __init__(self, level_map, level_frames, data):
        """Initialize the level"""
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Store the game's data
        self.data = data

        # Width of the level in pixels
        self.width = level_map.width * settings.TILE_SIZE
        # Bottom constraint of the level
        self.bottom = level_map.height * settings.TILE_SIZE

        # Get the level properties
        level_properties = level_map.get_layer_by_name("Data")[0].properties

        # If the level has background property, set it
        if level_properties["bg"]:
            bg_tile = level_frames["bg_tiles"][level_properties["bg"]]
        # Otherwise set it to None
        else:
            bg_tile = None

        # All sprites group
        self.sprites = Sprites(self.width, self.bottom,
                               {"small": level_frames["small_cloud"], "large": level_frames["large_cloud"]},
                               level_properties["horizon_line"], bg_tile, level_properties["top_limit"])
        # Sprites that collide
        self.collision_sprites = pygame.sprite.Group()
        # Semi collision sprites
        self.semi_collision_sprites = pygame.sprite.Group()
        # Sprites that deal damage
        self.damage_sprites = pygame.sprite.Group()

        # Tooth enemy sprites
        self.tooth_sprites = pygame.sprite.Group()
        # Pearl projectiles sprites
        self.pearl_sprites = pygame.sprite.Group()

        # Collectable item sprites
        self.item_sprites = pygame.sprite.Group()

        # Set the pearl surface
        self.pearl_surface = level_frames["pearl"]
        # Particle surfaces
        self.particle_frames = level_frames["particle"]

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

        # Handle pearl collisions
        self._pearl_collisions()
        # Check and handle player's collision, that result in damage
        self._damage_collisions()

        # Handle item collisions
        self._item_collisions()

        # Reflect the enemies if needed
        self._attack_collisions()

        # Constraint the player if needed
        self._check_constraints()

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
                                     self.collision_sprites, self.semi_collision_sprites, self.data)
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

                # If this is a flag, create finish level rectangle spot
                if obj.name == "flag":
                    self.finish_rect = pygame.FRect((obj.x, obj.y), (obj.width, obj.height))

        # Objects that can move
        for obj in level_map.get_layer_by_name("Moving Objects"):
            # Create a SpikeBall if that's the object
            if obj.name == "spike":
                SpikeBall((obj.x + obj.width / 2, obj.y + obj.height / 2), level_frames["spike_ball"],
                          (self.sprites, self.damage_sprites), obj.properties["radius"],
                          obj.properties["speed"], obj.properties["start_angle"], obj.properties["end_angle"])
                # Create its chain
                for radius in range(0, obj.properties["radius"], 20):
                    SpikeBall((obj.x + obj.width / 2, obj.y + obj.height / 2), level_frames["spike_chain"],
                              self.sprites, radius, obj.properties["speed"],
                              obj.properties["start_angle"], obj.properties["end_angle"],
                              settings.LAYERS_DEPTH["bg_details"])

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
                MovingSprite(start_pos, end_pos, frames, direction, speed, groups, obj.properties["flip"])

                # If it's a saw, draw its path
                if obj.name == "saw":
                    # If it moves horizontally, handle it that way
                    if direction == 'x':
                        # Save saw's vertical position, it stays the same
                        pos_y = start_pos[1] - level_frames["saw_chain"].get_height() / 2
                        # Save the left and right side of saw's track
                        left = int(start_pos[0])
                        right = int(end_pos[0])

                        # Create the path from multiple dots
                        for pos_x in range(left, right, 20):
                            Sprite((pos_x, pos_y), level_frames["saw_chain"], self.sprites,
                                   settings.LAYERS_DEPTH["bg_details"])

                    # Otherwise create a vertical path
                    else:
                        # Remain the saw's horizontal position, center it
                        pos_x = start_pos[0] - level_frames["saw_chain"].get_width() / 2

                        # Get the top and bottom saw's position
                        top = int(start_pos[1])
                        bottom = int(end_pos[1])

                        # Draw dots that indicate path from the most bottom saw position to the top one
                        for pos_y in range(top, bottom, 20):
                            Sprite((pos_x, pos_y), level_frames["saw_chain"], self.sprites,
                                   settings.LAYERS_DEPTH["bg_details"])

        # The rest of the enemies
        for enemy in level_map.get_layer_by_name("Enemies"):
            # Create a Tooth enemy
            if enemy.name == "tooth":
                Tooth((enemy.x, enemy.y), level_frames["tooth"], (self.sprites, self.damage_sprites,
                                                                  self.tooth_sprites),
                      self.collision_sprites)

            # Create a Shell enemy
            if enemy.name == "shell":
                Shell((enemy.x, enemy.y), level_frames["shell"], (self.sprites, self.collision_sprites),
                      enemy.properties["reverse"], self.player, self._create_pearl)

        # Spawn items
        for item in level_map.get_layer_by_name("Items"):
            Item((item.x + settings.TILE_SIZE / 2, item.y + settings.TILE_SIZE / 2),
                 level_frames["items"][item.name], (self.sprites, self.item_sprites), item.name, self.data)

        # Place the water tiles
        for water_tile in level_map.get_layer_by_name("Water"):
            # Calculate amount of rows and columns of water in tiles
            rows = int(water_tile.height / settings.TILE_SIZE)
            columns = int(water_tile.width / settings.TILE_SIZE)

            # Go through each row and column
            for row in range(rows):
                for column in range(columns):
                    # Calculate the position of water tile based off row and column, convert it to pixels
                    pos_x = water_tile.x + column * settings.TILE_SIZE
                    pos_y = water_tile.y + row * settings.TILE_SIZE

                    # If it's the first row of water tiles, create water tiles with animated waves
                    if row == 0:
                        AnimatedSprite((pos_x, pos_y), level_frames["water_top"], self.sprites,
                                       settings.LAYERS_DEPTH["water"])
                    # Otherwise create plain ones
                    else:
                        Sprite((pos_x, pos_y), level_frames["water"], self.sprites,
                               settings.LAYERS_DEPTH["water"])

    def _create_pearl(self, pos, direction):
        """Create a pearl shot by the shell"""
        Pearl(pos, self.pearl_surface, (self.sprites, self.damage_sprites, self.pearl_sprites),
              200, direction)

    def _pearl_collisions(self):
        """Check and handle pearl collisions"""
        # Check if pearl collides with any of the collide-able sprites, if so destroy it
        for sprite in self.collision_sprites:
            collided = pygame.sprite.spritecollide(sprite, self.pearl_sprites, True)
            # If there were any collisions, create a particle effect
            if collided:
                Particle(collided[0].rect.center, self.particle_frames, self.sprites)

    def _damage_collisions(self):
        """Check and handle player's collisions with sprites that deal damage"""
        # Go through each of the sprites that can damage the player
        for sprite in self.damage_sprites:
            # If it collides with the player, handle it
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.handle_damage()

                # If the damage sprite was a pearl, destroy it on contact
                if hasattr(sprite, "pearl"):
                    sprite.kill()
                    # Create a particle
                    Particle(sprite.rect.center, self.particle_frames, self.sprites)

    def _attack_collisions(self):
        """Handle the attack collisions"""
        # Go through each of the sprites that the player can reflect (pearls and Tooth enemies)
        for target in self.pearl_sprites.sprites() + self.tooth_sprites.sprites():
            # If player isn't flipped (is facing right)
            if not self.player.flip:
                # Save the facing target flag to True if the target is on the right of the player
                facing_target = self.player.rect.centerx < target.rect.centerx
            # Otherwise set it to True if the target is on the left
            else:
                facing_target = self.player.rect.centerx > target.rect.centerx

            # If target collides with player, player is attacking and is facing the target
            if target.rect.colliderect(self.player.rect) and self.player.attack and facing_target:
                # Reverse the target
                target.reverse()

    def _item_collisions(self):
        """Handle collisions with items and check them"""
        # If there are any items
        if self.item_sprites:
            # Check the collisions between them and the player
            item_collisions = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            # If there were any, collect the item
            if item_collisions:
                # Add proper boost
                item_collisions[0].collect()

                # Create a particle
                Particle(item_collisions[0].rect.center, self.particle_frames, self.sprites)

    def _check_constraints(self):
        """Check and constraint the player movement if he goes too far off the map"""
        # If player is behind left side of the map, move him back
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        # Do the same for the right side
        elif self.player.hitbox_rect.right >= self.width:
            self.player.hitbox_rect.right = self.width

        # Check if player went too far down
        if self.player.hitbox_rect.bottom > self.bottom:
            print("DIE")

        # Check if player touched the finish flag
        if self.player.hitbox_rect.colliderect(self.finish_rect):
            print("SUCCESS")

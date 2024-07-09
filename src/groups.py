import random

import pygame.sprite
from pygame.math import Vector2 as vector

from src.settings import settings
from src.sprites import Sprite, Cloud
from src.timer import Timer


class Sprites(pygame.sprite.Group):
    """Group of all sprites"""
    def __init__(self, level_width, level_height, clouds, horizon_line, bg_tile=None, top_limit=0):
        """Initialize the sprite group"""
        super().__init__()
        # Get the main surface
        self.surface = pygame.display.get_surface()

        # Get dimensions from the level in pixels
        self.width = level_width * settings.TILE_SIZE
        self.height = level_height * settings.TILE_SIZE

        # Create the background
        self._create_bg(bg_tile, level_width, level_height, int(top_limit / settings.TILE_SIZE) - 1)

        # Horizon line position
        self.horizon_line = horizon_line

        # Borders of the level
        self.borders = {
            "left": 0,
            # Add the window width, because player can't go outside of map, the camera should end sooner
            "right": -level_width + settings.WINDOW_WIDTH,
            "bottom": -level_height + settings.WINDOW_HEIGHT,
            "top": top_limit
        }

        # Sky flag
        self.sky = not bg_tile
        # Create sky if needed
        self._create_clouds(clouds)

        # Offset of the camera
        self.offset = vector()

    def draw(self, target_pos, delta_time):
        """Draw the sprites"""
        # Update the offset of the camera
        self.offset.x = -(target_pos[0] - settings.WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - settings.WINDOW_HEIGHT / 2)

        # Constraint the camera
        self._camera_constraint()

        # If there is sky, draw it
        if self.sky:
            # Draw the sky
            self._draw_sky()
            # Draw large clouds
            self._draw_large_clouds(delta_time)

            # Update the cloud appear timer
            self.cloud_timer.update()

        # Go through each of sprites, sort them by depth, for proper drawing
        for sprite in sorted(self, key=lambda element: element.pos_z):
            # Calculate the offset of this specific sprite
            offset = sprite.rect.topleft + self.offset
            # Blit them
            self.surface.blit(sprite.image, offset)

    def _camera_constraint(self):
        """Constraint the camera, when player moves too far"""
        # Change the offset if it's too far to the left
        if self.offset.x > self.borders["left"]:
            self.offset.x = self.borders["left"]
        # Change the offset to the right border, if it's too far
        if self.offset.x < self.borders["right"]:
            self.offset.x = self.borders["right"]

        # Check if the offset is too far to the bottom, if so, change it to be equal to the bottom of the level
        if self.offset.y < self.borders["bottom"]:
            self.offset.y = self.borders["bottom"]
        # Do the same for top
        if self.offset.y > self.borders["top"]:
            self.offset.y = self.borders["top"]

    def _create_bg(self, tile, level_width, level_height, top_limit):
        """Create the background with the given tile"""
        # If the level has a background, create the background tiles
        if tile:
            # Go through each column and row
            for row in range(-top_limit, level_height):
                for column in range(level_width):
                    # Get the tile position in pixels
                    pos_x = column * settings.TILE_SIZE
                    pos_y = row * settings.TILE_SIZE
                    # Create the background tile sprite
                    Sprite((pos_x, pos_y), tile, self, -1)

    def _create_clouds(self, clouds):
        """Create sky with clouds"""
        # If there isn't any background, create the clouds
        if self.sky:
            # Get the cloud assets
            self.small_clouds = clouds["small"]
            self.large_cloud = clouds["large"]

            # Direction of clouds
            self.cloud_direction = -1

            # Set the large cloud speed and position
            self.large_cloud_speed = 40
            self.large_cloud_x = 0

            # Set dimensions of the large clouds
            self.large_cloud_width = self.large_cloud.get_width()
            self.large_cloud_height = self.large_cloud.get_height()

            # Set the number of tiles that they can occupy
            self.large_cloud_tiles = int(self.width / self.large_cloud_width / settings.TILE_SIZE) + 2

            # Create clouds every 2,5 seconds, by calling the proper function
            self.cloud_timer = Timer(2500, self._create_small_cloud, True)
            # Start the timer
            self.cloud_timer.start()

            # Create 15 small clouds at the start
            for cloud_num in range(15):
                # Get a random position of a cloud
                pos = (random.randint(0, self.width / settings.TILE_SIZE),
                       random.randint(self.borders["top"], self.horizon_line))
                # Choose a random surface
                surface = random.choice(self.small_clouds)

                # Create a cloud
                Cloud(pos, surface, self)

    def _draw_sky(self):
        """Draw the sky"""
        # Fill the screen with the sky color
        self.surface.fill("#DDC6A1")

        # Get position of the horizon in the world
        horizon_pos = self.horizon_line + self.offset.y

        # Create rectangle indicating sea, up to the horizon line
        sea_rect = pygame.FRect(0, horizon_pos,
                                settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT - horizon_pos)
        # Draw the sea rectangle
        pygame.draw.rect(self.surface, "#92A9CE", sea_rect)

        # Draw the horizon line that goes through the entire screen with a width of 4
        pygame.draw.line(self.surface, "#F5F1DE",
                         (0, horizon_pos), (settings.WINDOW_WIDTH, horizon_pos), 4)

    def _draw_large_clouds(self, delta_time):
        """Draw large clouds and move them"""
        # Move the large cloud
        self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * delta_time

        # If clouds ended, set them back to horizontal position equal to 0
        if self.large_cloud_x <= -self.large_cloud_width:
            self.large_cloud_x = 0

        # Create as many clouds as there can be to fill width of the screen
        for cloud_num in range(self.large_cloud_tiles):
            # Get the left and top location
            left = self.large_cloud_x + self.large_cloud_width * cloud_num + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y

            # Blit the large cloud
            self.surface.blit(self.large_cloud, (left, top))

    def _create_small_cloud(self):
        """Create a random small cloud"""
        # Choose a random position from behind the right side of screen
        pos = (random.randint(self.width / settings.TILE_SIZE + 450, self.width / settings.TILE_SIZE + 600),
               random.randint(self.borders["top"], self.horizon_line))
        # Get a random cloud surface
        surface = random.choice(self.small_clouds)

        # Create a cloud with this information
        Cloud(pos, surface, self)


class WorldSprites(pygame.sprite.Group):
    """Sprites that appear in the overworld"""
    def __init__(self, data):
        """Initialize the overworld sprites"""
        super().__init__()

        # Get game's surface
        self.surface = pygame.display.get_surface()

        # Save data
        self.data = data

        # Create a camera offset vector
        self.offset = vector()

    def draw(self, pos):
        """Draw all the overworld sprites in group"""
        # Calculate offset based off the target position
        self.offset.x = -(pos[0] - settings.WINDOW_WIDTH / 2)
        self.offset.y = -(pos[1] - settings.WINDOW_HEIGHT / 2)

        # Go through each sprite sorted by depth value and draw the background
        for sprite in sorted(self, key=lambda element: element.pos_z):
            # Offset of sprites
            offset_pos = sprite.rect.topleft + self.offset

            # If given sprite is more in the background then the main objects, draw them
            if sprite.pos_z < settings.LAYERS_DEPTH["main"]:
                # If sprite depth is a path one
                if sprite.pos_z == settings.LAYERS_DEPTH["path"]:
                    # If the current level is unlocked, display the node
                    if sprite.level <= self.data.max_level:
                        self.surface.blit(sprite.image, offset_pos)
                # Draw the overworld sprite
                else:
                    self.surface.blit(sprite.image, offset_pos)

        # Check all the main objects and draw them in order based off vertical position
        for sprite in sorted(self, key=lambda element: element.rect.centery):
            

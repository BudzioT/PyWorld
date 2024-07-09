import pygame.sprite
from pygame.math import Vector2 as vector

from src.settings import settings
from src.sprites import Sprite


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

        # Sky flag
        self.sky = not bg_tile
        # Create sky if needed
        self._create_clouds(clouds)

        # Borders of the level
        self.borders = {
            "left": 0,
            # Add the window width, because player can't go outside of map, the camera should end sooner
            "right": -level_width + settings.WINDOW_WIDTH,
            "bottom": -level_height + settings.WINDOW_HEIGHT,
            "top": top_limit
        }

        # Offset of the camera
        self.offset = vector()

    def draw(self, target_pos):
        """Draw the sprites"""
        # Update the offset of the camera
        self.offset.x = -(target_pos[0] - settings.WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - settings.WINDOW_HEIGHT / 2)

        # Constraint the camera
        self._camera_constraint()

        # If there is sky, draw it
        if self.sky:
            self._draw_sky()

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

            # Set the large cloud variables
            self.large_cloud_speed = 40
            self.large_cloud_x = 0
            self.large_cloud_tiles = int(self.width / self.large_cloud.get_width() / settings.TILE_SIZE) + 2
            print(self.large_cloud_tiles)

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

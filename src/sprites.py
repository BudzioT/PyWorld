import pygame.sprite

from src.settings import settings


class Sprite(pygame.sprite.Sprite):
    """General sprite class"""
    def __init__(self, pos, surface, group):
        """Prepare the sprite"""
        super().__init__(group)

        # Create a basic surface with size the same as tiles
        self.image = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE))
        # Fill it with white color for test
        self.image.fill("white")

        # Get its rectangle as float for precision
        self.rect = self.image.get_frect(topleft=pos)
        # Store a copy of it for collisions
        self.last_rect = self.rect.copy()

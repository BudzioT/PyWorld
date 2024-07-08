import os

import pygame

from src.settings import settings


class Utilities:
    """Class that offers utilities"""
    def __init__(self):
        """Create utilities"""
        # Get file base path
        self.base_path = settings.BASE_PATH

    def load(self, path):
        """Load an image from absolute path"""
        return pygame.image.load(os.path.join(self.base_path, path))


# Instantiate utilities
utilities = Utilities()
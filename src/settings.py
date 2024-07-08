import sys
import os

import pygame


class Settings:
    """Settings of the game"""
    def __init__(self):
        """Initialize the settings"""
        # Window's dimensions
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720

        # Singular tile size
        self.TILE_SIZE = 64

        # Animation settings
        self.ANIMATION_SPEED = 5

        # Base file path
        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__))


# Settings instance
settings = Settings()

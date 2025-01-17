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

        # Layers with depth as value
        self.LAYERS_DEPTH = {
            "bg": 0,
            "clouds": 1,
            "bg_tiles": 2,
            "path": 3,
            "bg_details": 4,
            "main": 5,
            "water": 6,
            "fg": 7
        }


# Settings instance
settings = Settings()

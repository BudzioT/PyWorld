import sys
from os.path import join as path_join

import pygame
from pytmx.util_pygame import load_pygame

from src.settings import settings
from src.level import Level


class Game:
    """The entire game's class"""
    def __init__(self):
        """Create the game"""
        # Initialize pygame
        pygame.init()

        # Get main display surface
        self.surface = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Name it properly
        pygame.display.set_caption("PyWorld")

        # Load the maps
        self.maps = {0: load_pygame(path_join(settings.BASE_PATH, "../data/levels/omni.tmx"))}
        print(self.maps)

        # Current level
        self.current_level = Level(self.maps[0])

    def run(self):
        """Run the game"""
        # Game loop
        while True:
            # Handle events
            self._get_events()

            # Run the level
            self.current_level.run()

            # Update display
            self._update_surface()

    def _get_events(self):
        """Get and handle the game's events"""
        # Grab all the events
        for event in pygame.event.get():
            # If player wants to quit, let him do it
            if event.type == pygame.QUIT:
                # Free pygame resources
                pygame.quit()
                # Quit
                sys.exit()

    def _update_surface(self):
        """Update the display surface"""
        # Update the surface
        pygame.display.update()


# If it's a main file, run the game
if __name__ == "__main__":
    game = Game()
    game.run()

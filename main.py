import sys
from os.path import join as path_join

import pygame
from pytmx.util_pygame import load_pygame

from src.settings import settings
from src.level import Level
from src.utilities import utilities
from src.data import Data
from src.ui import UI
from src.overworld import OverWorld


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

        # FPS timer
        self.timer = pygame.time.Clock()

        # Import assets
        self._get_assets()

        # Game's user's interface
        self.ui = UI(self.ui_frames, self.font)

        # Data of the game
        self.data = Data(self.ui)

        # Load the maps
        self.maps = {0: load_pygame(path_join(settings.BASE_PATH, "../data/levels/omni.tmx"))}
        # Load the over-world map
        self.overworld_map = load_pygame(path_join(settings.BASE_PATH, "../data/overworld/overworld.tmx"))

        # Current level
        # self.current_level = Level(self.maps[0], self.level_frames, self.data)
        self.current_level = OverWorld(self.overworld_map, self.data, self.overworld_frames)

    def run(self):
        """Run the game"""
        # Game loop
        while True:
            # Remain the FPS at 60, save the delta time as milliseconds
            delta_time = self.timer.tick(60) / 1000

            # Handle events
            self._get_events()

            # Run the level
            self.current_level.run(delta_time)

            # Update display
            self._update_surface(delta_time)

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

    def _update_surface(self, delta_time):
        """Update the display surface"""
        # Update the user's interface and draw it
        self.ui.update(delta_time)

        # Update the surface
        pygame.display.update()

    def _get_assets(self):
        """Load and store the assets"""
        # Animation frames needed for a level
        self.level_frames = {
            # General frames
            "bg_tiles": utilities.load_folder_dict("../graphics/level/bg/tiles"),
            "flag": utilities.load_folder("../graphics/level/flag"),
            "water_top": utilities.load_folder("../graphics/level/water/top"),
            "water": utilities.load("../graphics/level/water/body.png"),
            "items": utilities.load_subfolders("../graphics/items"),
            "particle": utilities.load_folder("../graphics/effects/particle"),
            # Player
            "player": utilities.load_subfolders("../graphics/player"),
            # Enemies
            "saw": utilities.load_folder("../graphics/enemies/saw/animation"),
            "floor_spike": utilities.load_folder("../graphics/enemies/floor_spikes"),
            "spike_ball": utilities.load("../graphics/enemies/spike_ball/Spiked Ball.png"),
            "tooth": utilities.load_folder("../graphics/enemies/tooth/run"),
            "shell": utilities.load_subfolders("../graphics/enemies/shell"),
            "pearl": utilities.load("../graphics/enemies/bullets/pearl.png"),
            # Other objects
            "palms": utilities.load_subfolders("../graphics/level/palms"),
            "helicopter": utilities.load_folder("../graphics/level/helicopter"),
            "boat": utilities.load_folder("../graphics/objects/boat"),
            # Background details
            "candle": utilities.load_folder("../graphics/level/candle"),
            "candle_light": utilities.load_folder("../graphics/level/candle light"),
            "window": utilities.load_folder("../graphics/level/window"),
            "big_chain": utilities.load_folder("../graphics/level/big_chains"),
            "small_chain": utilities.load_folder("../graphics/level/small_chains"),
            "saw_chain": utilities.load("../graphics/enemies/saw/saw_chain.png"),
            "spike_chain": utilities.load("../graphics/enemies/spike_ball/spiked_chain.png"),
            "small_cloud": utilities.load_folder("../graphics/level/clouds/small"),
            "large_cloud": utilities.load("../graphics/level/clouds/large_cloud.png")
        }

        # Frames for overworld map
        self.overworld_frames = {
            # General frames
            "water": utilities.load_folder("../graphics/overworld/water"),
            # Other objects frames
            "palm": utilities.load_folder("../graphics/overworld/palm")
        }

        # Create game's font with a size of 40
        self.font = pygame.font.Font(path_join(settings.BASE_PATH, "../graphics/ui/runescape_uf.ttf"), 40)

        # Frames for user's interface
        self.ui_frames = {
            "health": utilities.load_folder("../graphics/ui/heart"),
            "coin": utilities.load("../graphics/ui/coin.png")
        }


# If it's a main file, run the game
if __name__ == "__main__":
    game = Game()
    game.run()

import os

import pygame

from src.settings import settings


class Utilities:
    """Class that offers utilities"""
    def __init__(self):
        """Create utilities"""
        # Get file base path
        self.base_path = settings.BASE_PATH

    def load(self, path, alpha=True):
        """Load an image from absolute path"""
        # If user wants to convert alpha, do it
        if alpha:
            return pygame.image.load(os.path.join(self.base_path, path)).convert_alpha()
        # Otherwise just load it normally
        else:
            return pygame.image.load(os.path.join(self.base_path, path))

    def load_folder(self, path):
        """Load an entire folder of images"""
        # Prepare frames list
        frames = []

        # Walk through each entry in the given path
        for dir_path, folders, images in os.walk(str(os.path.join(settings.BASE_PATH, path))):
            # Go through each image, sorted by name (names are indexes of frames)
            for image in sorted(images, key=lambda name: int(name.split('.')[0])):
                # Save its full, absolute path
                full_path = os.path.join(settings.BASE_PATH, dir_path, image)
                # Append it to the frames list after converting alpha
                frames.append(pygame.image.load(full_path).convert_alpha())

        # Return the ready list
        return frames

    def load_folder_dict(self, path):
        """Load folder of images and save it as a dictionary"""
        # Prepare the dictionary
        frames_dict = {}

        # Walk through every file in given path
        for dir_path, folders, images in os.walk(str(os.path.join(settings.BASE_PATH, path))):
            # Check every image
            for image in images:
                # Get its full path
                full_path = os.path.join(settings.BASE_PATH, dir_path, image)
                # Load it, convert alpha and append to the dictionary
                surface = pygame.image.load(full_path).convert_alpha()
                frames_dict[image.split('.')[0]] = surface

        return frames_dict

    def load_subfolders(self, path):
        """Load subfolders from the given path, store them in a dictionary"""
        frames_dict = {}
        # Walk through the path
        for files, folders, file in os.walk(str(os.path.join(settings.BASE_PATH, path))):
            # If there are any folders
            if folders:
                # Search every one of them, save its path
                for folder in folders:
                    print(path + '/' + folder)
                    # Load it into dictionary
                    frames_dict[folder] = self.load_folder(path + '/' + folder)

        return frames_dict


# Instantiate utilities
utilities = Utilities()
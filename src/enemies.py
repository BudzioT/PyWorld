import math

from src.sprites import Sprite
from src.settings import settings


class SpikeBall(Sprite):
    """Spike ball that moves in semicircular directions, damage player"""
    def __init__(self, pos, surface, group, radius, speed, start_angle, end_angle,
                 pos_z=settings.LAYERS_DEPTH["main"]):
        """Create the spike ball"""
        # Center of the spike
        self.center = pos
        # It's speed
        self.speed = speed

        # Start, current and end angles of the spike ball
        self.start_angle = start_angle
        self.angle = start_angle
        self.end_angle = end_angle

        # If angle is specified as -1, do set the circular flag to True, otherwise don't do full circular movement
        self.circular = True if self.end_angle == -1 else False

        # Radius of the spike ball movement
        self.radius = radius
        # Direction of it
        self.direction = 1

        # Calculate the horizontal and vertical position based off trigonometry rules
        pos_x = self.center[0] + math.cos(math.radians(self.angle)) * self.radius
        pos_y = self.center[1] + math.sin(math.radians(self.angle)) * self.radius
        # Initialize the parent sprite with them
        super().__init__((pos_x, pos_y), surface, group, pos_z)

    def update(self, delta_time):
        """Update spike ball"""
        # Get its new angle
        self.angle += self.direction * self.speed * delta_time

        # Set the direction based off the type of movement
        if not self.circular:
            # If current angle exceeded the end one, set it in the direction of the start angle
            if self.angle >= self.end_angle:
                self.direction = -1
            # Otherwise, if it is lower than the start angle, set it to go near the end one
            if self.angle < self.start_angle:
                self.direction = 1

        # Recalculate the positions
        pos_x = self.center[0] + math.cos(math.radians(self.angle)) * self.radius
        pos_y = self.center[1] + math.sin(math.radians(self.angle)) * self.radius

        # Set the new position of the rectangle
        self.rect.center = (pos_x, pos_y)

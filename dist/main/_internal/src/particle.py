from src.sprites import AnimatedSprite
from src.settings import settings


class Particle(AnimatedSprite):
    """Singular particle effect"""
    def __init__(self, pos, frames, group):
        """Initialize the particle"""
        super().__init__(pos, frames, group)

        # Center the particle
        self.rect.center = pos
        # Set its depth
        self.pos_z = settings.LAYERS_DEPTH["fg"]

    def _animate(self, delta_time):
        """Animate the particle sprite"""
        # Increase the current used frame
        self.frame += self.animation_speed * delta_time

        # If there are still frames, set the image to the current one
        if self.frame < len(self.frames):
            self.image = self.frames[int(self.frame)]
        # Otherwise kill the particle
        else:
            self.kill()

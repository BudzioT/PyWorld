from pygame.time import get_ticks


class Timer:
    """Simple timer class"""
    def __init__(self, duration, function=None, loops=False):
        """Initialize the timer"""
        # Duration of it
        self.duration = duration
        # Start time
        self.start_time = 0
        # Active flag
        self.active = False

        # Repeat flag
        self.loops = loops

        # Function to call
        self.function = function

    def start(self):
        """Start the timer"""
        # Set the active flag to true
        self.active = True
        # Get the start time to count duration
        self.start_time = get_ticks()

    def stop(self):
        """Stop the timer"""
        # Reset the active flag and the start time
        self.active = False
        self.start_time = 0

        # Check if the timer should repeat, if so start it again
        if self.loops:
            self.start()

    def update(self):
        """Update time on the timer"""
        # Get the current time
        current_time = get_ticks()

        # Calculate and check if duration has already passed from the start time
        if current_time - self.start_time >= self.duration:
            # If the timer was on and a function was given, call it
            if self.function and self.start_time != 0:
                self.function()
            # Stop the timer
            self.stop()

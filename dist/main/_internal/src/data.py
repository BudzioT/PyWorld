class Data:
    """Class that provides data for the game"""
    def __init__(self, ui):
        """Prepare the data"""
        # User's interface to write data to
        self.ui = ui

        # Player's amount of coins
        self._coins = 0
        # Player's amount of lives
        self._health = 5

        # Current level
        self.level = 0
        # The highest unlocked level
        self.max_level = 0

        # Create starting hearts
        self.ui.create_hearts(self._health)

    @property
    def health(self):
        """Get the health"""
        return self._health

    @health.setter
    def health(self, value):
        """Set the health"""
        # Set the amount of health
        self._health = value
        # Create the health sprites in user's interface
        self.ui.create_hearts(value)

    @property
    def coins(self):
        """Get the current amount of coins"""
        return self._coins

    @coins.setter
    def coins(self, value):
        """Set the amount of coins"""
        # Set current coins
        self._coins = value

        # If player collected 100 coins or more
        if self._coins >= 100:
            # Subtract 100 coins from him
            self._coins -= 100
            # Increase his health
            self._health += 1

        # Update the amount in UI
        self.ui.update_coins(self._coins)

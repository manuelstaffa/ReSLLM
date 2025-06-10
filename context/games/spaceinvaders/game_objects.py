class Player(GameObject):
    """
    The player figure i.e., the laser cannon.
    """

    def __init__(self):
        super().__init__()
        self.rgb = 92, 186, 92  # green
        self._xy = 0, 185
        self.wh = 7, 10


class Alien(GameObject):
    """
    The Space Invaders.
    """

    def __init__(self):
        super().__init__()
        self.rgb = 134, 134, 29
        self._xy = 0, 0
        self.wh = 8, 10


class Satellite(GameObject):
    """
    The Command Alien Ship.
    """

    def __init__(self):
        super().__init__()
        self.rgb = 151, 25, 122
        self._xy = 0, 0
        self.wh = 7, 8


class Shield(GameObject):
    """
    The shields between the player's cannon and the Space Invaders.
    """

    def __init__(self):
        super().__init__()
        self.rgb = 181, 83, 40
        self._xy = 0, 0
        self.wh = 8, 18


class Bullet(GameObject):
    """
    The player's laser beams and enemy laser bombs.
    """

    def __init__(self):
        super().__init__()
        self.rgb = 142, 142, 142
        self._xy = 0, 0
        self.wh = 1, 10


class Lives(GameObject):
    """
    The indicator for the player's remaining lives (HUD).
    """

    def __init__(self):
        super().__init__()
        self.rgb = 162, 134, 56
        self._xy = 84, 185
        self.wh = 12, 10

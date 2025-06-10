class Player(GameObject):
    """
    The player figure: Ms. Pac-Man.
    """

    def __init__(self):
        super(Player, self).__init__()
        self._xy = 78, 103
        self.wh = 9, 10
        self.rgb = 210, 164, 74


class Ghost(GameObject):
    """
    The Ghosts.
    """

    def __init__(self):
        super(Ghost, self).__init__()
        super().__init__()
        self._xy = 79, 57
        self.wh = 9, 10
        self.rgb = 200, 72, 72


class Fruit(GameObject):
    """
    The collectable fruits.
    """

    def __init__(self):
        super(Fruit, self).__init__()
        self._xy = 125, 173
        self.wh = 9, 10
        self.rgb = 184, 50, 50


class PowerPill(GameObject):
    """
    The collectable fruits.
    """

    def __init__(self):
        super(PowerPill, self).__init__()
        self._xy = 125, 173
        self.wh = 4, 7
        self.rgb = 228, 111, 111


class Life(GameObject):
    """
    The indicator for remaining lives (HUD).
    """

    def __init__(self):
        super(Life, self).__init__()
        self._xy = 12, 171
        self.wh = 7, 10
        self.rgb = 187, 187, 53

class Player(GameObject):
    """
    The player figure: Ms. Pac-Man.
    """

    def __init__(self):
        super(Player, self).__init__()
        self._xy = 78, 103
        self.wh = 8, 16
        self.rgb = 210, 164, 74


class Ghost(GameObject):
    """
    The Ghosts.
    """

    def __init__(self):
        super(Ghost, self).__init__()
        super().__init__()
        self._xy = 79, 57
        self.wh = 8, 16
        self.rgb = 252, 144, 200


pps = [(6, 39), (6, 171), (150, 39), (150, 171)]


class PowerPill(GameObject):
    """
    The collectable fruits.
    """

    def __init__(self, x=0, y=0):
        super(PowerPill, self).__init__()
        self._xy = x, y
        self.wh = 4, 10
        self.rgb = 228, 111, 111


class Life(GameObject):
    """
    The indicator for remaining lives (HUD).
    """

    def __init__(self):
        super(Life, self).__init__()
        self._xy = 8, 217
        self.wh = 20, 6
        self.rgb = 72, 176, 110
        self.hud = True
        self.value = 3

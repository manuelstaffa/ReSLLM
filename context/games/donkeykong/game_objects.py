class Player(GameObject):
    """
    The player figure: Mother Kangaroo.
    """

    def __init__(self):
        super(Player, self).__init__()
        self._xy = 43, 172
        self.wh = 8, 17
        self.rgb = 200, 72, 72


class Girlfriend(GameObject):
    """
    Mario's Girlfriend.
    """

    def __init__(self):
        super(Girlfriend, self).__init__()
        self._xy = 63, 18
        self.wh = 8, 16
        self.rgb = 84, 160, 197


class Barrel(GameObject):
    """
    The Monkey monkeys.
    """

    def __init__(self):
        super(Barrel, self).__init__()
        super().__init__()
        self._xy = 0, 0
        self.wh = 8, 8
        self.rgb = 236, 200, 96


class Hammer(GameObject):
    """
    The collectable fruits.
    """

    def __init__(self):
        super(Hammer, self).__init__()
        self._xy = 39, 68
        self.wh = 4, 7
        self.rgb = 236, 200, 96


class Ladder(GameObject):
    """
    The ladders.
    """

    def __init__(self, x=0, y=0):
        super(Ladder, self).__init__()
        self._xy = x, y
        self._prev_xy = x, y
        self.wh = 4, 17
        self.rgb = 181, 108, 224


class Platform(GameObject):
    """
    The platforms.
    """

    def __init__(self, x=0, y=0, w=8, h=4):
        super(Platform, self).__init__()
        self._xy = x, y
        self._prev_xy = x, y
        self.wh = w, h
        self.rgb = 162, 98, 33


class DonkeyKong(GameObject):
    """
    The donkey kong enemy.
    """

    def __init__(self):
        super(DonkeyKong, self).__init__()
        self._xy = 34, 15
        self.wh = 16, 19
        self.rgb = 181, 83, 40


class Life(GameObject):
    """
    The player's remaining lives (HUD).
    """

    def __init__(self):
        super(Life, self).__init__()
        self._xy = 116, 23
        self.wh = 12, 8
        self.rgb = 181, 108, 224
        self.value = 2

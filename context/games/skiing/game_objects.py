class Player(GameObject):
    """
    The player figure i.e., the skier.
    Orientation 0 is left, 7 and 8 are facing the slope and 15 is right.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 10, 18
        self.rgb = 214, 92, 92
        self.orientation = 8


class Flag(GameObject):
    """
    The poles (depicted as flags) of the gates.

    :ivar xy: Both positional coordinates x and y in a tuple.
    :type: (int, int)

    """

    def __init__(self, x=0, y=0):
        super().__init__()
        self.rgb = (10, 10, 255)
        self._xy = x + 4, y + 4
        self.wh = 5, 14


class Mogul(GameObject):
    """
    The moguls on the piste.

    :ivar xy: Both positional coordinates x and y in a tuple.
    :type: (int, int)

    """

    def __init__(self, x=0, y=0, subtype=None):
        super().__init__()
        self.rgb = (214, 214, 214)
        self._xy = x + 2, y + 3
        self.wh = 16, 7


class Tree(GameObject):
    """
    The trees on the piste.

    :ivar xy: Both positional coordinates x and y in a tuple.
    :type: (int, int)

    """

    def __init__(self, x=0, y=0):
        super().__init__()
        self.rgb = (110, 156, 66)
        self._xy = x, y
        self.wh = 16, 30


class Clock(GameObject):
    """
    The timer display (HUD).
    """

    def __init__(self, x=0, y=0, w=0, h=0):
        super().__init__()
        self._xy = x, y
        self.wh = w, h
        self.rgb = 0, 0, 0

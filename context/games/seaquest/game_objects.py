from enum import Enum


class Orientation(Enum):  # 16-wind compass directions
    N = 0
    NNE = 1
    NE = 2
    ENE = 3
    E = 4
    ESE = 5
    SE = 6
    SSE = 7
    S = 8
    SSW = 9
    SW = 10
    WSW = 11
    W = 12
    WNW = 13
    NW = 14
    NNW = 15


class Player(GameObject):
    """
    The player figure, i.e., the submarine.
    """

    def __init__(self):
        super().__init__()
        self._xy = 76, 46
        self.wh = 16, 11
        self.rgb = 187, 187, 53
        self.orientation = Orientation.E  # E is right, W is left


class Diver(GameObject):
    """
    The divers to be retrieved and rescued.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 8, 11
        self.rgb = 66, 72, 200


class Shark(GameObject):
    """
    The killer sharks.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 8, 7
        self.rgb = 92, 186, 92


class Submarine(GameObject):
    """
    The enemy submarines.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 8, 11
        self.rgb = 170, 170, 170


class EnemyMissile(GameObject):
    """
    The torpedoes fired from enemy submarines.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 6, 4
        self.rgb = 66, 72, 200


class PlayerMissile(GameObject):
    """
    The torpedoes launched from the player's submarine.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 8, 1
        self.rgb = 187, 187, 53


class Lives(ValueObject):
    """
    The indidcator for remaining reserve subs (lives) (HUD).
    """

    def __init__(self):
        super().__init__()
        self._xy = 58, 22
        self.rgb = 210, 210, 64
        self.wh = 23, 8
        self.value = 3


class OxygenBar(ValueObject):
    """
    The oxygen gauge (HUD).
    """

    def __init__(self):
        super().__init__()
        self._xy = 49, 170
        self.rgb = 214, 214, 214
        self.wh = 63, 5
        self.value = 100


class OxygenBarLogo(GameObject):
    """
    The 'OXYGEN' lettering next to the oxygen gauge (HUD).
    """

    def __init__(self):
        super().__init__()
        self._xy = 15, 170
        self.rgb = 0, 0, 0
        self.wh = 23, 5


class CollectedDiver(GameObject):
    """
    The indicator for collected divers (HUD). Varies between 0 and 6.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.rgb = 24, 26, 167
        self.wh = 8, 9

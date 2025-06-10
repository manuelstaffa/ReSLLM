class Player(GameObject):
    """
    The player figure: Mother Kangaroo.
    """

    def __init__(self):
        super(Player, self).__init__()
        self._xy = 78, 103
        self.wh = 8, 24
        self.rgb = 223, 183, 85


class Child(GameObject):
    """
    Baby Kangaroo.
    """

    def __init__(self):
        super(Child, self).__init__()
        self._xy = 78, 12
        self.wh = 8, 15
        self.rgb = 223, 183, 85


class Monkey(GameObject):
    """
    The Monkey monkeys.
    """

    def __init__(self):
        super(Monkey, self).__init__()
        super().__init__()
        self._xy = 79, 57
        self.wh = 6, 15
        self.rgb = 227, 159, 89


class Fruit(GameObject):
    """
    The collectable fruits.
    """

    def __init__(self):
        super(Fruit, self).__init__()
        self._xy = 125, 173
        self.wh = 7, 11
        self.rgb = 214, 92, 92


class Ladder(GameObject):
    """
    The ladders.
    """

    def __init__(self, x=0, y=0, w=8, h=36):
        super(Ladder, self).__init__()
        self._xy = x, y
        self._prev_xy = x, y
        self.wh = w, h
        self.rgb = 162, 98, 33


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


class FallingCoconut(GameObject):
    """
    The dangerous apples dropping down from the top.
    """

    def __init__(self):
        super(FallingCoconut, self).__init__()
        self._xy = 0, 0
        self.wh = 2, 3
        self.rgb = 162, 98, 33


class ThrownCoconut(GameObject):
    """
    The apples thrown at the player by the monkeys.
    """

    def __init__(self):
        super(ThrownCoconut, self).__init__()
        self._xy = 0, 0
        self.wh = 2, 3
        self.rgb = 227, 159, 89


class Bell(GameObject):
    """
    The bell that can be used to replenish the collectable fruits.
    """

    def __init__(self):
        super(Bell, self).__init__()
        self._xy = 126, 173
        self.wh = 6, 11
        self.rgb = 210, 164, 74

class Life(GameObject):
    """
    The player's remaining lives (HUD).
    """

    def __init__(self):
        super(Life, self).__init__()
        self._xy = 16, 183
        self.wh = 4, 7
        self.rgb = 160, 171, 79

class Time(ValueObject):
    """
    The time indicator (HUD).
    """

    def __init__(self):
        super(Time, self).__init__()
        self._xy = 80, 191
        self.wh = 15, 5
        self.rgb = 160, 171, 79
        self.value = 20

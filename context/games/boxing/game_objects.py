class Player(GameObject):
    """
    The player figure i.e., the boxer.


    :ivar right_arm_length: initial value: 0
    :ivar left_arm_length: initial value: 0
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 14, 46
        self.rgb = 214, 214, 214
        self.right_arm_length = 0
        self.left_arm_length = 0


class Enemy(GameObject):
    """
    The enemy boxer.

    :ivar right_arm_length: initial value: 0
    :ivar left_arm_length: initial value: 0
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 14, 46
        self.rgb = 0, 0, 0
        self.right_arm_length = 0
        self.left_arm_length = 0


class Clock(GameObject):
    """
    The game clock display (HUD).
    """

    def __init__(self, x=0, y=0, w=0, h=0):
        super().__init__()
        self._xy = x, y
        self.wh = w, h
        self.rgb = 20, 60, 0

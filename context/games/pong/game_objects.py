class Player(GameObject):
    """
    The player figure i.e., the movable bar at the side.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 4, 15
        self.rgb = 92, 186, 92


class Enemy(GameObject):
    """
    The enemy bar on the opposite side.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 4, 15
        self.rgb = 213, 130, 74


class Ball(GameObject):
    """
    The game ball.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 2, 4
        self.rgb = 236, 236, 236

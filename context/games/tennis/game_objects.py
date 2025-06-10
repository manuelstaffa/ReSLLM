class Player(GameObject):
    """
    The player figure i.e., the tennis player.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 13, 23
        self.rgb = 240, 128, 128


class Enemy(GameObject):
    """
    The enemy tennis player.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 13, 23
        self.rgb = 117, 128, 240


class Ball(GameObject):
    """
    The tennis ball.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 2, 2
        self.rgb = 236, 236, 236


class BallShadow(GameObject):
    """
    The shadow cast by the ball onto the ground.
    """

    def __init__(self):
        super().__init__()
        self._xy = 0, 0
        self.wh = 2, 2
        self.rgb = 74, 74, 74

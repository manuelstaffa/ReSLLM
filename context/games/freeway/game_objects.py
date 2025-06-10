MAX_NB_OBJECTS = {"Chicken": 2, "Car": 10}


class Chicken(GameObject):
    """
    The player figure i.e., the chicken.
    """

    def __init__(self):
        super(Chicken, self).__init__()
        self._xy = 0, 0
        self.wh = 6, 8
        self.rgb = 252, 252, 84


class Car(GameObject):
    """
    The vehicles on the freeway.
    """

    def __init__(self):
        super(Car, self).__init__()
        self._xy = 0, 0
        self.wh = 8, 10
        self.rgb = 167, 26, 26

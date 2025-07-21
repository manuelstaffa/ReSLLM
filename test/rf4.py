from ocatari.ram.freeway import *


def is_collision(chicken, car):
    """
    Determines if the chicken has collided with a car.

    :param chicken: A Chicken object.
    :param car: A Car object.
    :return: True if there is a collision, False otherwise.
    :rtype: bool
    """
    print("Checking collision between chicken at", chicken.y, "and car at", car.y)
    return chicken.is_on_top(car)


def get_chicken_position(chicken):
    """
    Retrieves the current y-coordinate of the chicken.

    :param chicken: A Chicken object.
    :return: The y-coordinate of the chicken.
    :rtype: int
    """
    return chicken.y


def get_chicken_progress(chicken):
    """
    Calculates the progress of the chicken towards the goal (top of the screen).

    :param chicken: A Chicken object.
    :return: The progress of the chicken as a float between 0 (bottom) and 1 (top).
    :rtype: float
    """
    screen_height = 187
    print(
        "Chicken Y Position:",
        chicken.y,
        "gives reward:",
        (screen_height - chicken.y) / screen_height,
    )
    # Calculate progress as a fraction of the
    return (screen_height - chicken.y) / screen_height


def reward_function(env):
    """
    Calculates the reward for the current state of the game.

    :param env: The game environment, which contains game objects.
    :return: The calculated reward.
    :rtype: float
    """
    game_objects = env.objects
    # print("Game Objects:", game_objects)
    reward = 0.0
    chicken = []
    cars = []

    # Separate the chicken and cars from game objects
    for obj in game_objects:
        if isinstance(obj, Chicken):
            chicken.append(obj)
        elif isinstance(obj, Car):
            cars.append(obj)

    chicken = chicken[0] if chicken else None
    # print("Chicken:", chicken.y if chicken else "None")

    # Check for collisions with any car
    if chicken:
        for car in cars:
            if is_collision(chicken, car):
                reward -= 1.0  # Penalize collision
                break

        # Reward for progress towards the top of the screen
        reward += get_chicken_progress(chicken)

    print("Reward:", reward)
    return reward

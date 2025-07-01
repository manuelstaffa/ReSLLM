from ocatari.ram.freeway import *


def check_collision(chicken, car):
    """
    Check if the chicken collides with a car.

    :param chicken: The chicken game object.
    :param car: The car game object.
    :return: True if there is a collision, False otherwise.
    """
    chicken_x1, chicken_y1 = chicken.x, chicken.y
    chicken_x2, chicken_y2 = chicken_x1 + chicken.w, chicken_y1 + chicken.h

    car_x1, car_y1 = car.x, car.y
    car_x2, car_y2 = car_x1 + car.w, car_y1 + car.h

    # Check if there is an overlap between the bounding boxes
    if (
        chicken_x1 < car_x2
        and chicken_x2 > car_x1
        and chicken_y1 < car_y2
        and chicken_y2 > car_y1
    ):
        return True
    return False


def reached_top(chicken, screen_height=160):
    """
    Check if the chicken has reached the top of the screen.

    :param chicken: The chicken game object.
    :param screen_height: The height of the screen.
    :return: True if the chicken has reached the top, False otherwise.
    """
    return chicken.y <= 0


def update_position(chicken, dx, dy):
    """
    Update the position of the chicken based on movement deltas.

    :param chicken: The chicken game object.
    :param dx: Change in x-coordinate.
    :param dy: Change in y-coordinate.
    """
    chicken.x += dx
    chicken.y += dy
    chicken._save_prev()  # Save the previous position


def is_moving(chicken):
    """
    Determine if the chicken is moving.

    :param chicken: The chicken game object.
    :return: True if the chicken is moving, False otherwise.
    """
    return chicken.dx != 0 or chicken.dy != 0


def reward_function(objects):
    """
    Calculate the reward for the agent based on the current game state.

    :param objects: List of all game objects currently in the game scene.
    :return: A numerical reward value.
    """
    # print(objects)
    objects = objects.objects
    # print(objects)
    # Initialize reward
    reward = 0

    # Identify the chicken controlled by the player and cars
    player_chicken = None
    cars = []

    for obj in objects:
        if (
            isinstance(obj, Chicken) and not obj.hud
        ):  # Assuming the player's chicken is not part of the HUD
            if player_chicken is None:  # First chicken found is the player's chicken
                player_chicken = obj
            else:
                # If there's another chicken, decide which one is the player's based on movement or position
                if (
                    obj.y < player_chicken.y
                ):  # Assume the player's chicken has moved further up
                    player_chicken = obj
        elif isinstance(obj, Car):
            cars.append(obj)

    # Check if the player's chicken has reached the top
    if player_chicken and reached_top(player_chicken):
        reward += 100  # Large reward for reaching the top

    # Check for collisions with cars
    if player_chicken:
        for car in cars:
            if check_collision(player_chicken, car):
                reward -= 10  # Penalty for collision

    # Encourage upward movement
    if player_chicken and player_chicken.dy < 0:  # dy < 0 means moving up on the screen
        reward += 1

    # Discourage no movement or downward movement
    if player_chicken and player_chicken.dy >= 0:
        reward -= 1

    return reward

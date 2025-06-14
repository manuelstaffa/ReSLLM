from ocatari.ram.Freeway import *

def is_collision(chicken, car) -> bool:
    """
    Determines if the chicken and a car collide with each other.

    :param chicken: The chicken object.
    :param car: The car object.
    :return: True if the chicken and the car collide, False otherwise.
    """
    return (car.x <= chicken.x <= car.x + car.w) and (car.y <= chicken.y <= car.y + car.h)

def chicken_crossed(chicken) -> bool:
    """
    Checks if the chicken has successfully crossed the freeway.

    :param chicken: The chicken object.
    :return: True if the chicken has reached the top of the screen, False otherwise.
    """
    return chicken.y <= 0

def chicken_back_to_start(chicken) -> bool:
    """
    Checks if the chicken is at the starting position at the bottom of the screen.

    :param chicken: The chicken object.
    :return: True if the chicken is at the starting position, False otherwise.
    """
    return chicken.y >= 160 - chicken.h

def calculate_crossing_progress(chicken) -> float:
    """
    Calculates the progress of the chicken in crossing the freeway.

    :param chicken: The chicken object.
    :return: A float value representing the progress of the chicken on the screen (0.0 to 1.0).
    """
    return (160 - chicken.y) / 160

def reward_function(game_objects) -> float:
    """
    Computes the reward for the current state of the game.

    :param game_objects: List of game objects, including chickens and cars.
    :return: A floating point reward value.
    """
    chickens = [obj for obj in game_objects if isinstance(obj, Chicken)]
    cars = [obj for obj in game_objects if isinstance(obj, Car)]
    
    reward = 0.0

    for chicken in chickens:
        # Reward for progressing towards the top of the screen
        reward += calculate_crossing_progress(chicken)
        
        # Penalty for collision with any car
        for car in cars:
            if is_collision(chicken, car):
                reward -= 1.0  # Penalty for collision
            
        # Check if chicken has successfully crossed
        if chicken_crossed(chicken):
            reward += 10.0  # Large reward for successful crossing
            
        # Reset reward if chicken returns to start
        if chicken_back_to_start(chicken):
            reward = 0.0  # Reset reward if chicken goes back to start

    return reward


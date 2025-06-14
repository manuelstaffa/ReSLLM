from ocatari.ram.Freeway import *

class GameObject:
    # Predefined GameObject class (as provided).

class ValueObject(GameObject):
    # Predefined ValueObject class (as provided).

class Chicken(GameObject):
    # Predefined Chicken class (as provided).

class Car(GameObject):
    # Predefined Car class (as provided).

# Helper function to check collision between two game objects
def check_collision(obj1, obj2) -> bool:
    """
    Check if two game objects collide based on their bounding boxes.

    :param obj1: First game object.
    :param obj2: Second game object.
    :return: True if the objects collide, False otherwise.
    """
    return obj1.is_on_top(obj2)

# Helper function to calculate chicken's progress
def calculate_chicken_progress(chicken: Chicken) -> int:
    """
    Calculate how far the chicken has progressed from the start position.

    :param chicken: The chicken game object.
    :return: Progress score based on chicken's y position.
    """
    return chicken.y

# Function to calculate reward
def reward_function(game_objects) -> float:
    """
    Calculate the reward based on the game state.

    :param game_objects: List of game objects including chickens and cars.
    :return: Calculated reward.
    """
    reward = 0.0
    chickens = [obj for obj in game_objects if isinstance(obj, Chicken)]
    cars = [obj for obj in game_objects if isinstance(obj, Car)]

    for chicken in chickens:
        # Reward progress towards the top
        current_progress = calculate_chicken_progress(chicken)
        previous_progress = chicken.prev_xy[1]
        
        # Reward for moving upwards
        reward += max(0, previous_progress - current_progress)

        # Penalize collisions with cars
        for car in cars:
            if check_collision(chicken, car):
                reward -= 10  # Large penalty for collision

    return reward


import pygame
import math
import numpy as np
from settings import *


def is_car_on_road(car_rect):
    """
    Check if the car is within the road boundaries.

    Args:
        car_rect (pygame.Rect): The rectangle representing the car's position and size.

    Returns:
        bool: True if the car is within the road (inside the outer square and outside the inner square), False otherwise.
    """
    car_is_within_outer_square = outer_square.contains(car_rect)
    car_is_outside_inner_square = not inner_square.colliderect(car_rect)

    return car_is_within_outer_square and car_is_outside_inner_square


class CarLogic:
    """
    Represents the logic and behavior of a car in the simulation.

    Attributes:
        start_x (float): Initial x-coordinate of the car.
        start_y (float): Initial y-coordinate of the car.
        start_angle (float): Initial angle (in degrees) of the car.
        start_speed (float): Initial speed of the car.
        width (int): Width of the car.
        height (int): Height of the car.
        weights (list): List of weights for the car's neural network.
        checkpoints (list): List of tuples representing checkpoint coordinates.
        current_checkpoint_index (int): Index of the next checkpoint to reach.
        checkpoints_seen (int): Number of checkpoints passed by the car.
        EPSILON (float): Distance threshold to consider a checkpoint reached.
        ray_length (int): Maximum length of the raycast rays.
        max_turn_angle (float): Maximum angle the car can turn.
        game_over (bool): Indicates if the car has crashed or not.
        frames_alive (int): Number of frames the car has been alive.
    """

    def __init__(
        self,
        x,
        y,
        weights,
        angle=0,
        speed=5,
        ray_length=250,
        epsilon=50,
        max_turn_angle=25,
    ):
        """
        Initialize a new CarLogic instance.

        Args:
            x (float): Initial x-coordinate of the car.
            y (float): Initial y-coordinate of the car.
            weights (list): Weights for the car's neural network.
            angle (float, optional): Initial angle of the car in degrees.
            speed (float, optional): Initial speed of the car.
            ray_length (int, optional): Maximum length of the raycast rays.
            epsilon (float, optional): Distance threshold to consider a checkpoint reached.
            max_turn_angle (float, optional): Maximum angle the car can turn.
        """
        self.start_x = x
        self.start_y = y
        self.start_angle = angle
        self.start_speed = speed
        self.width, self.height = 20, 10
        self.weights = weights
        self.checkpoints = checkpoints
        self.current_checkpoint_index = 0
        self.checkpoints_seen = 0
        self.epsilon = epsilon
        self.ray_length = ray_length
        self.max_turn_angle = max_turn_angle
        self.reset()

    def reset(self):
        """
        Reset the car's position, angle, speed, and game state.
        """
        self.x = self.start_x
        self.y = self.start_y
        self.angle = self.start_angle
        self.speed = self.start_speed
        self.game_over = False
        self.frames_alive = 0
        self.current_checkpoint_index = 0
        self.checkpoints_seen = 0

    def update(self):
        """
        Update the car's position, speed, and check for collisions
        and checkpoints.
        """
        if not self.game_over:
            # Perform raycasting and normalize the values
            raycast_values = [x / self.ray_length for x in self.cast_all_rays()]

            # Update the car's speed based on the raycast values
            new_speed = (
                10 * 1 / (1 + math.exp(-np.dot(self.weights[4:7], raycast_values)))
            )

            # Smooth speed transition
            self.last_speed = self.speed * 0.75 + new_speed * 0.25
            self.speed = new_speed

            # Calculate the change in angle
            weighted_sum = np.dot(self.weights[:3], raycast_values)
            delta_angle = (
                self.weights[3] * self.max_turn_angle * math.tanh(weighted_sum)
            )
            self.add_angle(delta_angle)

            # Update the car's position
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))
            self.frames_alive += 1

            # Check for collision with road boundaries
            if not is_car_on_road(self.get_rect()):
                self.game_over = True
                self.speed = 0

            # Check if the car has reached the next checkpoint
            if self.current_checkpoint_index < len(self.checkpoints):
                checkpoint_x, checkpoint_y = self.checkpoints[
                    self.current_checkpoint_index
                ]
                if (
                    abs(self.x - checkpoint_x) < self.epsilon
                    and abs(self.y - checkpoint_y) < self.epsilon
                ):
                    self.current_checkpoint_index += 1
                    self.current_checkpoint_index %= len(self.checkpoints)
                    self.checkpoints_seen += 1

    def add_angle(self, degrees):
        """
        Add a given angle to the car's current angle, ensuring it stays within 0-360 degrees.

        Args:
            degrees (float): The angle in degrees to add to the car's current angle.
        """
        self.angle = (self.angle + degrees) % 360

    def get_rect(self):
        """
        Get the pygame.Rect representing the car's position and size.

        Returns:
            pygame.Rect: The rectangle representing the car's position
                         and size.
        """
        return pygame.Rect(
            self.x - self.width / 2, self.y - self.height / 2, self.width, self.height
        )

    def cast_all_rays(self):
        """
        Perform raycasting in three directions: straight, left, and right.

        Returns:
            list: A list of distances representing the length of the rays in
                  each direction.
        """
        ray_angles = [0, -30, 30]  # Straight, left, and right rays
        raycast_values = []

        for angle_offset in ray_angles:
            angle = self.angle + angle_offset
            raycast_values.append(self.cast_single_ray(angle))

        return raycast_values

    def cast_single_ray(self, angle):
        """
        Cast a single ray at the given angle and return the distance until it
        hits an obstacle.

        Args:
            angle (float): The angle in degrees at which to cast the ray.

        Returns:
            int: The distance from the car to the point where the ray hits
                 an obstacle.
        """
        ray_length = self.ray_length  # Maximum length of the ray
        ray_hit_distance = ray_length

        # Define the ray start point
        start_x, start_y = self.x, self.y

        # Cast ray and check collision with both squares
        for length in range(ray_length):
            end_x = start_x + length * math.cos(math.radians(angle))
            end_y = start_y - length * math.sin(math.radians(angle))

            # Check if the point is outside the outer square
            # or inside the inner square
            outer_collide = outer_square.collidepoint(end_x, end_y)
            inner_collide = inner_square.collidepoint(end_x, end_y)
            if not outer_collide or inner_collide:
                ray_hit_distance = length
                break

        return ray_hit_distance

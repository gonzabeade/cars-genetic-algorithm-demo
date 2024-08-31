import pygame
import sys
from car_logic import CarLogic
from car_renderer import CarRenderer
from genetic_algorithm import GeneticAlgorithm
from settings import *
import numpy as np


def init(cars_logic):
    for car_logic in cars_logic:
        car_logic.reset()


def main():
    # Initialize Pygame
    pygame.init()

    # Initialize font after Pygame has been initialized
    font = pygame.font.SysFont(None, 55)

    # Initialize the genetic algorithm
    num_cars = 10
    ga = GeneticAlgorithm(population_size=num_cars)

    max_fitness = 0

    for generation in range(generations):

        initial = -1
        cars_logic = [
            CarLogic(
                x=checkpoints[initial][0] + np.random.randint(-15, 15),
                y=checkpoints[initial][1] + np.random.randint(-15, 15),
                angle=np.random.randint(-30, 30),
                weights=ga.population[i],
                epsilon=epsilon,
            )
            for i in range(num_cars)
        ]
        cars_renderer = [CarRenderer(logic) for logic in cars_logic]

        init(cars_logic)

        # Run the simulation for a fixed number of frames or until all cars are dead
        for _ in range(max_generation_duration):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            window.fill(WHITE)
            pygame.draw.rect(window, GREY, outer_square)
            pygame.draw.rect(window, WHITE, inner_square)

            # text
            text = font.render(f"Generation {generation+1}", True, BLACK)
            window.blit(text, (10, 10))

            # Checkpoints
            for checkpoint in checkpoints:
                pygame.draw.circle(window, CYAN, checkpoint, 5)  # Draw checkpoint dots

            # Update each car's logic
            for car_logic in cars_logic:
                car_logic.update()

            # Draw the cars
            for car_renderer in cars_renderer:
                car_renderer.draw(window)

            # Check if all cars are in game over state
            if all(car_logic.game_over for car_logic in cars_logic):
                break

            pygame.display.flip()
            pygame.time.Clock().tick(30)

        # Evaluate fitness and generate new population
        fitness_scores = ga.evaluate_fitness(cars_logic)
        max_fitness = max(score for score in fitness_scores)
        best_index = np.argmax([score for score in fitness_scores])
        best_weights = ga.population[best_index]

        print(f"Generation {generation+1} - Max Aptitude: {max_fitness}")

        ga.generate_new_population(fitness_scores)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

        window.fill(WHITE)


if __name__ == "__main__":
    main()

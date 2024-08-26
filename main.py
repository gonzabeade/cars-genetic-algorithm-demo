import pygame
import sys
import math
import random
import numpy as np

# Initialize PyGame
pygame.init()

# Set up display
width, height = 500, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drive Multiple Cars on Square Road")

# Define colors
GREY = (169, 169, 169)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)  # Color for the front indicator
CYAN = (0, 255, 255)    # Color for checkpoints


# Define the road
inner_square_size = 200
outer_square_size = 400

# Number of generations 
generations = 10000
epsilon = 50
max_generation_duration = 125 

# Calculate the coordinates of the squares
inner_square = pygame.Rect((width - inner_square_size) // 2, (height - inner_square_size) // 2, inner_square_size, inner_square_size)
outer_square = pygame.Rect((width - outer_square_size) // 2, (height - outer_square_size) // 2, outer_square_size, outer_square_size)

# Font for displaying "GAME OVER"
font = pygame.font.SysFont(None, 55)

# Define checkpoints (order matters)
checkpoints = [
    (width // 2 , height // 2 - 150 ),
    (width // 2 + 150, height // 2 - 150),
    (width // 2 + 150, height // 2),
    (width // 2 + 150, height // 2 + 150),
    (width // 2, height // 2 + 150),
    (width // 2 - 150, height // 2 + 150),
    (width // 2 - 150, height // 2),
    (width // 2 - 150 , height // 2 - 150 ),

]

class CarLogic:
    def __init__(self, x, y, weights, angle=0, speed=5, ray_length=250, epsilon=50):
        self.start_x = x
        self.start_y = y
        self.start_angle = angle
        self.start_speed = speed
        self.width, self.height = 20, 10
        self.weights = weights
        self.checkpoints = checkpoints
        self.current_checkpoint_index = 0
        self.checkpoints_seen = 0
        self.EPSILON = epsilon  # Distance threshold to consider a checkpoint reached
        self.ray_length = 250
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.angle = self.start_angle
        self.speed = self.start_speed
        self.game_over = False
        self.frames_alive = 0
        self.current_checkpoint_index = 0
        self.checkpoints_seen = 0

    def update(self):
        
        if not self.game_over:
            raycast_values = [x / self.ray_length for x in self.raycast()]

            new_speed =  math.fabs(self.weights[7] * math.tanh(np.dot(self.weights[4:7], raycast_values)))

            self.last_speed = self.speed * 0.75 + new_speed * 0.25 
            self.speed = new_speed
            print(self.speed)
            weighted_sum = np.dot(self.weights[:3], raycast_values)
            delta_angle = self.weights[3] * math.tanh(weighted_sum)
            self.addAngle(delta_angle)
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))
            self.frames_alive += 1

            print(raycast_values, self.weights)

            # Check for collision
            if not is_car_on_road(self.get_rect()):
                self.game_over = True
                self.speed = 0
            
            # Check if the car is close to the current checkpoint
            if self.current_checkpoint_index < len(self.checkpoints):
                checkpoint_x, checkpoint_y = self.checkpoints[self.current_checkpoint_index]
                if (abs(self.x - checkpoint_x) < self.EPSILON and
                        abs(self.y - checkpoint_y) < self.EPSILON):
                    self.current_checkpoint_index += 1
                    self.checkpoints_seen += 1

    def addAngle(self, degrees):
        self.angle = (self.angle + degrees) % 360

    def get_rect(self):
        return pygame.Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height)
    
    def raycast(self):
        """Perform raycasting and return the distances for the three rays."""
        ray_angles = [0, -30, 30]  # Straight, left, and right rays
        raycast_values = []

        for angle_offset in ray_angles:
            angle = self.angle + angle_offset
            raycast_values.append(self.cast_ray(angle))

        return raycast_values
    
    def cast_ray(self, angle):
        """Cast a single ray at the given angle and return the distance."""
        ray_length = self.ray_length  # Maximum length of the ray
        ray_hit_distance = ray_length  # Start assuming the ray hits at max length

        # Define the ray start point
        start_x, start_y = self.x, self.y
        
        # Cast ray and check collision with both squares
        for length in range(ray_length):
            end_x = start_x + length * math.cos(math.radians(angle))
            end_y = start_y - length * math.sin(math.radians(angle))
            
            # Check if the point is outside the outer square or inside the inner square
            if not outer_square.collidepoint(end_x, end_y) or inner_square.collidepoint(end_x, end_y):
                ray_hit_distance = length
                break

        return ray_hit_distance


class CarRenderer:
    def __init__(self, logic):
        self.logic = logic
        self.surface = pygame.Surface((logic.width, logic.height), pygame.SRCALPHA)
        self.surface.fill(RED)
    
    def draw(self, surface):
        logic = self.logic
        # Rotate the car
        rotated_car = pygame.transform.rotate(self.surface, logic.angle)
        rotated_rect = rotated_car.get_rect(center=(logic.x, logic.y))
        
        # Draw the car
        surface.blit(rotated_car, rotated_rect.topleft)
        
        # Draw the front indicator (small triangle)
        front_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle))
        )
        left_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle + 120)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle + 120))
        )
        right_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle - 120)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle - 120))
        )
        
        pygame.draw.polygon(surface, YELLOW, [front_point, left_point, right_point])
        
        # Draw rays for visualization
        self.draw_rays(surface, logic.raycast())

    def draw_rays(self, surface, raycast_values):
        """Draw the rays with varying colors based on their distance."""
        logic = self.logic
        ray_angles = [0, -30, 30]

        for angle_offset, distance in zip(ray_angles, raycast_values):
            angle = logic.angle + angle_offset
            ray_length = distance  # Length of the ray is the distance hit
            alpha = int(255 * (1 - (distance / self.logic.ray_length)))  # Calculate alpha based on distance (closer = more solid)
            color = (0, 255, 0, alpha)  # Green with variable transparency

            end_x = logic.x + ray_length * math.cos(math.radians(angle))
            end_y = logic.y - ray_length * math.sin(math.radians(angle))

            # Create a transparent surface to draw the ray with variable alpha
            ray_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.line(ray_surface, color, (logic.x, logic.y), (end_x, end_y), 2)
            surface.blit(ray_surface, (0, 0))  # Blit the ray surface onto the main surface

def is_car_on_road(car_rect):
    car_is_within_outer_square = outer_square.contains(car_rect)
    car_is_outside_inner_square = not inner_square.colliderect(car_rect)

    return car_is_within_outer_square and car_is_outside_inner_square

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate=0.5, mutation_std=0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_std = mutation_std
        self.population = self.initialize_population()
    
    def initialize_population(self):
        # Initialize population with random weights w1, w2, w3, w4
        return [np.random.uniform(-5, 5, 8) for _ in range(self.population_size)]
    
    def evaluate_fitness(self, cars_logic):
        # Fitness function that considers checkpoints seen and distance to the next checkpoint
        fitness_scores = []
        for car_logic in cars_logic:
            fitness_scores.append(car_logic.frames_alive * car_logic.last_speed * car_logic.last_speed)
        
        return fitness_scores
    
    def select_parents(self, fitness_scores):
        # Convert fitness scores to probabilities
        total_fitness = sum(fitness_scores)
        probabilities = [score / total_fitness for score in fitness_scores]
        
        # Select two parents randomly based on fitness probabilities
        selected_indices = np.random.choice(len(self.population), size=2, replace=False, p=probabilities)
        return self.population[selected_indices[0]], self.population[selected_indices[1]]
    
    def crossover(self, parent1, parent2):
        # Perform crossover between two parents with each gene having a 50% chance of being selected from either parent
        child1 = np.array([np.random.choice([gene1, gene2]) for gene1, gene2 in zip(parent1, parent2)])
        child2 = np.array([np.random.choice([gene1, gene2]) for gene1, gene2 in zip(parent1, parent2)])
        return child1, child2
    
    def mutate(self, child):
        # Mutate each gene with a Gaussian noise with certain mutation rate
        for i in range(len(child)):
            if np.random.rand() < self.mutation_rate:
                child[i] += np.random.normal(0, self.mutation_std)
        return child
    
    def generate_new_population(self, fitness_scores):
        # Generate a new population from the current one
        new_population = []
        
        for _ in range(self.population_size // 2):
            parent1, parent2 = self.select_parents(fitness_scores)
            child1, child2 = self.crossover(parent1, parent2)
            new_population.append(self.mutate(child1))
            new_population.append(self.mutate(child2))
        
        self.population = new_population



def init(cars_logic):
    for car_logic in cars_logic:
        car_logic.reset()

def main():
    # Initialize the genetic algorithm
    num_cars = 10
    ga = GeneticAlgorithm(population_size=num_cars)
    
    max_fitness = 0
    
    for generation in range(generations):
        print(f"Generation {generation+1}")
        
        initial = np.random.randint(0, len(checkpoints))
        cars_logic = [
                CarLogic(
                    x=checkpoints[initial][0]+np.random.randint(-15, 15), 
                    y=checkpoints[initial][1]+np.random.randint(-15, 15), 
                    angle=np.random.randint(-180, 180),
                    weights=ga.population[i], 
                    epsilon=epsilon
                ) for i in range(num_cars)
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
        max_fitness = max(score for score in fitness_scores) # Use the first element of the tuple
        best_index = np.argmax([score for score in fitness_scores])
        best_weights = ga.population[best_index]
        
        # Print best fitness and genes
        print(f"Generation {generation+1} - Max Aptitude: {max_fitness}")
        
        ga.generate_new_population(fitness_scores)
        
        # Display current generation and max aptitude on the screen

        pygame.display.flip()
        pygame.time.Clock().tick(30)

        # Clear the screen for the next generation
        window.fill(WHITE)

if __name__ == "__main__":
    main()

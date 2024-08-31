import numpy as np


class GeneticAlgorithm:
    """
    A class that implements a simple genetic algorithm for evolving a population of weights.

    Attributes:
        population_size (int): The number of individuals in the population.
        mutation_rate (float): The probability that a gene will mutate.
        mutation_std (float): The standard deviation of the Gaussian mutation.
        population (list): The current population of individuals.
        generations (int): The number of generations that have passed.
    """

    def __init__(self, population_size, mutation_rate=0.5, mutation_std=1):
        """
        Initializes the GeneticAlgorithm with the given population size, mutation rate, and mutation standard deviation.

        Args:
            population_size (int): The number of individuals in the population.
            mutation_rate (float, optional): The probability that a gene will mutate.
            mutation_std (float, optional): The standard deviation of the Gaussian mutation.
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_std = mutation_std
        self.population = self.initialize_population()
        self.generations = 0

    def initialize_population(self):
        """
        Initializes the population with random weights for each individual.

        Returns:
            list: A list of numpy arrays, each representing an individual's weights.
        """
        return [np.random.uniform(-5, 5, 8) for _ in range(self.population_size)]

    def evaluate_fitness(self, cars_logic):
        """
        Evaluates the fitness of each individual in the population.

        The fitness function considers both the number of checkpoints seen and the last speed of the car.
        The formula used is: fitness = 0.01 + last_speed * (checkpoints_seen ** 2)
        This formula rewards individuals that pass more checkpoints, with a small constant (0.01) to ensure
        non-zero fitness scores. Higher speeds also contribute positively, but the number of checkpoints seen
        has a quadratic impact, making it the most significant factor.

        Args:
            cars_logic (list): A list of CarLogic objects representing the cars controlled by the individuals.

        Returns:
            list: A list of fitness scores corresponding to each individual in the population.
        """
        fitness_scores = []
        for car_logic in cars_logic:
            fitness_scores.append(
                0.01 + car_logic.last_speed * car_logic.checkpoints_seen**2
            )
        return fitness_scores

    def select_parents(self, fitness_scores):
        """
        Selects two parents from the population based on their fitness scores.

        The selection is done probabilistically, where individuals with higher fitness scores have a higher
        probability of being selected.

        Args:
            fitness_scores (list): A list of fitness scores for each individual in the population.

        Returns:
            tuple: A tuple containing two numpy arrays, each representing a parent's weights.
        """
        total_fitness = sum(fitness_scores)
        probabilities = [score / total_fitness for score in fitness_scores]

        selected_indices = np.random.choice(
            len(self.population), size=2, replace=True, p=probabilities
        )
        return (
            self.population[selected_indices[0]],
            self.population[selected_indices[1]],
        )

    def crossover(self, parent1, parent2):
        """
        Performs crossover between two parents to create two children.

        Each gene in the children has a 50% chance of being inherited from either parent.

        Args:
            parent1 (numpy.ndarray): The first parent's weights.
            parent2 (numpy.ndarray): The second parent's weights.

        Returns:
            tuple: A tuple containing two numpy arrays, each representing a child's weights.
        """
        child1 = np.array(
            [np.random.choice([gene1, gene2]) for gene1, gene2 in zip(parent1, parent2)]
        )
        child2 = np.array(
            [np.random.choice([gene1, gene2]) for gene1, gene2 in zip(parent1, parent2)]
        )
        return child1, child2

    def mutate(self, child):
        """
        Mutates a child's genes with a certain mutation rate and standard deviation.

        Each gene in the child has a probability of being altered by a Gaussian noise.

        Args:
            child (numpy.ndarray): The child's weights to be mutated.

        Returns:
            numpy.ndarray: The mutated child's weights.
        """
        for i in range(len(child)):
            if np.random.rand() < self.mutation_rate:
                child[i] += np.random.normal(0, self.mutation_std)
        return child

    def generate_new_population(self, fitness_scores):
        """
        Generates a new population by selecting parents, performing crossover, and applying mutation.

        This method also updates the mutation standard deviation over generations, gradually reducing it
        as the number of generations increases.

        Args:
            fitness_scores (list): A list of fitness scores for each individual in the population.
        """
        new_population = []

        for _ in range(self.population_size // 2):
            parent1, parent2 = self.select_parents(fitness_scores)
            child1, child2 = self.crossover(parent1, parent2)
            new_population.append(self.mutate(child1))
            new_population.append(self.mutate(child2))

        self.generations += 1
        self.mutation_std = (50 - self.generations) / 50
        self.mutation_std = 0 if self.mutation_std < 0 else self.mutation_std
        self.population = new_population

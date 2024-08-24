import pygame
import sys
import math
import random

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

# Define the road
inner_square_size = 200
outer_square_size = 400

# Calculate the coordinates of the squares
inner_square = pygame.Rect((width - inner_square_size) // 2, (height - inner_square_size) // 2, inner_square_size, inner_square_size)
outer_square = pygame.Rect((width - outer_square_size) // 2, (height - outer_square_size) // 2, outer_square_size, outer_square_size)

# Font for displaying "GAME OVER"
font = pygame.font.SysFont(None, 55)

class Car:
    def __init__(self, x, y, angle=0, speed=2):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.width, self.height = 20, 10
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.color = RED
        self.surface.fill(self.color)
        self.game_over = False
    
    def update(self, deltaAngle):
        if not self.game_over:
            self.addAngle(deltaAngle)
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))
            
            # Check for collision
            if not is_car_on_road(self.get_rect()):
                self.game_over = True
                self.speed = 0
                self.color = BLACK
                self.surface.fill(self.color)
    
    def addAngle(self, degrees):
        self.angle = (self.angle + degrees) % 360

    def get_rect(self):
        return pygame.transform.rotate(self.surface, self.angle).get_rect(center=(self.x, self.y))
    
    def draw(self, surface):
        rotated_car = pygame.transform.rotate(self.surface, self.angle)
        rotated_rect = rotated_car.get_rect(center=(self.x, self.y))
        surface.blit(rotated_car, rotated_rect.topleft)

def is_car_on_road(car_rect):
    return outer_square.contains(car_rect) and not car_rect.colliderect(inner_square)

def main():
    # Create multiple cars
    num_cars = 3
    cars = [Car(x=400, y=200, angle=random.randint(-5, 5)) for _ in range(num_cars)]

    # Run the game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get the keys currently pressed
        keys = pygame.key.get_pressed()

        # Update each car
        for car in cars:
            car.update(deltaAngle=random.randint(-15, 15))

        # Draw the road and the cars
        window.fill(WHITE)  # Fill background with white
        pygame.draw.rect(window, GREY, outer_square)
        pygame.draw.rect(window, WHITE, inner_square)
        
        # Draw each car
        for car in cars:
            car.draw(window)
        
        # Display "GAME OVER" message for any cars that are game over
        if any(car.game_over for car in cars):
            game_over_text = font.render("GAME OVER", True, BLACK)
            window.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(30)

if __name__ == "__main__":
    main()

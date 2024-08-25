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
YELLOW = (255, 255, 0)  # Color for the front indicator

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
        self.start_x = x
        self.start_y = y
        self.start_angle = angle
        self.start_speed = speed
        self.width, self.height = 20, 10
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.reset()

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.angle = self.start_angle
        self.speed = self.start_speed
        self.color = RED
        self.surface.fill(self.color)
        self.game_over = False
    
    def update(self, deltaAngle):
        if not self.game_over:
            self.addAngle(deltaAngle)
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))
            
            # Perform raycasting
            raycast_values = self.raycast()

            # Print raycast values for debugging
            print(f"RAYCAST VALUES: {raycast_values}")
            
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
        # Rotate the car
        rotated_car = pygame.transform.rotate(self.surface, self.angle)
        rotated_rect = rotated_car.get_rect(center=(self.x, self.y))
        
        # Draw the car
        surface.blit(rotated_car, rotated_rect.topleft)
        
        # Draw the front indicator (small triangle)
        front_point = (
            self.x + (self.width / 4) * math.cos(math.radians(self.angle)),
            self.y - (self.width / 4) * math.sin(math.radians(self.angle))
        )
        left_point = (
            self.x + (self.width / 4) * math.cos(math.radians(self.angle + 120)),
            self.y - (self.width / 4) * math.sin(math.radians(self.angle + 120))
        )
        right_point = (
            self.x + (self.width / 4) * math.cos(math.radians(self.angle - 120)),
            self.y - (self.width / 4) * math.sin(math.radians(self.angle - 120))
        )
        
        pygame.draw.polygon(surface, YELLOW, [front_point, left_point, right_point])
        
        # Draw rays for visualization
        self.draw_rays(surface, self.raycast())

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
        ray_length = 100  # Maximum length of the ray
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
    
    def draw_rays(self, surface, raycast_values):
        """Draw the rays with varying colors based on their distance."""
        ray_angles = [0, -30, 30]

        for angle_offset, distance in zip(ray_angles, raycast_values):
            angle = self.angle + angle_offset
            ray_length = distance  # Length of the ray is the distance hit
            alpha = int(255 * (1 - (distance / 100)))  # Calculate alpha based on distance (closer = more solid)
            color = (0, 255, 0, alpha)  # Green with variable transparency

            end_x = self.x + ray_length * math.cos(math.radians(angle))
            end_y = self.y - ray_length * math.sin(math.radians(angle))

            # Create a transparent surface to draw the ray with variable alpha
            ray_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.line(ray_surface, color, (self.x, self.y), (end_x, end_y), 2)
            surface.blit(ray_surface, (0, 0))  # Blit the ray surface onto the main surface

def is_car_on_road(car_rect):
    car_is_within_outer_square = outer_square.contains(car_rect)
    car_is_outside_inner_square = not inner_square.colliderect(car_rect)

    return car_is_within_outer_square and car_is_outside_inner_square

def init(cars):
    for car in cars:
        car.reset()

def main():
    # Create multiple cars
    num_cars = 5
    cars = [Car(x=400, y=200, angle=random.randint(-10, 10)) for _ in range(num_cars)]

    init(cars)  # Initialize cars at the start

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
        
        # Check if all cars are in game over state
        if all(car.game_over for car in cars):
            # Display "GAME OVER" message
            game_over_text = font.render("All dead, resetting...", True, BLACK)
            window.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds
            init(cars)  # Reset cars after game over

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(30)

        # Separate frames in the debug output
        print("------")

if __name__ == "__main__":
    main()

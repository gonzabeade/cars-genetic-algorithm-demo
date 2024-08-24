import pygame
import sys
import math

# Initialize PyGame
pygame.init()

# Set up display
width, height = 500, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Drive the Car on Square Road")

# Define colors
GREY = (169, 169, 169)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define the car's properties
car_width, car_height = 20, 10
car_speed = 2  # Speed of the car
car_angle = 0  # Start angle facing right

# Define the road
inner_square_size = 200
outer_square_size = 400
road_thickness = (outer_square_size - inner_square_size) // 2

# Calculate the coordinates of the squares
inner_square = pygame.Rect((width - inner_square_size) // 2, (height - inner_square_size) // 2, inner_square_size, inner_square_size)
outer_square = pygame.Rect((width - outer_square_size) // 2, (height - outer_square_size) // 2, outer_square_size, outer_square_size)

# Start the car inside the road (e.g., on the top edge of the inner square, moving right)
car_x = 200
car_y = 400

# Create the car surface
car_surface = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
car_surface.fill(RED)

# Font for displaying "GAME OVER"
font = pygame.font.SysFont(None, 55)

def is_car_on_road(car_rect):
    return outer_square.contains(car_rect) and not car_rect.colliderect(inner_square)
    
# Run the game loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_over:
        # Get the keys currently pressed
        keys = pygame.key.get_pressed()

        # Rotate the car with left/right arrow keys
        if keys[pygame.K_LEFT]:
            car_angle += 5
        if keys[pygame.K_RIGHT]:
            car_angle -= 5

        # Move the car forward with the space bar
        if keys[pygame.K_SPACE]:
            car_x += car_speed * math.cos(math.radians(car_angle))
            car_y -= car_speed * math.sin(math.radians(car_angle))

        # Draw the road and the car
        window.fill(WHITE)  # Fill background with white
        pygame.draw.rect(window, GREY, outer_square)
        pygame.draw.rect(window, WHITE, inner_square)

        # Rotate the car surface and get the new rect
        rotated_car = pygame.transform.rotate(car_surface, car_angle)
        rotated_rect = rotated_car.get_rect(center=(car_x, car_y))

        # Check for collision
        if not is_car_on_road(rotated_rect):
            game_over = True

        # Draw the rotated car on the screen
        window.blit(rotated_car, rotated_rect.topleft)
    else:
        # Display "GAME OVER" message
        game_over_text = font.render("GAME OVER", True, BLACK)
        window.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - game_over_text.get_height() // 2))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(30)

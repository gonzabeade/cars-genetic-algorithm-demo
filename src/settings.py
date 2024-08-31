import pygame

# Colors
GREY = (169, 169, 169)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Display
width, height = 500, 500
window = pygame.display.set_mode((width, height))

# Squares
inner_square_size = 300
outer_square_size = 400
inner_square = pygame.Rect(
    (width - inner_square_size) // 2,
    (height - inner_square_size) // 2,
    inner_square_size,
    inner_square_size,
)
outer_square = pygame.Rect(
    (width - outer_square_size) // 2,
    (height - outer_square_size) // 2,
    outer_square_size,
    outer_square_size,
)

# Checkpoints
offset = 175
checkpoints = [
    (width // 2 + offset, height // 2 - offset),
    (width // 2 + offset, height // 2),
    (width // 2 + offset, height // 2 + offset),
    (width // 2, height // 2 + offset),
    (width // 2 - offset, height // 2 + offset),
    (width // 2 - offset, height // 2),
    (width // 2 - offset, height // 2 - offset),
    (width // 2, height // 2 - offset),
]

# Other settings
generations = 10000
epsilon = 50
max_generation_duration = 250

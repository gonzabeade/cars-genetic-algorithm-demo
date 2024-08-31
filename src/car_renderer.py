import pygame
import math
from settings import *


class CarRenderer:
    def __init__(self, logic):
        self.logic = logic
        self.surface = pygame.Surface((logic.width, logic.height), pygame.SRCALPHA)
        self.surface.fill(RED)

    def draw(self, surface):
        logic = self.logic
        rotated_car = pygame.transform.rotate(self.surface, logic.angle)
        rotated_rect = rotated_car.get_rect(center=(logic.x, logic.y))
        surface.blit(rotated_car, rotated_rect.topleft)

        front_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle)),
        )
        left_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle + 120)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle + 120)),
        )
        right_point = (
            logic.x + (logic.width / 4) * math.cos(math.radians(logic.angle - 120)),
            logic.y - (logic.width / 4) * math.sin(math.radians(logic.angle - 120)),
        )

        pygame.draw.polygon(surface, YELLOW, [front_point, left_point, right_point])

        self.draw_rays(surface, logic.cast_all_rays())

    def draw_rays(self, surface, raycast_values):
        logic = self.logic
        ray_angles = [0, -30, 30]

        for angle_offset, distance in zip(ray_angles, raycast_values):
            angle = logic.angle + angle_offset
            ray_length = distance
            alpha = int(255 * (1 - (distance / self.logic.ray_length)))
            color = (0, 255, 0, alpha)

            end_x = logic.x + ray_length * math.cos(math.radians(angle))
            end_y = logic.y - ray_length * math.sin(math.radians(angle))

            ray_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.line(ray_surface, color, (logic.x, logic.y), (end_x, end_y), 2)
            surface.blit(ray_surface, (0, 0))

import pygame
from constants import *

class Building:
    def __init__(self, grid_x, grid_y, image_id, image):
        """
        Represents a placed building in the world.

        Args:
            grid_x (int): The top-left grid X coordinate.
            grid_y (int): The top-left grid Y coordinate.
            image_id (str): The ID of the building (e.g., "main_crystal").
            image (pygame.Surface): The already-scaled surface to draw.
        """
        self.image_id = image_id
        self.image = image

        self.game_size = image.get_width() // TILE_SIZE

        self.world_rect = pygame.Rect(
            grid_x * TILE_SIZE,
            grid_y * TILE_SIZE,
            self.game_size,
            self.game_size
        )

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.world_rect)
        surface.blit(self.image, screen_rect)


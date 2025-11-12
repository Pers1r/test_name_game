import pygame
from constants import *

class Building:
    def __init__(self, grid_x, grid_y, item_id, image):
        """
        Represents a placed building in the world.

        Args:
            grid_x (int): The top-left grid X coordinate.
            grid_y (int): The top-left grid Y coordinate.
            item_id (str): The ID of the building (e.g., "main_crystal").
            image (pygame.Surface): The already-scaled surface to draw.
        """
        self.item_id = item_id
        self.image = image

        self.game_size = image.get_width() // TILE_SIZE

        self.world_rect = pygame.Rect(
            grid_x * TILE_SIZE,
            grid_y * TILE_SIZE,
            self.game_size *TILE_SIZE,
            self.game_size *TILE_SIZE
        )

        self.health = 50 # All buildings have 50 health for now
        if item_id == "main_crystal":
            self.health = 200 # Make crystal stronger
        elif item_id == "work_branch":
            self.health = 30

    def take_damage(self, damage):
        """Applies damage to the building."""
        self.health -= damage

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.world_rect)
        surface.blit(self.image, screen_rect)


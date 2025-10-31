import pygame


from constants import *


class Tile:
    def __init__(self, grid_x, grid_y, ground_type="grass", is_walkable=True):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(grid_x, grid_y, TILE_SIZE, TILE_SIZE)

        self.color = "green"
        if self.tile_type == "water":
            self.color = "blue"
        elif self.tile_type == "rock":
            self.color = "grey"
    def draw(self, screen, camera):
        screen_rect = camera.set_target(self.world_rect)

        pygame.draw.rect(screen, self.color, screen_rect)


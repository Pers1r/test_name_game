import pygame


from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, is_walkable=True):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.is_walkable = is_walkable

        if self.tile_type == "water":
            self.color = "blue"
            self.is_walkable = False
        elif self.tile_type == "rock":
            self.color = "grey"
            self.is_walkable = False
        else:
            self.color = "green"
            self.is_walkable = True

    def draw(self, screen, camera):
        screen_rect = camera.set_target(self.world_rect)

        pygame.draw.rect(screen, self.color, screen_rect)


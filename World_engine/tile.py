import pygame


from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, is_walkable=True):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.color = "green"
        if self.tile_type == "watter":
            self.color = "blue"
        elif self.tile_type == "rock":
            self.color = "grey"
    def draw(self, screen, camera):
        screen_rect = camera.set_target(self.world_rect)

        pygame.draw.rect(screen, self.color, screen_rect)


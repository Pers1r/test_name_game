import pygame


from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, image):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.is_walkable = True

        self.image = image

        if "water" in self.tile_type:
            self.is_walkable = False
        elif "rock" in self.tile_type:
            self.is_walkable = False

    def draw(self, screen, camera):
        screen_rect = camera.set_target(self.world_rect)

        # pygame.draw.rect(screen, pygame.SRCALPHA, screen_rect)
        screen.blit(self.image, screen_rect)



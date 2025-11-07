import pygame


from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, image):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.is_walkable = False
        self.is_bullet_penetrable = False
        self._is_buildable = False

        if "water" in self.tile_type:
            self.color = "blue"
            self.is_bullet_penetrable = True
        elif "rock" in self.tile_type:
            self.color = "grey"

        elif "grass" in self.tile_type:
            self.color = "green"
            self.is_walkable = True
            self.is_bullet_penetrable = True

            self._is_buildable = True

        elif "wall" in self.tile_type:
            self.color = "grey"
            self.is_walkable = False
            self.is_bullet_penetrable = False
            self._is_buildable = False

        elif "turret" in self.tile_type:
            self.color = "red"
            self.is_walkable = False
            self.is_bullet_penetrable = False
            self._is_buildable = False

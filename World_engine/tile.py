import pygame
from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, image):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.building = None

        self._is_walkable_flag = False
        self._is_bullet_penetrable_flag = False
        self._is_buildable_flag = False
        self.health = float('inf') # Indestructible by default
        self.drop_item_id = None
        self.color = "grey" # Default color

        # --- Set properties based on tile_type ---
        if "water" in self.tile_type:
            self.color = "blue"
            self._is_bullet_penetrable_flag = True
        elif "rock" in self.tile_type:
            self.color = "grey"
            self.health = 10
            self.drop_item_id = "resource_stone"
        elif "grass" in self.tile_type:
            self.color = "green"
            self._is_walkable_flag = True
            self._is_bullet_penetrable_flag = True
            self._is_buildable_flag = True
        elif "wall" in self.tile_type:
            self.color = "grey"
            self.health = 20
            self.drop_item_id = "resource_stone"
        elif "turret" in self.tile_type:
            self.color = "red"
        elif self.tile_type == "cave_ground":
            self.color = "brown"
            self._is_walkable_flag = True
            self._is_bullet_penetrable_flag = True
            self._is_buildable_flag = True
        elif self.tile_type == "elevator_up":
            self.color = "cyan"
            self._is_walkable_flag = True
            self._is_bullet_penetrable_flag = True
        elif self.tile_type == "cave_stone":
            self.health = 10
            self.drop_item_id = "resource_stone"
        elif self.tile_type == "cave_coal":
            self.health = 10
            self.drop_item_id = "resource_coal"
        elif self.tile_type == "cave_iron":
            self.health = 15
            self.drop_item_id = "resource_iron"
        elif self.tile_type == "cave_brown_iron":
            self.health = 15
            self.drop_item_id = "resource_brown_iron"
        elif self.tile_type == "cave_silver":
            self.health = 20
            self.drop_item_id = "resource_silver"
        elif self.tile_type == "cave_gold":
            self.health = 20
            self.drop_item_id = "resource_gold"
        elif self.tile_type == "cave_ruby":
            self.health = 25
            self.drop_item_id = "resource_ruby"
        elif self.tile_type == "cave_diamond":
            self.health = 30
            self.drop_item_id = "resource_diamond"

    @property
    def is_walkable(self):
        """A tile is not walkable if a building is on it."""
        if self.building:
            return False
        return self._is_walkable_flag

    @property
    def is_buildable(self):
        """A tile is not buildable if a building is on it."""
        if self.building:
            return False
        return self._is_buildable_flag

    @property
    def is_bullet_penetrable(self):
        """A tile is not penetrable by bullets if a building is on it."""
        if self.building:
            return False
        return self._is_bullet_penetrable_flag

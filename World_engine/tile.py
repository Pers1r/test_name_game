import pygame
from constants import *


class Tile:
    def __init__(self, ground_type, world_x, world_y, image):
        self.tile_type = ground_type
        self.world_rect = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)

        self.is_walkable = False
        self.is_bullet_penetrable = False
        self._is_buildable = False
        self.health = float('inf') # Indestructible by default
        self.drop_item_id = None
        self.color = "grey" # Default color

        # --- Set properties based on tile_type ---
        if "water" in self.tile_type:
            self.color = "blue"
            self.is_bullet_penetrable = True

        elif "rock" in self.tile_type: # Overworld rock
            self.color = "grey"
            self.health = 10
            self.drop_item_id = "resource_stone"

        elif "grass" in self.tile_type:
            self.color = "green"
            self.is_walkable = True
            self.is_bullet_penetrable = True
            self._is_buildable = True

        elif "wall" in self.tile_type:
            self.color = "grey"
            self.health = 20 # Building walls
            self.drop_item_id = "resource_stone"

        elif "turret" in self.tile_type:
            self.color = "red"

        elif self.tile_type == "cave_ground":
            self.color = "brown"
            self.is_walkable = True
            self.is_bullet_penetrable = True
            self._is_buildable = True

        elif self.tile_type == "elevator_up":
            self.color = "cyan"
            self.is_walkable = True
            self.is_bullet_penetrable = True

        # --- Ores and Stone ---
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

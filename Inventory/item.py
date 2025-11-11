import pygame
from constants import *


class Item:
    """
    The base class for all items in the game (resources, tools, buildables).
    """
    def __init__(self, item_id, name, item_type, image, description=""):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type # 'buildable', 'resource', 'weapon', 'tool'
        self.image = image
        self.description = description


class BuildableItem(Item):
    """
    A subclass for items that can be placed in the world.
    """
    def __init__(self, item_id, name, item_type, image, description, build_image_id, game_size):
        super().__init__(item_id, name, "buildable", image, description)
        self.build_image_id = build_image_id
        self.game_size = game_size

        self.ghost_surface = None

    def get_ghost_surface(self, build_image_surfaces):
        """
        Gets or creates the semi-transparent ghost surface for this item.
        """
        if self.ghost_surface:
            return self.ghost_surface

        image = build_image_surfaces.get(self.build_image_id)
        if not image:
            size_px = self.game_size * TILE_SIZE
            image = pygame.Surface((size_px, size_px))
            image.fill((100, 0, 100)) # Bright purple error color
            print(f"Error: Could not find build image for {self.item_id}")

        self.ghost_surface = image.copy()
        self.ghost_surface.set_alpha(150)
        return self.ghost_surface

class ToolItem(Item):
    """
    A subclass for items that can be used as tools (e.g., to shoot, mine).
    """
    def __init__(self, item_id, name, image, description, shoot_delay, enemy_damage, block_damage):
        super().__init__(item_id, name, "tool", image, description)
        self.shoot_delay = shoot_delay # in milliseconds
        self.enemy_damage = enemy_damage
        self.block_damage = block_damage
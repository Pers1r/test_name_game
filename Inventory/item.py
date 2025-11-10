import pygame
from constants import *


class Item:
    def __init__(self, item_id, name, item_type, image, description=""):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type # 'buildable', 'resource', 'weapon', 'tool'
        self.image = image
        self.description = description


class BuildableItem(Item):
    def __init__(self, item_id, name, item_type, image, description, build_image_id, game_size):
        super().__init__(item_id, name, "buildable", image, description)
        self.build_image_id = build_image_id
        self.game_size = game_size

        self.ghost_surface = None

    def get_ghost_surface(self, build_image_surfaces):
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
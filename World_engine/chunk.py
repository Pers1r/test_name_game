import pygame
import noise
import random
from constants import *
from .tile import *

class Chunk:
    def __init__(self, chunk_x, chunk_y, tile_dictionary):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.tile_dictionary = tile_dictionary

        self.chunk = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

        self.surface = pygame.Surface((CHUNK_SIZE*TILE_SIZE, CHUNK_SIZE*TILE_SIZE), pygame.SRCALPHA)
        self.world_rect = self.surface.get_rect(
            topleft=(self.chunk_x*CHUNK_SIZE*TILE_SIZE, self.chunk_y*CHUNK_SIZE*TILE_SIZE)
        )

    def get_tile_name_by_context(self, world, base_type, x, y):
        if base_type == "water":
            mask = 0
            N  = world.get_base_type_at(x, y - 1) == "grass"
            S  = world.get_base_type_at(x, y + 1) == "grass"
            W  = world.get_base_type_at(x - 1, y) == "grass"
            E  = world.get_base_type_at(x + 1, y) == "grass"
            NW = world.get_base_type_at(x - 1, y - 1) == "grass"
            NE = world.get_base_type_at(x + 1, y - 1) == "grass"
            SW = world.get_base_type_at(x - 1, y + 1) == "grass"
            SE = world.get_base_type_at(x + 1, y + 1) == "grass"

            if N: mask += 1
            if S: mask += 2
            if W: mask += 4
            if E: mask += 8
            if NW: mask += 16
            if NE: mask += 32
            if SW: mask += 64
            if SE: mask += 128

            if mask == 0:
                return "water_default"  # No grass neighbors
            else:
                return f"water_grass_{mask}" # e.g., "water_grass_21"

        elif base_type == "grass":
            if random.randint(1,1000) < 200:
                return f"grass_default_{random.randint(2, 4)}"
            else:
                return "grass_default_1"

        # --- Rock (Simplified) ---
        elif base_type == "rock":
            return "rock_default"

        # Default fallback
        return "grass_default_1"

    def generate_terrain(self, world):
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):

                global_tile_x = (self.chunk_x * CHUNK_SIZE) + col
                global_tile_y = (self.chunk_y * CHUNK_SIZE) + row

                base_type = world.get_base_type_at(global_tile_x, global_tile_y)

                tile_name = self.get_tile_name_by_context(world, base_type, global_tile_x, global_tile_y)

                tile_image = self.tile_dictionary.get(tile_name)

                if not tile_image:
                    if "water" in tile_name: # e.g., "water_grass_99" doesn't exist
                        tile_image = self.tile_dictionary.get("water_default")
                    elif "grass" in tile_name:
                        tile_image = self.tile_dictionary.get("grass_default_1")
                    else:
                        tile_image = self.tile_dictionary.get("rock_default")

                world_x = global_tile_x * TILE_SIZE
                world_y = global_tile_y * TILE_SIZE

                self.chunk[row][col] = Tile(tile_name, world_x, world_y, tile_image)

                local_x = col * TILE_SIZE
                local_y = row * TILE_SIZE
                self.surface.blit(tile_image, (local_x, local_y))

    def update_tile_at(self, local_x, local_y, new_tile_name, tile_dictionary):
        new_tile_image = tile_dictionary.get(new_tile_name)
        if not new_tile_image:
            print(f"Error: Tile name '{new_tile_name}' not in dictionary.")
            new_tile_image = tile_dictionary.get("rock_default") # Fallback
            new_tile_name = "rock_default"

        world_x = (self.chunk_x * CHUNK_SIZE + local_x) * TILE_SIZE
        world_y = (self.chunk_y * CHUNK_SIZE + local_y) * TILE_SIZE

        new_tile = Tile(new_tile_name, world_x, world_y, new_tile_image)
        self.chunk[local_y][local_x] = new_tile

        draw_pos = (local_x * TILE_SIZE, local_y * TILE_SIZE)
        # Clear the old tile area (fill with a transparent color)
        self.surface.fill((0, 0, 0, 0), pygame.Rect(draw_pos, (TILE_SIZE, TILE_SIZE)))
        # Blit the new tile image
        self.surface.blit(new_tile_image, draw_pos)


    def draw(self, screen, camera):
        screen_rect = camera.set_target(self.world_rect)
        screen.blit(self.surface, screen_rect)




import pygame
import noise
from constants import *
from .tile import *
from .chunk import *



class World:
    def __init__(self, seed, tile_dictionary):
        self.chunks = {}
        self.seed = seed
        self.tile_dictionary = tile_dictionary

    def get_base_type_at(self, global_x, global_y):
        noise_value = noise.pnoise2(global_x*0.1, global_y*0.1, base=self.seed)

        if noise_value < -0.3:
            return "water"
        elif noise_value < 0.3:
            return "grass"
        else:
            return "rock"

    def get_or_generate_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) in self.chunks:
            return self.chunks[(chunk_x, chunk_y)]

        new_chunk = Chunk(chunk_x, chunk_y, self.tile_dictionary)
        new_chunk.generate_terrain(self)
        self.chunks[(chunk_x, chunk_y)] = new_chunk
        return new_chunk

    def get_tile_at_grid_pos(self, grid_x, grid_y):
        try:
            chunk_x = grid_x // CHUNK_SIZE
            chunk_y = grid_y // CHUNK_SIZE

            local_x = grid_x % CHUNK_SIZE
            local_y = grid_y % CHUNK_SIZE

            chunk = self.chunks.get((chunk_x, chunk_y))
            if chunk:
                return chunk.chunk[local_y][local_x]
        except (IndexError, TypeError):
            return None
        return None

    def get_collidable_tiles_near(self, player_rect):
        collidable_tiles = []
        grid_x = player_rect.centerx // TILE_SIZE
        grid_y = player_rect.centery // TILE_SIZE

        for y in range(grid_y - 1, grid_y + 2):
            for x in range(grid_x - 1, grid_x + 2):
                tile = self.get_tile_at_grid_pos(x, y)

                if tile and not tile.is_walkable:
                    collidable_tiles.append(tile)

        return collidable_tiles





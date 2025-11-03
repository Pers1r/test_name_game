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

    def get_or_generate_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) in self.chunks:
            return self.chunks[(chunk_x, chunk_y)]

        new_chunk = Chunk(chunk_x, chunk_y, self.tile_dictionary)
        new_chunk.generate_terrain(self.seed)
        self.chunks[(chunk_x, chunk_y)] = new_chunk
        return new_chunk

    # def get_visible_chunks(self, camera):
    #     camera_x= camera.rect.x//(CHUNK_SIZE*TILE_SIZE)
    #     camera_y= camera.rect.y//(CHUNK_SIZE*TILE_SIZE)
    #     visible_chunks = []
    #     for chunk in self.chunks.keys():
    #         if chunk[0] in [camera_x-1, camera_x, camera_x+1] and chunk[1] in [camera_y-1, camera_y, camera_y+1]:
    #             visible_chunks.append(chunk)
    #     return visible_chunks

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





import pygame
import noise
from constants import *
from .tile import *

class Chunk:
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y

        self.chunk = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]

    def generate_terrain(self, seed):
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):

                global_tile_x = (self.chunk_x * CHUNK_SIZE) + col
                global_tile_y = (self.chunk_y * CHUNK_SIZE) + row

                noise_value = noise.pnoise2(global_tile_x*0.1, global_tile_y*0.1, base=seed)

                if noise_value < -0.3:
                    tile_type = "watter"
                elif noise_value < 0.3:
                    tile_type = "grass"
                else:
                    tile_type = "rock"

                world_x = global_tile_x * TILE_SIZE
                world_y = global_tile_y * TILE_SIZE

                self.chunk[row][col] = Tile(tile_type, world_x, world_y)

    def draw(self, screen, camera):
        for row in self.chunk:
            for tile in row:
                if tile:
                    tile.draw(screen, camera)



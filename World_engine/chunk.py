import pygame
import noise
from constants import *
from .tile import *

class Chunk:
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.chunk = [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                self.chunk[row][col] = Tile(row, col)


    def generate_terrain(self, seed):
        for row in range(CHUNK_SIZE):
            for col in range(CHUNK_SIZE):
                global_tile_x = (self.chunk_x * CHUNK_SIZE) + row
                global_tile_y = (self.chunk_y * CHUNK_SIZE) + col

                noise_value = noise.pnoise2(global_tile_x*0.1, global_tile_y*0.1, base=seed)

                if noise_value < -0.3:
                    self.chunk[row][col].tile_type = "watter"
                elif noise_value < 0.3:
                    self.chunk[row][col].tile_type = "grass"
                else:
                    self.chunk[row][col].tile_type = "rock"

    def draw(self, screen, camera):
        for row in self.chunk:
            for tile in row:
                tile.draw(screen, camera)



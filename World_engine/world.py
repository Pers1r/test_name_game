import pygame
import noise
from constants import *
from .tile import *
from .chunk import *



class World:
    def __init__(self, seed):
        self.chunks = {}
        self.seed = seed

    def get_or_generate_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) in self.chunks:
            return self.chunks[(chunk_x, chunk_y)]

        new_chunk = Chunk(chunk_x, chunk_y)
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





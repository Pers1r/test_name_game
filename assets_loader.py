import pygame
from constants import *

tile_size = TILE_SIZE

TILE_ATLAS = {
    'grass_default_1': (0 * tile_size, 6 * tile_size, tile_size, tile_size),
    'grass_default_2': (1 * tile_size, 6 * tile_size, tile_size, tile_size),
    'grass_default_3': (2 * tile_size, 6 * tile_size, tile_size, tile_size),
    'grass_default_4': (3 * tile_size, 6 * tile_size, tile_size, tile_size),
    'water_default': (0 * tile_size, 13 * tile_size, tile_size, tile_size),
    'rock_default' : (7 * tile_size, 12 * tile_size, tile_size, tile_size),
}

def load_tiles_from_atlas(tileset_image, atlas_definition):
    tile_dictionary = {}
    print("Loading tiles...")

    for name, rect_coords in atlas_definition.items():
        print(f"  - Loading '{name}' from {rect_coords}")
        rect = pygame.Rect(rect_coords)

        tile_image = tileset_image.subsurface(rect).convert_alpha()
        tile_dictionary[name] = tile_image

    return tile_dictionary
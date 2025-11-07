import pygame
from constants import *

# This is our "database"
BUILD_DATA = {
    "wall": {
        "id": "wall",
        "name": "Wall",
        "keybind": pygame.K_1,
        "tile_name": "wall_tile", # The name of the tile to create
        "placeholder_color": (100, 100, 100) # Gray
    },
    "turret": {
        "id": "turret",
        "name": "Turret",
        "keybind": pygame.K_2,
        "tile_name": "turret_tile", # The name of the tile to create
        "placeholder_color": (200, 50, 50) # Red
    },
}
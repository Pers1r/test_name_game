import pygame
from constants import *

# This is our "database"
BUILD_DATA = {
    "main_crystal": {
        "id": "main_crystal",
        "name": "Main Crystal",
        "keybind": pygame.K_1,
        "image_id": "main_crystal",
        "game_size": 2
    },
    "work_branch": {
        "id": "work_branch",
        "name": "Workbench",
        "keybind": pygame.K_2,
        "image_id": "work_branch",
        "game_size": 1
    },
    "elevator_down": {
        "id": "elevator_down",
        "name": "Elevator",
        "keybind": pygame.K_3,
        "image_id": "elevator_down",
        "game_size": 1
    },
}
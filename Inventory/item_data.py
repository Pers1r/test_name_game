import pygame
from constants import *

# This is our "database"
ITEM_DATA = {
    "main_crystal": {
        "name": "Main Crystal",
        "type": "buildable",
        "description": "Your colony's core. Protect it.",
        "icon_image_id": "main_crystal", # Uses image from BUILD_IMAGES in assets_loader
        "build_data": {
            "build_image_id": "main_crystal",
            "game_size": 2
        }
    },
    "work_branch": {
        "name": "Workbench",
        "type": "buildable",
        "description": "Craft basic items and tools.",
        "icon_image_id": "work_branch",
        "build_data": {
            "build_image_id": "work_branch",
            "game_size": 1
        }
    },
    "elevator_down": {
        "name": "Elevator",
        "type": "buildable",
        "description": "Travels to the caves beneath.",
        "icon_image_id": "elevator_down",
        "build_data": {
            "build_image_id": "elevator_down",
            "game_size": 1
        }
    },
    # Example of a resource item for the future
    # "coal": {
    #     "name": "Coal",
    #     "type": "resource",
    #     "description": "A combustible black rock.",
    #     "icon_image_id": "coal_icon", # Would need to load this
    #     "build_data": None
    # }
}
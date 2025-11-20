import pygame
from constants import *

# This is our "database"
ITEM_DATA = {
    "default_tool": {
        "name": "Default Tool",
        "type": "tool",
        "description": "A basic multi-purpose tool.",
        "icon_image_id": "default_tool_icon", # Uses image from BUILD_IMAGES
        "build_data": None,
        "tool_data": {
            "shoot_delay": PLATER_SHOOT_DELAY, # Use existing constant
            "enemy_damage": 5, # Was 'damage'
            "block_damage": 1  # New stat for mining
        }
    },
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
    # --- NEW ITEMS ---
    "resource_wood": {
        "name": "Wood Log",
        "type": "resource",
        "description": "Useful for construction.",
        "icon_image_id": "resource_wood",
        "build_data": None,
        "tool_data": None
    },
    "resource_stick": {
        "name": "Stick",
        "type": "resource",
        "description": "A small stick.",
        "icon_image_id": "resource_stick",
        "build_data": None,
        "tool_data": None
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
    "resource_stone": {
        "name": "Stone",
        "type": "resource",
        "description": "A hard, solid material.",
        "icon_image_id": "cave_stone_icon", # We'll add this icon
        "build_data": None,
        "tool_data": None
    },
    "resource_coal": {
        "name": "Coal",
        "type": "resource",
        "description": "A combustible black rock.",
        "icon_image_id": "cave_coal_icon", # We'll add this icon
        "build_data": None,
        "tool_data": None
    },
    "resource_iron": {
        "name": "Iron Ore",
        "type": "resource",
        "description": "A raw, unrefined metal.",
        "icon_image_id": "cave_iron_icon", # We'll add this icon
        "build_data": None,
        "tool_data": None
    },
    "resource_brown_iron": {
        "name": "Iron Ore (Brown)",
        "type": "resource",
        "description": "A raw, unrefined metal.",
        "icon_image_id": "cave_brown_iron_icon",
        "build_data": None,
        "tool_data": None
    },
    "resource_silver": {
        "name": "Silver Ore",
        "type": "resource",
        "description": "A lustrous, precious metal.",
        "icon_image_id": "cave_silver_icon",
        "build_data": None,
        "tool_data": None
    },
    "resource_gold": {
        "name": "Gold Ore",
        "type": "resource",
        "description": "A soft, precious yellow metal.",
        "icon_image_id": "cave_gold_icon",
        "build_data": None,
        "tool_data": None
    },
    "resource_ruby": {
        "name": "Ruby",
        "type": "resource",
        "description": "A precious red gemstone.",
        "icon_image_id": "cave_ruby_icon",
        "build_data": None,
        "tool_data": None
    },
    "resource_diamond": {
        "name": "Diamond",
        "type": "resource",
        "description": "The hardest known substance.",
        "icon_image_id": "cave_diamond_icon",
        "build_data": None,
        "tool_data": None
    },
}
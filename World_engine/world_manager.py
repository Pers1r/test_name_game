import pygame
from World_engine.world import World
from constants import *


class WorldManager:
    def __init__(self, seed, tile_dictionary, rocks_images):
        """
        Manages all game worlds, the current active world,
        and transitions between them.
        """
        self.worlds = {
            "overworld" : World(seed, tile_dictionary, rocks_images, world_type="overworld"),
            "cave" : World(seed, tile_dictionary, rocks_images, world_type="cave")
        }
        self.current_world_id = "overworld"

        self.elevator_links = {}

    def get_current_world(self):
        """Returns the currently active World object."""
        return self.worlds[self.current_world_id]

    def get_world(self, world_id):
        """Returns a specific World object by its ID."""
        return self.worlds.get(world_id)

    def create_elevator_link(self, overworld_grid_pos, cave_grid_pos):
        """
        Creates a two-way link between an overworld position and a cave position.

        Args:
            overworld_grid_pos (tuple): (x, y) grid coordinate in the overworld.
            cave_grid_pos (tuple): (x, y) grid coordinate in the cave.
        """
        ow_key = f"overworld,{overworld_grid_pos[0]},{overworld_grid_pos[1]}"
        cave_key = f"cave,{cave_grid_pos[0]},{cave_grid_pos[1]}"
        self.elevator_links[ow_key] = ("cave", cave_grid_pos[0], cave_grid_pos[1])
        self.elevator_links[cave_key] = ("overworld", overworld_grid_pos[0], overworld_grid_pos[1])

        print(f"Created link: {ow_key} <-> {cave_key}")

    def get_elevator_link(self, grid_x, grid_y):
        key = f"{self.current_world_id},{grid_x},{grid_y}"
        return self.elevator_links.get(key)

    def transition_player(self, player, camera, target_world_id, target_grid_x, target_grid_y):
        """
        Moves the player and camera to a new world and position.
        """
        self.current_world_id = target_world_id
        target_world = self.get_current_world()
        camera.world = target_world

        target_world_x = (target_grid_x * TILE_SIZE) + (TILE_SIZE // 2)
        target_world_y = (target_grid_y * TILE_SIZE) + (TILE_SIZE // 2)

        player.pos.x = target_world_x
        player.pos.y = target_world_y
        player.rect.center = (round(player.pos.x), round(player.pos.y))

        camera.update(player)
        print(f"Player transitioned to {target_world_id} at ({target_grid_x}, {target_grid_y})")

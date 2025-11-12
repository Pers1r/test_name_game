import pygame
import noise
from constants import *
from .tile import *
from .chunk import *
from Entities.dropped_item import DroppedItem


class World:
    def __init__(self, seed, tile_dictionary, rocks_images, world_type="overworld"):
        self.chunks = {}
        self.seed = seed
        self.tile_dictionary = tile_dictionary
        self.rocks_images = rocks_images
        self.world_type = world_type

        self.buildings_list = []
        self.dropped_items_list = []
        self.bullets = []
        self.enemy_list = []

        self.item_factory = None

    def update(self, dt, player, inventory_manager):
        """
        Updates all entities within this world.
        """
        for bullet in self.bullets:
            bullet.update(dt, self, self.item_factory)

        for enemy in self.enemy_list:
            enemy.update(dt, player, self, self.enemy_list)

        for item in self.dropped_items_list:
            item.update()

            if not inventory_manager.is_open():
                item.check_pickup(player, inventory_manager.inventory)

        self.bullets = [bullet for bullet in self.bullets if bullet.lifetime > 0]
        self.enemy_list = [e for e in self.enemy_list if e.is_alive]
        self.dropped_items_list = [i for i in self.dropped_items_list if i.is_alive]

        surviving_buildings = []
        for building in self.buildings_list:
            if building.health <= 0:
                # Building is destroyed, drop its item
                item_proto = self.item_factory.get(building.item_id)
                if item_proto:
                    new_drop = DroppedItem(building.world_rect.centerx, building.world_rect.centery, item_proto)
                    self.dropped_items_list.append(new_drop)

                # Unlink the building from the tiles it occupied
                size = building.game_size
                grid_x = building.world_rect.x // TILE_SIZE
                grid_y = building.world_rect.y // TILE_SIZE
                for y in range(grid_y, grid_y + size):
                    for x in range(grid_x, grid_x + size):
                        tile = self.get_tile_at_grid_pos(x, y)
                        if tile and tile.building == building:
                            tile.building = None # Unlink
            else:
                surviving_buildings.append(building)

        self.buildings_list = surviving_buildings

    def draw(self, surface, camera):
        """
        Draws all chunks and entities in this world.
        """
        # --- 1. Draw Chunks ---
        cam_chunk_x = camera.rect.center[0] // (CHUNK_SIZE * TILE_SIZE)
        cam_chunk_y = camera.rect.center[1] // (CHUNK_SIZE * TILE_SIZE)
        for y in range(cam_chunk_y - 3, cam_chunk_y + 3):
            for x in range(cam_chunk_x - 3, cam_chunk_x + 3):
                chunk_to_draw = self.get_or_generate_chunk(x, y)
                chunk_to_draw.draw(surface, camera)

        # --- 2. Draw Entities ---
        for building in self.buildings_list:
            building.draw(surface, camera)

        for bullet in self.bullets:
            bullet.draw(surface, camera)

        for enemy in self.enemy_list:
            enemy.draw(surface, camera)

        for item in self.dropped_items_list:
            item.draw(surface, camera)

    def get_base_type_at(self, global_x, global_y):
        if self.world_type == "overworld":
            noise_value = noise.pnoise2(global_x*0.1, global_y*0.1, base=self.seed)

            if noise_value < -0.3:
                return "water"
            elif noise_value < 0.4:
                return "grass"
            else:
                return "rock"

        elif self.world_type == "cave":
            noise_value = noise.pnoise2(global_x * 0.05, global_y * 0.05, base=self.seed)

            if noise_value > -0.1: # More common
                return "cave_stone" # Wall
            else:
                return "cave_ground" # Floor

    def get_ore_type_at(self, global_x, global_y):
        """
        Uses stacked Perlin noise maps to determine if an ore should
        spawn at this location. Returns None if no ore.
        """
        # Check rarest first
        # Diamond (rarest)
        diamond_noise = noise.pnoise2(global_x * 0.3, global_y * 0.3, base=self.seed + 4)
        if diamond_noise > 0.75: # High threshold = very rare
            return "cave_diamond"

        # Ruby
        ruby_noise = noise.pnoise2(global_x * 0.28, global_y * 0.28, base=self.seed + 6)
        if ruby_noise > 0.7:
            return "cave_ruby"

        # Gold
        gold_noise = noise.pnoise2(global_x * 0.25, global_y * 0.25, base=self.seed + 3)
        if gold_noise > 0.65:
            return "cave_gold"

        # Silver
        silver_noise = noise.pnoise2(global_x * 0.2, global_y * 0.2, base=self.seed + 5)
        if silver_noise > 0.6:
            return "cave_silver"

        # Iron (common)
        iron_noise = noise.pnoise2(global_x * 0.15, global_y * 0.15, base=self.seed + 1)
        if iron_noise > 0.55:
            # Add some variety to iron spawns
            if iron_noise > 0.6:
                 return "cave_brown_iron"
            return "cave_iron"

        # Coal (most common)
        coal_noise = noise.pnoise2(global_x * 0.12, global_y * 0.12, base=self.seed + 2) # Larger, broader patches
        if coal_noise > 0.5:
            return "cave_coal"

        # No ore found
        return None

    def get_or_generate_chunk(self, chunk_x, chunk_y):
        if (chunk_x, chunk_y) in self.chunks:
            return self.chunks[(chunk_x, chunk_y)]

        new_chunk = Chunk(chunk_x, chunk_y, self.tile_dictionary, self.rocks_images)
        new_chunk.generate_terrain(self)
        self.chunks[(chunk_x, chunk_y)] = new_chunk
        return new_chunk

    def get_tile_at_grid_pos(self, grid_x, grid_y):
        try:
            chunk_x = grid_x // CHUNK_SIZE
            chunk_y = grid_y // CHUNK_SIZE

            local_x = grid_x % CHUNK_SIZE
            local_y = grid_y % CHUNK_SIZE

            chunk = self.get_or_generate_chunk(chunk_x, chunk_y)
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

    def set_tile(self, grid_x, grid_y, new_tile_name):
        try:
            chunk_x = grid_x // CHUNK_SIZE
            chunk_y = grid_y // CHUNK_SIZE
            local_x = grid_x % CHUNK_SIZE
            local_y = grid_y % CHUNK_SIZE

            chunk = self.get_or_generate_chunk(chunk_x, chunk_y)
            if chunk:
                chunk.update_tile_at(local_x, local_y, new_tile_name)
            else:
                print(f"Error: Tried to set tile in non-existent chunk ({chunk_x}, {chunk_y})")
        except Exception as e:
            print(f"Error setting tile: {e}")

    def damage_tile(self, grid_x, grid_y, damage):
        """
        Applies damage to a tile. If the tile is destroyed,
        it sets it to cave_ground and returns the item ID to drop.
        """
        tile = self.get_tile_at_grid_pos(grid_x, grid_y)

        if tile and tile.health != float('inf'):
            tile.health -= damage
            # print(f"Tile at ({grid_x}, {grid_y}) health: {tile.health}") # Debug

            if tile.health <= 0:
                drop_id = tile.drop_item_id
                replacement_tile = "cave_ground"

                if self.world_type == "overworld":
                    if "rock" in tile.tile_type:
                        replacement_tile = "cave_ground"
                    else:
                        replacement_tile = "grass_default_1"

                # Replace destroyed block with cave ground
                self.set_tile(grid_x, grid_y, replacement_tile)

                return drop_id # Return what to drop

        return None # Nothing was destroyed




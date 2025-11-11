import pygame
from numpy.core.shape_base import block

from constants import *
from Building.building import Building
from .inventory import Inventory
from .item import Item, BuildableItem, ToolItem
from .item_data import ITEM_DATA


class InventoryManager:
    def __init__(self, world_manager, build_image_surfaces):
        self.world_manager = world_manager
        self.build_image_surfaces = build_image_surfaces
        self.item_factory = {}

        self.inventory = Inventory(hotbar_size=8, full_size=32)

        self._load_item_prototypes(build_image_surfaces)

    def _load_item_prototypes(self, build_image_surfaces):
        """
        Loads all item data from ITEM_DATA and creates
        Item or BuildableItem objects.
        """
        print("Loading item prototypes...")
        for item_id, data in ITEM_DATA.items():
            icon_image = build_image_surfaces.get(data['icon_image_id'])
            if not icon_image:
                print(f"Warning: Missing icon '{data['icon_image_id']}' for item '{item_id}'.")
                icon_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                icon_image.fill((255, 0, 255)) # Error pink

            if data["type"] == "buildable":
                b_data = data["build_data"]
                self.item_factory[item_id] = BuildableItem(
                    item_id=item_id,
                    name=data["name"],
                    item_type=data["type"],
                    image=icon_image,
                    description=data["description"],
                    build_image_id=b_data["build_image_id"],
                    game_size=b_data["game_size"],
                )

            elif data["type"] == "tool":
                t_data = data["tool_data"]
                self.item_factory[item_id] = ToolItem(
                    item_id=item_id,
                    name=data["name"],
                    image=icon_image,
                    description=data["description"],
                    shoot_delay=t_data["shoot_delay"],
                    enemy_damage=t_data["enemy_damage"],
                    block_damage=t_data["block_damage"]
                )

            else:
                self.item_factory[item_id] = Item(
                    item_id=item_id,
                    name=data["name"],
                    item_type=data["type"],
                    image=icon_image,
                    description=data["description"]
                )
        print("Item loading complete.")

    def spawn_starting_items(self):
        """Adds the default items to the player's inventory."""
        crystal = self.item_factory.get("main_crystal")
        bench = self.item_factory.get("work_branch")
        tool = self.item_factory.get("default_tool")

        if tool: self.inventory.add_item(tool, 1)
        if crystal: self.inventory.add_item(crystal, 1)
        if bench: self.inventory.add_item(bench, 1)

    def is_open(self):
        """Checks if the full inventory UI is open."""
        return self.inventory.is_open

    def toggle_inventory(self):
        """Opens or closes the full inventory UI."""
        self.inventory.is_open = not self.inventory.is_open
        print(f"Inventory open: {self.inventory.is_open}")

    def get_selected_buildable(self):
        """
        Checks if the currently selected hotbar item is a BuildableItem.
        """
        if self.is_open():
            return None

        slot = self.inventory.get_selected_item_slot()
        if slot.item and isinstance(slot.item, BuildableItem):
            return slot.item
        return None

    def get_selected_tool_item(self):
        """
        Checks if the currently selected hotbar item is a ToolItem.
        """
        if self.is_open():
            return None # Can't use tools while inventory is open

        slot = self.inventory.get_selected_item_slot()
        if slot.item and isinstance(slot.item, ToolItem):
            return slot.item
        return None

    def handle_input(self, event, world, world_mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.toggle_inventory()

            if not self.is_open():
                self.inventory.handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_open():
                # TODO: Handle inventory click-and-drag logic
                pass
            else:
                buildable_item = self.get_selected_buildable()
                if buildable_item:
                    self.try_place_building(world, world_mouse_pos, buildable_item)

    def try_place_building(self, world, world_mouse_pos, item):
        """
        Contains all the logic for checking and placing a buildable item.
        This is moved from the old BuildingManager.
        """
        size = item.game_size
        grid_x = int(world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(world_mouse_pos[1] // TILE_SIZE)

        can_build = True
        for y in range(grid_y, grid_y + size):
            for x in range(grid_x, grid_x + size):
                tile = world.get_tile_at_grid_pos(x, y)
                if not tile or not tile._is_buildable:
                    can_build = False
                    break
                if not can_build:
                    break

        if can_build:
            temp_rect = pygame.Rect(grid_x * TILE_SIZE, grid_y * TILE_SIZE, size * TILE_SIZE, size * TILE_SIZE)
            for b in world.buildings_list:
                if temp_rect.colliderect(b.world_rect):
                    can_build = False
                    break

        if can_build and item.item_id == "elevator_down":
            if self.world_manager.get_elevator_link(grid_x, grid_y):
                print("Cannot build: An elevator link already exists here.")
                can_build = False
        if can_build:

            if item.item_id == "elevator_down":
                # --- This is your correct elevator logic from the last fix ---
                overworld_world = self.world_manager.get_world("overworld")
                cave_world = self.world_manager.get_world("cave")

                if not overworld_world or not cave_world:
                    print("ERROR: Missing overworld or cave world!")
                    return

                if world.world_type == "overworld":
                    image = self.build_image_surfaces["elevator_down"]
                    new_building = Building(grid_x, grid_y, "elevator_down", image)
                    world.buildings_list.append(new_building)
                    world.set_tile(grid_x, grid_y, "elevator_up")

                    for y in range(grid_y - 1, grid_y + 2):
                        for x in range(grid_x - 1, grid_x + 2):
                            cave_world.set_tile(x, y, "cave_ground")
                    cave_world.set_tile(grid_x, grid_y, "elevator_up")

                elif world.world_type == "cave":
                    world.set_tile(grid_x, grid_y, "elevator_up")
                    image = self.build_image_surfaces["elevator_down"]
                    new_building = Building(grid_x, grid_y, "elevator_down", image)
                    overworld_world.buildings_list.append(new_building)
                    overworld_world.set_tile(grid_x, grid_y, "elevator_up")

                self.world_manager.create_elevator_link((grid_x, grid_y), (grid_x, grid_y))
                print(f"Placed elevator link at ({grid_x}, {grid_y})")

            else:
                # --- DEFAULT LOGIC FOR ALL OTHER BUILDINGS ---
                for y in range(grid_y, grid_y + size):
                    for x in range(grid_x, grid_x + size):
                        world.set_tile(x, y, "rock_default")

                image = self.build_image_surfaces[item.build_image_id]
                new_building = Building(grid_x, grid_y, item.item_id, image)
                world.buildings_list.append(new_building)
                print(f"Placed {item.name} at ({grid_x}, {grid_y})")


            self.inventory.remove_item(self.inventory.selected_slot_index, 1)

        elif not can_build:
            print("Cannot build here. Space is not free or link exists.")

    def draw_hotbar(self, screen):
        """Draws the hotbar UI."""
        self.inventory.draw_hotbar(screen)

    def draw_inventory(self, screen):
        """Draws the full inventory UI."""
        self.inventory.draw_inventory(screen)

    def draw_ghost(self, surface, camera, world_mouse_pos):
        """Draws the building preview ghost."""
        buildable_item = self.get_selected_buildable()
        if not buildable_item:
            return

        ghost_surface = buildable_item.get_ghost_surface(self.build_image_surfaces)
        size = buildable_item.game_size

        grid_x = int(world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(world_mouse_pos[1] // TILE_SIZE)
        ghost_world_pos = (grid_x * TILE_SIZE, grid_y * TILE_SIZE)

        can_build = True
        world = camera.world # Get world from camera

        # --- 1. Check tiles ---
        for y in range(grid_y, grid_y + size):
            for x in range(grid_x, grid_x + size):
                tile = world.get_tile_at_grid_pos(x, y)
                if not tile or not tile._is_buildable:
                    can_build = False
                    break
            if not can_build:
                break

        # --- 2. Check buildings ---
        ghost_rect = ghost_surface.get_rect(topleft=ghost_world_pos)
        if can_build:
            for b in world.buildings_list:
                if ghost_rect.colliderect(b.world_rect):
                    can_build = False
                    break

        # --- 3. Check elevator links ---
        if can_build and buildable_item.item_id == "elevator_down":
             if self.world_manager.get_elevator_link(grid_x, grid_y):
                can_build = False

        # --- Draw the ghost with a red/white tint ---
        tint = (255, 255, 255, 150) if can_build else (255, 50, 50, 150)
        screen_rect = camera.set_target(ghost_rect)

        temp_surf = ghost_surface.copy()
        temp_surf.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(temp_surf, screen_rect)

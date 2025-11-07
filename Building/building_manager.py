import pygame
from constants import *

class BuildingManager:
    def __init__(self, build_data, tile_dictionary):
        self.build_data = build_data
        self.tile_dictionary = tile_dictionary

        self.building_mode = False
        self.selected_building_id = None
        self.ghost_surface = None

        self.menu_height = 80
        self.button_size = 60
        self.button_padding = 10
        self.menu_rect = pygame.Rect(0, SCREEN_HEIGHT - self.menu_height, SCREEN_WIDTH, self.menu_height)

        self.ui_buttons = {}
        self._create_ui_buttons()

    def _create_ui_buttons(self):
        x_pos = self.button_padding

        wall_data = self.build_data["wall"]
        wall_rect = pygame.Rect(
            x_pos,
            SCREEN_HEIGHT - self.menu_height + self.button_padding,
            self.button_size,
            self.button_size
        )
        self.ui_buttons[wall_data["id"]] = wall_rect

        x_pos += self.button_size + self.button_padding
        turret_data = self.build_data["turret"]
        turret_rect = pygame.Rect(
            x_pos,
            SCREEN_HEIGHT - self.menu_height + self.button_padding,
            self.button_size, self.button_size
        )
        self.ui_buttons[turret_data["id"]] = turret_rect

    def toggle_mode(self):
        self.building_mode = not self.building_mode
        if not self.building_mode:
            self.select_building(None)
        print(f"Building mode: {self.building_mode}")

    def select_building(self, building_id):
        self.selected_building_id = building_id
        if building_id:
            self._create_ghost_surface()
        else:
            self.ghost_surface = None

    def _create_ghost_surface(self):
        if not self.selected_building_id:
            return

        data = self.build_data[self.selected_building_id]
        tile_name = data["tile_name"]

        image = self.tile_dictionary.get(tile_name)
        if not image:
            image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            image.fill(data["placeholder_color"])

        self.ghost_surface = image.copy()
        self.ghost_surface.set_alpha(150)

    def handle_input(self, event, world, world_mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                self.toggle_mode()
            if self.building_mode:
                for data in self.build_data.values():
                    if event.key == data["keybind"]:
                        self.selected_building_id = data["id"]

        if event.type == pygame.MOUSEBUTTONDOWN and self.building_mode:
            mx, my  = event.pos

            if self.menu_rect.collidepoint(mx, my):
                for building_id, rect in self.ui_buttons.items():
                    if rect.collidepoint(mx, my):
                        self.select_building(building_id)
                        return

            elif self.selected_building_id and event.button == 1:
                self.try_place_building(world, world_mouse_pos)

    def try_place_building(self, world, world_mouse_pos):
        grid_x = int(world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(world_mouse_pos[1] // TILE_SIZE)

        tile = world.get_tile(grid_x, grid_y)

        if tile and tile.is_buildable:
            data = self.build_data[self.selected_building_id]
            world.set_tile(grid_x, grid_y, data["tile_name"])
            print(f"Placed {self.selected_building_id} at ({grid_x}, {grid_y})")
        else:
            print("Cannot build here. Space is not free.")

    def draw_ui(self, screen):
        if not self.building_mode:
            return

        pygame.draw.rect(screen, (20, 20, 20, 200), self.menu_rect)

        for building_id, rect in self.ui_buttons.items():
            data = self.build_data[building_id]
            color = data["placeholder_color"]

            if building_id == self.selected_building_id:
                pygame.draw.rect(screen, "yellow", rect.inflate(4, 4), 2)

            pygame.draw.rect(screen, color, rect)

            font = pygame.font.Font(None, 24)
            key_char = pygame.key.name(data["keybind"])
            text = font.render(key_char, True, WHITE)
            screen.blit(text, text.get_rect(topright=rect.topright))

    def draw_ghost(self, surface, camera, world_mouse_pos):
        if not self.building_mode or not self.ghost_surface:
            return

        grid_x = int(world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(world_mouse_pos[1] // TILE_SIZE)

        ghost_world_pos = (grid_x*TILE_SIZE, grid_y*TILE_SIZE)

        tile = camera.world.get_tile_at_grid_pos(grid_x, grid_y)
        can_build = tile and tile.is_buildable

        tint = (255, 255, 255, 150) if can_build else (255, 50, 50, 150)

        ghost_rect = self.ghost_surface.get_rect(topleft=ghost_world_pos)

        screen_rect = camera.set_target(ghost_rect)

        tmp_surf = self.ghost_surface.copy()
        tmp_surf.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(tmp_surf, screen_rect)


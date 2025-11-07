import pygame
from constants import *
from Building.building import Building

class BuildingManager:
    def __init__(self, build_data, tile_dictionary, bild_image_surfaces):
        self.build_data = build_data
        self.tile_dictionary = tile_dictionary
        self.bild_image_surfaces = bild_image_surfaces

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

        for building_id, data in self.build_data.items():
            button_rect = pygame.Rect(
                x_pos,
                SCREEN_HEIGHT - self.menu_height + self.button_size,
                self.button_size,
                self.button_size
            )
            self.ui_buttons[building_id] = button_rect
            x_pos += self.button_size + self.button_padding

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
        image_id = data["image_id"]

        image = self.tile_dictionary.get(image_id)
        if not image:
            size = data["game_size"] * TILE_SIZE
            image = pygame.Surface((size, size))
            image.fill((100, 0, 100)) # Bright purple error color

        self.ghost_surface = image.copy()
        self.ghost_surface.set_alpha(150)

    def handle_input(self, event, world, world_mouse_pos, buildings_list):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                self.toggle_mode()
            if self.building_mode:
                for data in self.build_data.values():
                    if event.key == data["keybind"]:
                        self.select_building(data["id"])

        if event.type == pygame.MOUSEBUTTONDOWN and self.building_mode:
            mx, my  = event.pos

            if self.menu_rect.collidepoint(mx, my):
                for building_id, rect in self.ui_buttons.items():
                    if rect.collidepoint(mx, my):
                        self.select_building(building_id)
                        return

            elif self.selected_building_id and event.button == 1:
                self.try_place_building(world, world_mouse_pos, buildings_list)

    def try_place_building(self, world, world_mouse_pos, buildings_list):
        data = self.build_data[self.selected_building_id]
        size = data["game_size"]

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
            for y in range(grid_y, grid_y + size):
                for x in range(grid_x, grid_x + size):
                    world.set_tile(x, y, "rock_default")

            image_id = data["image_id"]
            image = self.bild_image_surfaces[image_id]

            new_building = Building(grid_x, grid_y, image_id, image)
            buildings_list.append(new_building)

            print(f"Placed {self.selected_building_id} at ({grid_x}, {grid_y})")
        else:
            print("Cannot build here. Space is not free.")

    def draw_ui(self, screen):
        if not self.building_mode:
            return

        menu_bg_surface = pygame.Surface(self.menu_rect.size, pygame.SRCALPHA)
        menu_bg_surface.fill((20, 20, 20, 200))
        screen.blit(menu_bg_surface, self.menu_rect.topleft)

        for building_id, rect in self.ui_buttons.items():
            data = self.build_data[building_id]

            # Draw border if selected
            if building_id == self.selected_building_id:
                pygame.draw.rect(screen, "yellow", rect.inflate(4, 4), 2)

            image_id = data["image_id"]
            if image_id:
                image = self.bild_image_surfaces.get(image_id)
                if image:
                    scaled_image = pygame.transform.scale(image, rect.size)
                    screen.blit(scaled_image, rect.topleft)
                else:
                    pygame.draw.rect(screen, (100, 0, 100), rect) # Error color
            else:
                pygame.draw.rect(screen, (50, 50, 50), rect)

            # Draw keybind number
            font = pygame.font.Font(None, 24)
            key_char = pygame.key.name(data["keybind"])
            text = font.render(key_char, True, WHITE)
            screen.blit(text, text.get_rect(topright=rect.topright))

    def draw_ghost(self, surface, camera, world_mouse_pos, buildings_list):
        if not self.building_mode or not self.ghost_surface:
            return

        data = self.build_data[self.selected_building_id]
        size = data["game_size"]

        grid_x = int(world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(world_mouse_pos[1] // TILE_SIZE)

        ghost_world_pos = (grid_x*TILE_SIZE, grid_y*TILE_SIZE)

        can_build = True

        for y in range(grid_y, grid_y + size):
            for x in range(grid_x, grid_x + size):
                tile = camera.world.get_tile_at_grid_pos(x, y)
                if not tile or not tile._is_buildable:
                    can_build = False
                    break
                if not can_build:
                    break

        if can_build:
            ghost_rect = self.ghost_surface.get_rect(topleft=ghost_world_pos)
            for b in buildings_list:
                if ghost_rect.colliderect(b.world_rect):
                    can_build = False
                    break

        tint = (255, 255, 255, 150) if can_build else (255, 50, 50, 150)
        ghost_rect = self.ghost_surface.get_rect(topleft=ghost_world_pos)
        screen_rect = camera.set_target(ghost_rect)

        tmp_surf = self.ghost_surface.copy()
        tmp_surf.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(tmp_surf, screen_rect)


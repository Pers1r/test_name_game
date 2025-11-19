import pygame
import random
import math
import sys
import os

# --- Core Game Modules ---
from game_states import GameState
from camera import Camera
from player import Player
from wave_manager import WaveManager

# --- World Engine ---
from World_engine.world import World
from World_engine.world_manager import WorldManager

# --- UI & Managers ---
from Inventory.inventory_manager import InventoryManager
from Crafting.crafting_manager import CraftingManager
from ui.pause_menu import draw_pause_menu, handle_pause_click
from ui.game_over_screen import draw_game_over_screen, handle_game_over_click

# --- Loaders & Constants ---
from constants import *
from assets_loader import *

# --- Entities ---
from bullet import Bullet
from enemy import Enemy
from Building.building import Building
from Entities.dropped_item import DroppedItem


class Game:
    def __init__(self, debug=False, performance=False, asset_path="."):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug = debug
        self.asset_path = asset_path

        # --- Display Setup ---
        if performance:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        else:
            flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED | pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        print(f"Fixed window created with size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

        self.zoom_level = ZOOM_LEVEL
        self.world_surface_width = int(SCREEN_WIDTH / self.zoom_level)
        self.world_surface_height = int(SCREEN_HEIGHT / self.zoom_level)
        self.world_surface = pygame.Surface((self.world_surface_width, self.world_surface_height))
        print(f"World surface created with size: {self.world_surface_width}x{self.world_surface_height}")

        # --- Game State ---
        self.game_state = GameState.PLAYING
        self.previous_state = GameState.PLAYING
        self.pause_menu_rects = {}

        # --- Load Assets ---
        self.font = pygame.font.Font(None, 30)
        self.font_large = pygame.font.Font(None, 72)

        try:
            # Note: We now use self.resource_path()
            tileset_image = pygame.image.load(self.resource_path("assets/TileSet_V2.png")).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load tileset image: {e}")
            pygame.quit()
            sys.exit()

        self.tile_dictionary = load_tiles_from_atlas(tileset_image, TILE_ATLAS)
        self.build_image_surfaces = load_build_images(BUILD_IMAGES)
        self.rocks_image_surfaces = load_rocks_images(ROCKS_IMAGES)

        # --- Initialize Core Systems ---
        if self.debug:
            seed = 300
        else:
            seed = random.randint(100, 1000)

        self.player = Player(0, 0, debug=self.debug)
        self.camera = Camera(self.world_surface_width, self.world_surface_height)
        self.world_manager = WorldManager(seed=seed, tile_dictionary=self.tile_dictionary, rocks_images=self.rocks_image_surfaces)
        self.camera.world = self.world_manager.get_current_world()

        # --- Main Game Loop Tracking ---
        self.main_crystal = None

        # --- Initialize Managers ---
        self.inventory_manager = InventoryManager(self.world_manager, self.build_image_surfaces)
        self.crafting_manager = CraftingManager(self.inventory_manager)
        self.wave_manager = WaveManager()

        # --- Link Item Factory to Worlds ---
        # This is a crucial step for drops
        item_factory = self.inventory_manager.item_factory
        self.world_manager.get_world("overworld").item_factory = item_factory
        self.world_manager.get_world("cave").item_factory = item_factory

        # --- Final Setup ---
        self.inventory_manager.spawn_starting_items()
        self.load_start_chunks()

        # --- Mouse Position Variables ---
        self.screen_mouse_pos = (0, 0)
        self.surface_mouse_pos = (0, 0)
        self.world_mouse_pos = (0, 0)
        self.current_time = 0
        self.current_world = self.world_manager.get_current_world()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_start_chunks(self):
        for x in range(-START_CHUNKS_NUM, START_CHUNKS_NUM + 1):
            for y in range(-START_CHUNKS_NUM, START_CHUNKS_NUM + 1):
                self.world_manager.get_current_world().get_or_generate_chunk(x, y)

    def set_state(self, new_state):
        # Prevent state changes after game over
        if self.game_state == GameState.GAME_OVER:
            return

        if self.game_state != GameState.PAUSED:
            self.previous_state = self.game_state

        self.game_state = new_state

        # --- Update manager states ---
        # This synchronizes all managers with the central game state
        self.inventory_manager.inventory.is_open = (new_state == GameState.INVENTORY)
        self.crafting_manager.is_open = (new_state == GameState.CRAFTING)
        print(f"Game state changed to: {self.game_state}")

    def toggle_pause(self):
        if self.game_state == GameState.PAUSED:
            self.set_state(self.previous_state)
        else:
            self.set_state(GameState.PAUSED)

    def run(self):
        while self.running:
            # --- Core Loop ---
            dt = self.clock.tick(FPS) / 1000.0
            self.current_time = pygame.time.get_ticks()

            if self.game_state != GameState.GAME_OVER:
                self.current_world = self.world_manager.get_current_world()

            # --- Mouse Position ---
            mx, my = pygame.mouse.get_pos()
            self.screen_mouse_pos = (mx, my)
            self.surface_mouse_x = self.screen_mouse_pos[0] / self.zoom_level
            self.surface_mouse_y = self.screen_mouse_pos[1] / self.zoom_level
            self.surface_mouse_pos = (self.surface_mouse_x, self.surface_mouse_y)
            self.world_mouse_x = self.camera.rect.x + self.surface_mouse_x
            self.world_mouse_y = self.camera.rect.y + self.surface_mouse_y
            self.world_mouse_pos = (self.world_mouse_x, self.world_mouse_y)

            # --- Process Inputs ---
            self.handle_events()

            # --- Update Game Logic ---
            self.update(dt)

            # --- Render Graphics ---
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GameState.INVENTORY or self.game_state == GameState.CRAFTING:
                        self.set_state(GameState.PLAYING)
                    elif self.game_state == GameState.PLAYING:
                        self.toggle_pause()
                    elif self.game_state == GameState.PAUSED:
                        self.toggle_pause()

            # --- State-Based Event Handling ---
            if self.game_state == GameState.PLAYING:
                self._handle_playing_events(event)
            elif self.game_state == GameState.PAUSED:
                self._handle_paused_events(event)
            elif self.game_state == GameState.INVENTORY:
                self._handle_inventory_events(event)
            elif self.game_state == GameState.CRAFTING:
                self._handle_crafting_events(event)
            elif self.game_state == GameState.GAME_OVER:
                self._handle_game_over_events(event)

    def _handle_playing_events(self, event):
        self.inventory_manager.handle_hotbar_keys(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.set_state(GameState.INVENTORY)
            if event.key == pygame.K_n: # Start wave
                self.wave_manager.start_next_wave()
            if event.key == pygame.K_f: # Interact
                self.handle_interaction()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Pass to inventory manager for placing buildings
            self.inventory_manager.handle_place_building_click(event, self.current_world, self.world_mouse_pos, self)

        if event.type == pygame.MOUSEWHEEL:
            self.handle_zoom(event)

    def _handle_paused_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = handle_pause_click(event.pos, self.pause_menu_rects)
            if action == "resume":
                self.toggle_pause()
            elif action == "options":
                print("Options clicked!") # TODO
            elif action == "quit":
                self.running = False

    def _handle_inventory_events(self, event):
        # InventoryManager handles clicks within the full inventory
        self.inventory_manager.handle_inventory_input(event)

    def _handle_crafting_events(self, event):
        self.crafting_manager.handle_input(event)
        # If crafting manager closes itself, return to playing
        if not self.crafting_manager.is_open:
            self.set_state(GameState.PLAYING)

    def _handle_game_over_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = handle_game_over_click(event.pos, self.game_over_rects)
            if action == "quit":
                self.running = False

    def update(self, dt):
        if self.game_state == GameState.PLAYING:
            self.player.update(dt, self.current_world, self.camera)
            self.camera.update(self.player)
            self.handle_shooting()

        if self.game_state == GameState.PLAYING or self.game_state == GameState.INVENTORY or self.game_state == GameState.CRAFTING:
            # Pass the main_crystal to the world update loop
            self.current_world.update(dt, self.player, self.inventory_manager, self.main_crystal)

            if self.world_manager.current_world_id == "overworld":
                self.wave_manager.update(
                    self.current_time,
                    self.player,
                    self.current_world
                )

            # --- Check for Lose Conditions ---
            self._check_lose_conditions()

    def _check_lose_conditions(self):
        # 1. Player dies before placing crystal
        if not self.player.is_alive and self.main_crystal is None:
            print("Game Over: Player died before placing the crystal.")
            self.set_state(GameState.GAME_OVER)

        # 2. Player dies, but crystal is placed -> Respawn
        elif not self.player.is_alive and self.main_crystal is not None:
            self._respawn_player()

        # 3. Crystal is destroyed
        if self.main_crystal and not self.main_crystal.is_alive:
            print("Game Over: The Main Crystal was destroyed.")
            self.set_state(GameState.GAME_OVER)

    def _respawn_player(self):
        # Find a safe spot near the crystal
        respawn_pos = self.main_crystal.world_rect.center
        # TODO: Add logic to find a valid *walkable* tile near the crystal
        # For now, just respawn on its center.
        self.player.respawn(respawn_pos)
        self.camera.update(self.player) # Snap camera to respawn

    def draw(self):
        self.world_surface.fill("black")

        # --- Draw World ---
        self.current_world.draw(self.world_surface, self.camera)

        # --- Draw Player & Ghost ---
        if self.game_state != GameState.GAME_OVER:
            self.player.draw(self.world_surface, self.camera, self.surface_mouse_pos)
            self.inventory_manager.draw_ghost(self.world_surface, self.camera, self.world_mouse_pos)

        # --- Scale World to Screen ---
        pygame.transform.scale(self.world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), self.screen)

        self.inventory_manager.draw_hotbar(self.screen)

        if self.game_state == GameState.INVENTORY:
            self.inventory_manager.draw_inventory(self.screen)
        elif self.game_state == GameState.CRAFTING:
            self.crafting_manager.draw(self.screen)
        elif self.game_state == GameState.PAUSED:
            self.pause_menu_rects = draw_pause_menu(self.screen, self.font)
        elif self.game_state == GameState.GAME_OVER:
            # Draw the game over screen
            self.game_over_rects = draw_game_over_screen(self.screen, self.font_large)

        if self.debug:
            self.draw_debug_info()

        pygame.display.flip()

    def handle_interaction(self):
        """ Handles all 'F' key interactions (elevators, workbenches, etc.) """
        grid_x = int(self.world_mouse_pos[0] // TILE_SIZE)
        grid_y = int(self.world_mouse_pos[1] // TILE_SIZE)

        # --- 1. Check for Building Interaction (e.g., Workbench) ---
        for building in self.current_world.buildings_list:
            if building.item_id == "work_branch" and building.world_rect.collidepoint(self.world_mouse_pos):
                interaction_rect = self.player.rect.inflate(TILE_SIZE * 2, TILE_SIZE * 2)
                if interaction_rect.colliderect(building.world_rect):
                    self.crafting_manager.open_workbench(building)
                    self.set_state(GameState.CRAFTING) # Set game state
                    return

        # --- 2. Check for Tile/Elevator Interaction ---
        player_grid_x = int(self.player.pos.x // TILE_SIZE)
        player_grid_y = int(self.player.pos.y // TILE_SIZE)

        # Check if player is standing on a link
        link = self.world_manager.get_elevator_link(player_grid_x, player_grid_y)
        if link:
            target_world_id, target_x, target_y = link
            self.world_manager.transition_player(self.player, self.camera, target_world_id, target_x, target_y)
            return

        print("Nothing to interact with.")

    def handle_shooting(self):
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0]:
            selected_tool = self.inventory_manager.get_selected_tool_item()
            if selected_tool and not self.inventory_manager.get_selected_buildable():
                new_bullet = self.player.shoot(selected_tool)
                if new_bullet:
                    self.current_world.bullets.append(new_bullet)

    def handle_zoom(self, event):
        if event.y < 0: # Scroll Up
            self.zoom_level -= 0.1
        elif event.y > 0: # Scroll Down
            self.zoom_level += 0.1

        self.zoom_level = max(0.8, min(self.zoom_level, 2.3))
        self.world_surface_width = int(SCREEN_WIDTH / self.zoom_level)
        self.world_surface_height = int(SCREEN_HEIGHT / self.zoom_level)
        self.world_surface = pygame.Surface((self.world_surface_width, self.world_surface_height))
        self.camera.width = self.camera.rect.width = self.world_surface_width
        self.camera.height = self.camera.rect.height = self.world_surface_height
        self.player.update_zoom_properties(self.zoom_level)

    def draw_debug_info(self):
        # Collect debug info from managers
        wave_debug = self.wave_manager.get_debug_info()

        # Draw
        texts = [
            f"Player World Pos: ({int(self.player.rect.x)}, {int(self.player.rect.y)})",
            f"Player Health: {self.player.health}", # Added
            f"Camera World Pos: ({int(self.camera.rect.x)}, {int(self.camera.rect.y)})",
            f"FPS: {int(self.clock.get_fps())}",
            f"Bullets: {len(self.current_world.bullets)}",
            f"Enemies: {len(self.current_world.enemy_list)}",
            wave_debug[0], # Wave text
            wave_debug[1], # Spawning text
            f"World: {self.world_manager.current_world_id}",
            f"Game State: {self.game_state.name}"
            f"Crystal Placed: {'YES' if self.main_crystal else 'NO'}" # Added
        ]

        for i, text in enumerate(texts):
            img = self.font.render(text, True, WHITE)
            self.screen.blit(img, (10, 10 + i * 30))





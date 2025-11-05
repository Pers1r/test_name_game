import pygame
import random
import math
import sys
import os

from World_engine.world import World
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, ZOOM_LEVEL, TILE_SIZE, CHUNK_SIZE, WHITE)
from assets_loader import *
from World_engine import *
from camera import Camera
from player import Player
from bullet import Bullet
from enemy import Enemy

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def spawn_enemy(player, world_surface_width, enemy_list):
    spawn_radius = (world_surface_width / 2) + random.randint(50,150)
    angle = random.uniform(0, 2 * math.pi)

    spawn_x = player.pos.x + math.cos(angle) * spawn_radius
    spawn_y = player.pos.y + math.sin(angle) * spawn_radius

    enemy_list.append(Enemy(spawn_x, spawn_y))

def draw_pause_menu(screen, font):
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) # Black with 150 alpha
    screen.blit(overlay, (0, 0))

    # Menu text
    menu_title = font.render("Paused", True, WHITE)
    resume_text = font.render("Resume", True, WHITE)
    options_text = font.render("Options", True, WHITE)
    quit_text = font.render("Quit", True, WHITE)

    # Get mouse position for hover checks
    mx, my = pygame.mouse.get_pos()

    # Button Rects (we create them here to position text)
    # Centered on screen
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    title_rect = menu_title.get_rect(center=(center_x, center_y - 100))
    resume_btn_rect = resume_text.get_rect(center=(center_x, center_y))
    options_btn_rect = options_text.get_rect(center=(center_x, center_y + 50))
    quit_btn_rect = quit_text.get_rect(center=(center_x, center_y + 100))

    # --- Draw hover effect ---
    if resume_btn_rect.collidepoint(mx, my):
        pygame.draw.rect(screen, (50, 50, 50), resume_btn_rect.inflate(20, 10))
    if options_btn_rect.collidepoint(mx, my):
        pygame.draw.rect(screen, (50, 50, 50), options_btn_rect.inflate(20, 10))
    if quit_btn_rect.collidepoint(mx, my):
        pygame.draw.rect(screen, (50, 50, 50), quit_btn_rect.inflate(20, 10))

    # Draw text
    screen.blit(menu_title, title_rect)
    screen.blit(resume_text, resume_btn_rect)
    screen.blit(options_text, options_btn_rect)
    screen.blit(quit_text, quit_btn_rect)

    # Return the rects for click detection
    return {
        "resume": resume_btn_rect,
        "options": options_btn_rect,
        "quit": quit_btn_rect
    }

def main(debug=False, performance=False):
    pygame.init()
    clock = pygame.time.Clock()
    RUNNING = True

    if performance:
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    else:
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SCALED |pygame.FULLSCREEN
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    print(f"Fixed window created with size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    zoom_level = ZOOM_LEVEL

    world_surface_width = int(SCREEN_WIDTH/ zoom_level)
    world_surface_height = int(SCREEN_HEIGHT/ zoom_level)
    world_surface = pygame.Surface((world_surface_width, world_surface_height))
    print(f"World surface created with size: {world_surface_width}x{world_surface_height}")

    try:
        tileset_image = pygame.image.load(resource_path("assets/TileSet_V2.png")).convert_alpha()
    except pygame.error as e:
        print(f"Unable to load tileset image: {e}")
        pygame.quit()
        sys.exit()

    tile_dictionary = load_tiles_from_atlas(tileset_image, TILE_ATLAS)

    player = Player(0, 0, debug=debug)
    camera = Camera(world_surface_width, world_surface_height)

    if debug:
        world = World(seed=300, tile_dictionary=tile_dictionary)
    else:
        world = World(seed=random.randint(100, 1000), tile_dictionary=tile_dictionary)
    for x in range(-START_CHUNKS_NUM, START_CHUNKS_NUM + 1):
        for y in range(-START_CHUNKS_NUM, START_CHUNKS_NUM + 1):
            world.get_or_generate_chunk(x, y)

    font = pygame.font.Font(None, 30)

    bullets = []
    enemy_list = []

    wave_number = 0
    wave_active = False
    enemies_to_spawn_this_wave = 0
    spawn_timer = 0
    spawn_delay = 1000

    game_paused = False
    pause_btn_rects = {}

    def start_next_wave():
        nonlocal wave_number, wave_active, enemies_to_spawn_this_wave, spawn_timer
        if wave_active: # Don't start a wave if one is active
            return

        wave_number += 1
        wave_active = True
        enemies_to_spawn_this_wave = 5 + (wave_number * 3)
        spawn_timer = pygame.time.get_ticks()

    while RUNNING:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks()

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Exit on ESCAPE
                    game_paused = not game_paused

                if not game_paused:
                    if event.key == pygame.K_n: # Press 'N' to start next wave
                        start_next_wave()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_paused:
                    if event.button == 1:
                        if button_rects["resume"].collidepoint(mx, my):
                            game_paused = False
                        if button_rects["options"].collidepoint(mx, my):
                            print("Options clicked!")
                            # TODO: ...
                        if button_rects["quit"].collidepoint(mx, my):
                            RUNNING = False

                if not game_paused:
                    if event.button == 4:
                        zoom_level -= 0.1
                    if event.button == 5:
                        zoom_level += 0.1

                    zoom_level = max(0.8, min(zoom_level, 2.3))

                    # --- RE-CREATE SURFACES ON ZOOM CHANGE ---
                    world_surface_width = int(SCREEN_WIDTH / zoom_level)
                    world_surface_height = int(SCREEN_HEIGHT / zoom_level)
                    world_surface = pygame.Surface((world_surface_width, world_surface_height))

                    # Update camera
                    camera.width = world_surface_width
                    camera.height = world_surface_height
                    camera.rect.width = world_surface_width
                    camera.rect.height = world_surface_height

                    # Update player
                    player.update_zoom_properties(zoom_level)

        if not game_paused:
            mouse_state = pygame.mouse.get_pressed()
            if mouse_state[0]:
                new_bullet = player.shoot()
                if new_bullet:
                    bullets.append(new_bullet)

            if wave_active and enemies_to_spawn_this_wave > 0:
                if current_time - spawn_timer > spawn_delay:
                    spawn_timer = current_time
                    spawn_enemy(player, world_surface_width, enemy_list)
                    enemies_to_spawn_this_wave -= 1

            if wave_active and enemies_to_spawn_this_wave == 0 and not enemy_list:
                wave_active = False
                print(f"--- WAVE {wave_number} COMPLETE! ---")
                print("Press 'N' to start next wave.")

            player.update(dt, world, camera)
            camera.update(player)

            for bullet in bullets:
                bullet.update(dt, world, enemy_list)

            for enemy in enemy_list:
                enemy.update(dt, player, world, enemy_list)

            bullets = [bullet for bullet in bullets if bullet.lifetime > 0]
            enemy_list = [e for e in enemy_list if e.is_alive]

        world_surface.fill("black")

        cam_chunk_x = camera.rect.center[0] // (CHUNK_SIZE * TILE_SIZE)
        cam_chunk_y = camera.rect.center[1] // (CHUNK_SIZE * TILE_SIZE)
        for y in range(cam_chunk_y - 3, cam_chunk_y + 3):
            for x in range(cam_chunk_x - 3, cam_chunk_x + 3):
                chunk_to_draw = world.get_or_generate_chunk(x, y)
                chunk_to_draw.draw(world_surface, camera)

        screen_mouse_pos = pygame.mouse.get_pos()
        # Scale the mouse position down to match the world_surface
        world_mouse_x = screen_mouse_pos[0] / ZOOM_LEVEL
        world_mouse_y = screen_mouse_pos[1] / ZOOM_LEVEL

        player.draw(world_surface, camera, (world_mouse_x, world_mouse_y))

        for bullet in bullets:
            bullet.draw(world_surface, camera)

        for enemy in enemy_list:
            enemy.draw(world_surface, camera)

        pygame.transform.scale(world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)
        # screen.blit(world_surface, (0, 0))

        if debug:
            player_pos_text = f"Player World Pos: ({int(player.rect.x)}, {int(player.rect.y)})"
            cam_pos_text = f"Camera World Pos: ({int(camera.rect.x)}, {int(camera.rect.y)})"
            fps_text = f"FPS: {int(clock.get_fps())}"
            bullet_text = f"Bullets: {len(bullets)}"

            enemy_text = f"Enemies: {len(enemy_list)}"
            wave_text = f"Wave: {wave_number} (Active: {wave_active})"
            spawning_text = f"To Spawn: {enemies_to_spawn_this_wave}"

            text1 = font.render(player_pos_text, True, WHITE)
            text2 = font.render(cam_pos_text, True, WHITE)
            text3 = font.render(fps_text, True, WHITE)
            text4 = font.render(bullet_text, True, WHITE)
            text5 = font.render(enemy_text, True, WHITE)
            text6 = font.render(wave_text, True, WHITE)
            text7 = font.render(spawning_text, True, WHITE)

            screen.blit(text1, (10, 10))
            screen.blit(text2, (10, 40))
            screen.blit(text3, (10, 70))
            screen.blit(text4, (10, 100))
            screen.blit(text5, (10, 130))
            screen.blit(text6, (10, 160))
            screen.blit(text7, (10, 190))

            if not wave_active and wave_number == 0:
                wave_prompt_text = font.render("Press 'N' to start the first wave!", True, WHITE)
                screen.blit(wave_prompt_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        if game_paused:
            button_rects = draw_pause_menu(screen, font)

        pygame.display.flip()

    # --- Quit ---
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(debug=True, performance=False)
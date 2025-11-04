import pygame
import random
import sys

from World_engine.world import World
from constants import *
from assets_loader import *
from World_engine import *
from camera import Camera
from player import Player

def main(debug=False):
    pygame.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    RUNNING = True

    # Create a window with NOFRAME flag
    flags = pygame.NOFRAME | pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags, vsync=1)
    print(f"Borderless window created with size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    world_surface_width = int(SCREEN_WIDTH/ ZOOM_LEVEL)
    world_surface_height = int(SCREEN_HEIGHT/ ZOOM_LEVEL)
    world_surface = pygame.Surface((world_surface_width, world_surface_height))
    print(f"World surface created with size: {world_surface_width}x{world_surface_height}")

    try:
        tileset_image = pygame.image.load("assets/TileSet_V2.png").convert_alpha()
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
    for x in range(-5, 6):
        for y in range(-5, 6):
            world.get_or_generate_chunk(x, y)





    font = pygame.font.Font(None, 30)

    while RUNNING:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Exit on ESCAPE
                    RUNNING = False

        world_surface.fill("red")

        player.update(dt, world, camera)
        camera.update(player)

        cam_chunk_x = camera.rect.center[0] // (CHUNK_SIZE * TILE_SIZE)
        cam_chunk_y = camera.rect.center[1] // (CHUNK_SIZE * TILE_SIZE)
        for y in range(cam_chunk_y - 4, cam_chunk_y + 4):
            for x in range(cam_chunk_x - 4, cam_chunk_x + 4):
                chunk_to_draw = world.get_or_generate_chunk(x, y)
                chunk_to_draw.draw(world_surface, camera)

        screen_mouse_pos = pygame.mouse.get_pos()
        # Scale the mouse position down to match the world_surface
        world_mouse_x = screen_mouse_pos[0] / ZOOM_LEVEL
        world_mouse_y = screen_mouse_pos[1] / ZOOM_LEVEL

        player.draw(world_surface, camera, (world_mouse_x, world_mouse_y))

        pygame.transform.scale(world_surface, (SCREEN_WIDTH, SCREEN_HEIGHT), screen)



        if debug:
            player_pos_text = f"Player World Pos: ({int(player.rect.x)}, {int(player.rect.y)})"
            cam_pos_text = f"Camera World Pos: ({int(camera.rect.x)}, {int(camera.rect.y)})"
            fps_text = f"FPS: {int(clock.get_fps())}"

            text1 = font.render(player_pos_text, True, WHITE)
            text2 = font.render(cam_pos_text, True, WHITE)
            text3 = font.render(fps_text, True, WHITE)

            screen.blit(text1, (10, 10))
            screen.blit(text2, (10, 40))
            screen.blit(text3, (10, 70))

        pygame.display.flip()

    # --- Quit ---
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main(debug=True)
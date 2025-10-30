import pygame
from constants import *



def main(debug=False):
    pygame.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    RUNNING = True

    # Create a window with NOFRAME flag
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
    print(f"Borderless window created with size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")




    while RUNNING:
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Exit on ESCAPE
                    RUNNING = False



        clock.tick(60)

if __name__ == "__main__":
    main()
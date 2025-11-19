import pygame
from constants import *

def draw_game_over_screen(screen, font):
    """
    Draws a "Game Over" screen with a Quit button.
    Returns a dictionary containing the rect for the quit button.
    """
    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((100, 0, 0, 200)) # Dark red overlay
    screen.blit(overlay, (0, 0))

    title_text = font.render("Game Over", True, WHITE)
    quit_text = font.render("Quit Game", True, WHITE)

    # Get mouse position for hover checks
    mx, my = pygame.mouse.get_pos()

    # Button Rects
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    title_rect = title_text.get_rect(center=(center_x, center_y - 50))
    quit_btn_rect = quit_text.get_rect(center=(center_x, center_y + 50))

    # --- Draw hover effect ---
    if quit_btn_rect.collidepoint(mx, my):
        pygame.draw.rect(screen, (50, 50, 50), quit_btn_rect.inflate(20, 10))

    # Draw text
    screen.blit(title_text, title_rect)
    screen.blit(quit_text, quit_btn_rect)

    # Return the rects for click detection
    return {
        "quit": quit_btn_rect
    }

def handle_game_over_click(mouse_pos, button_rects):
    if not button_rects:
        return None

    if button_rects["quit"].collidepoint(mouse_pos):
        return "quit"

    return None
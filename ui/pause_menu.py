import pygame
from constants import *

def draw_pause_menu(screen, font):
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

    # Button Rects
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

def handle_pause_click(mouse_pos, button_rects):
    """Checks for clicks on the pause menu buttons."""
    if not button_rects:
        return None

    if button_rects["resume"].collidepoint(mouse_pos):
        return "resume"
    if button_rects["options"].collidepoint(mouse_pos):
        return "options"
    if button_rects["quit"].collidepoint(mouse_pos):
        return "quit"
    return None
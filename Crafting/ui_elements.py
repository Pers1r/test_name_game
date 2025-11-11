import pygame
from constants import WHITE


class CraftingButton:
    """A simple UI button for the crafting menu."""
    def __init__(self, item, rect, text):
        self.item = item
        self.rect = rect
        self.text = text

        self.color_normal = (50, 50, 50)
        self.color_hover = (80, 80, 80)
        self.font = pygame.font.Font(None, 30)

        self.icon = pygame.transform.scale(item.image, (rect.height - 10, rect.height - 10))
        self.text_surf = self.font.render(text, True, WHITE)

    def draw(self, screen, mouse_x, mouse_y):
        is_hovered = self.rect.collidepoint(mouse_x, mouse_y)

        # Draw background
        color = self.color_hover if is_hovered else self.color_normal
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 1) # Border

        # Draw icon
        icon_rect = self.icon.get_rect(centery=self.rect.centery, x=self.rect.x + 5)
        screen.blit(self.icon, icon_rect)

        # Draw text
        text_rect = self.text_surf.get_rect(centery=self.rect.centery, x=icon_rect.right + 10)
        screen.blit(self.text_surf, text_rect)
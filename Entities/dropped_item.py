import pygame
from constants import *


class DroppedItem(pygame.sprite.Sprite):
    """
    Represents an item on the ground that can be picked up.
    """
    def __init__(self, world_x, world_y, item_prototype):
        super().__init__()

        self.item_prototype = item_prototype

        self.image = pygame.transform.scale(item_prototype.image, (TILE_SIZE // 2, TILE_SIZE // 2))
        self.rect = self.image.get_rect(center=(world_x, world_y))

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 60000
        self.is_alive = True

    def update(self):
        """Checks if the item's lifetime has expired."""
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.is_alive = False

    def check_pickup(self, player, inventory):
        """
        Checks if the player is colliding with this item.
        If so, tries to add it to the inventory and disappears.
        """
        if self.rect.colliderect(player.rect):
            # Try to add the item
            success = inventory.add_item(self.item_prototype)
            if success:
                self.is_alive = False

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.rect)
        surface.blit(self.image, screen_rect)
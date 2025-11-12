import pygame
from constants import *
from .item import Item, BuildableItem


class ItemSlot:
    """Represents one slot in the inventory."""
    def __init__(self):
        self.item = None
        self.quantity = 0

    def set_item(self, item, quantity=1):
        self.item = item
        self.quantity = quantity

    def clear(self):
        self.item = None
        self.quantity = 0

    def add_quantity(self, quantity):
        self.quantity += quantity


class Inventory:
    """Manages all the player's item slots and hotbar."""
    def __init__(self, hotbar_size=8, full_size=32):
        self.hotbar_size = hotbar_size
        self.full_size = full_size

        self.slots = [ItemSlot() for _ in range(self.full_size)]
        self.is_open = False
        self.selected_slot_index = 0
        self.max_stack = 100

        self.slot_size = 56
        self.slot_padding = 8
        self.hotbar_rect = pygame.Rect(
            (SCREEN_WIDTH - (hotbar_size * (self.slot_size + self.slot_padding))) / 2,
            SCREEN_HEIGHT - (self.slot_size + self.slot_padding * 2),
            hotbar_size * (self.slot_size + self.slot_padding) + self.slot_padding,
            self.slot_size + self.slot_padding * 2
        )

        self.font_small = pygame.font.Font(None, 24)

    def get_selected_item_slot(self):
        """Returns the ItemSlot object currently selected on the hotbar."""
        return self.slots[self.selected_slot_index]

    def add_item(self, item_to_add, quantity=1):
        """
        Adds an item to the inventory, stacking up to self.max_stack.
        Returns True if the item was fully added, False otherwise.
        """
        item_id = item_to_add.item_id
        for slot in self.slots:
            if slot.item and slot.item.item_id == item_id and slot.quantity < self.max_stack:
                space_available = self.max_stack - slot.quantity
                add_amount = min(quantity, space_available)

                slot.add_quantity(add_amount)
                quantity -= add_amount
                if quantity <= 0:
                    return True

        for slot in self.slots:
            if slot.item is None:
                add_amount = min(quantity, self.max_stack)
                slot.set_item(item_to_add, add_amount)
                quantity -= add_amount

                if quantity <= 0:
                    return True

        if quantity > 0:
            print(f"Inventory full. Could not add {quantity} of {item_id}")
            return False

        return True


    def handle_input(self, event):
        """Handles key presses for selecting hotbar slots."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: self.selected_slot_index = 0
            if event.key == pygame.K_2: self.selected_slot_index = 1
            if event.key == pygame.K_3: self.selected_slot_index = 2
            if event.key == pygame.K_4: self.selected_slot_index = 3
            if event.key == pygame.K_5: self.selected_slot_index = 4
            if event.key == pygame.K_6: self.selected_slot_index = 5
            if event.key == pygame.K_7: self.selected_slot_index = 6
            if event.key == pygame.K_8: self.selected_slot_index = 7

    def draw_hotbar(self, screen):
        """Draws the hotbar on the screen."""
        bg_surface = pygame.Surface(self.hotbar_rect.size, pygame.SRCALPHA)
        bg_surface.fill((20, 20, 20, 200))
        screen.blit(bg_surface, self.hotbar_rect.topleft)

        for i in range(self.hotbar_size):
            slot = self.slots[i]
            x = self.hotbar_rect.x + self.slot_padding + (i * (self.slot_size + self.slot_padding))
            y = self.hotbar_rect.y + self.slot_padding

            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            if i == self.selected_slot_index:
                pygame.draw.rect(screen, "yellow", slot_rect, 2)
            else:
                pygame.draw.rect(screen, (80, 80, 80), slot_rect, 1)

            if slot.item:
                # Center the icon
                icon = pygame.transform.scale(slot.item.image, (self.slot_size - 8, self.slot_size - 8))
                icon_rect = icon.get_rect(center=slot_rect.center)
                screen.blit(icon, icon_rect)

                # Draw quantity
                if slot.quantity > 1:
                    qty_text = self.font_small.render(str(slot.quantity), True, WHITE)
                    qty_rect = qty_text.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    screen.blit(qty_text, qty_rect)

    def draw_inventory(self, screen):
        """Draws the full inventory screen when 'E' is pressed."""
        if not self.is_open:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        cols = self.hotbar_size
        rows = self.full_size // cols

        inv_width = cols * (self.slot_size + self.slot_padding) + self.slot_padding
        inv_height = rows * (self.slot_size + self.slot_padding) + self.slot_padding

        inv_x = (SCREEN_WIDTH - inv_width) // 2
        inv_y = (SCREEN_HEIGHT - inv_height) // 2

        inv_bg_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        pygame.draw.rect(screen, (20, 20, 20), inv_bg_rect)
        pygame.draw.rect(screen, (80, 80, 80), inv_bg_rect, 2)

        for i in range(self.full_size):
            slot = self.slots[i]
            row = i // cols
            col = i % cols

            x = inv_x + self.slot_padding + (col * (self.slot_size + self.slot_padding))
            y = inv_y + self.slot_padding + (row * (self.slot_size + self.slot_padding))

            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)

            # Highlight hotbar slots
            if i < self.hotbar_size:
                 pygame.draw.rect(screen, (50, 50, 50), slot_rect)

            # Draw slot border
            if i == self.selected_slot_index:
                pygame.draw.rect(screen, "yellow", slot_rect, 2)
            else:
                pygame.draw.rect(screen, (80, 80, 80), slot_rect, 1)

            # Draw item icon and quantity
            if slot.item:
                icon = pygame.transform.scale(slot.item.image, (self.slot_size - 8, self.slot_size - 8))
                icon_rect = icon.get_rect(center=slot_rect.center)
                screen.blit(icon, icon_rect)

                if slot.quantity > 1:
                    qty_text = self.font_small.render(str(slot.quantity), True, WHITE)
                    qty_rect = qty_text.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    screen.blit(qty_text, qty_rect)

    def remove_item(self, slot_index, quantity):
        """Removes a specific quantity from an item slot."""
        slot = self.slots[slot_index]
        if slot.item:
            slot.quantity -= quantity
            if slot.quantity <= 0:
                slot.clear()
            return True
        return False



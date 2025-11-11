import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from .ui_elements import CraftingButton
from Inventory.item import Item, BuildableItem, ToolItem


class CraftingManager:
    """
    Manages the UI and logic for crafting stations like the workbench.
    """
    def __init__(self, inventory_manager):
        self.inventory_manager = inventory_manager
        self.is_open = False
        self.font_title = pygame.font.Font(None, 48)
        self.font_item = pygame.font.Font(None, 30)

        self.window_rect = pygame.Rect(0, 0, 400, 500)
        self.window_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.workbench_recipes = [
            "default_tool",
            "work_branch",
            "elevator_down",
        ]

        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        """Creates the UI buttons for the workbench recipes."""
        x_start = self.window_rect.x + 20
        y_start = self.window_rect.y + 80
        btn_height = 50
        btn_width = self.window_rect.width - 40

        for i, item_id in enumerate(self.workbench_recipes):
            item = self.inventory_manager.item_factory.get(item_id)
            if not item:
                print(f"Warning: Could not create crafting button for missing item {item_id}")
                continue

            y_pos = y_start + i * (btn_height + 10)
            btn_rect = pygame.Rect(x_start, y_pos, btn_width, btn_height)

            self.buttons.append(
                CraftingButton(item, btn_rect, f"Buy {item.name}")
            )

    def open_workbench(self, workbench_building):
        """Opens the crafting UI."""
        self.is_open = True
        print(f"Interacted with workbench at {workbench_building.world_rect.topleft}")

    def close_ui(self):
        """Closes any open crafting UI."""
        self.is_open = False

    def handle_input(self, event):
        """Handles mouse clicks on crafting buttons."""
        if not self.is_open:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is outside the window to close it
            if not self.window_rect.collidepoint(event.pos):
                self.close_ui()
                return

            # Check buttons
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    self.buy_item(button.item)
                    break

    def buy_item(self, item):
        """
        'Buys' an item (adds it to inventory).
        In the future, this will check for resources.
        """
        print(f"Crafting/Buying: {item.name}")
        success = self.inventory_manager.inventory.add_item(item)
        if not success:
            print("Inventory is full!")
            # TODO: Show a message to the player

    def draw(self, screen):
        """Draws the crafting window."""
        if not self.is_open:
            return

        # 1. Draw window background
        pygame.draw.rect(screen, (20, 20, 20), self.window_rect)
        pygame.draw.rect(screen, (80, 80, 80), self.window_rect, 2)

        # 2. Draw title
        title_text = self.font_title.render("Workbench", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.window_rect.centerx, y=self.window_rect.y + 20)
        screen.blit(title_text, title_rect)

        # 3. Draw buttons
        mx, my = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(screen, mx, my)
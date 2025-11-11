import pygame
import math
from constants import *
from Entities.dropped_item import DroppedItem

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, enemy_damage, block_damage):
        super().__init__()

        self.pos = pygame.Vector2(x, y)
        self.speed = BULLET_SPEED

        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.speed

        self.rect = pygame.Rect(x-2, y-2, BULLET_SIZE, BULLET_SIZE)

        self.lifetime = BULLET_LIFETIME

        self.enemy_damage = enemy_damage
        self.block_damage = block_damage

    def update(self, dt, world, enemy_list, dropped_items_list, item_factory):
        """
        Update the bullet's position and check for collisions.
        We now pass in dropped_items_list and item_factory.
        """
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        self.lifetime -= dt

        grid_x = int(self.pos.x // TILE_SIZE)
        grid_y = int(self.pos.y // TILE_SIZE)
        tile = world.get_tile_at_grid_pos(grid_x, grid_y)

        if tile and not tile.is_bullet_penetrable:
            drop_id = world.damage_tile(grid_x, grid_y, self.block_damage)

            if drop_id:
                item_proto = item_factory.get(drop_id)
                if item_proto:
                    # Spawn the item at the block's center
                    world_x = (grid_x * TILE_SIZE) + (TILE_SIZE // 2)
                    world_y = (grid_y * TILE_SIZE) + (TILE_SIZE // 2)
                    new_drop = DroppedItem(world_x, world_y, item_proto)
                    dropped_items_list.append(new_drop)
                else:
                    print(f"Error: No item prototype found for drop_id '{drop_id}'")
            self.lifetime = 0
            return


        for enemy in enemy_list:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.lifetime = 0
                break

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.rect)

        pygame.draw.circle(surface, "yellow", screen_rect.center, 4)


import pygame
import math
from constants import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()

        self.pos = pygame.Vector2(x, y)
        self.speed = 700

        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.speed

        self.rect = pygame.Rect(x-2, y-2, 4, 4)

        self.lifetime = 2.0

    def update(self, dt, world, enemy_list):
        self.pos += self.velocity * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        self.lifetime -= dt

        grid_x = int(self.pos.x // TILE_SIZE)
        grid_y = int(self.pos.y // TILE_SIZE)
        tile = world.get_tile_at_grid_pos(grid_x, grid_y)

        if tile and not tile.is_bullet_penetrable:
            self.lifetime = 0
            return

        for enemy in enemy_list:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(5)
                self.lifetime = 0
                break

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.rect)

        pygame.draw.circle(surface, "yellow", screen_rect.center, 4)


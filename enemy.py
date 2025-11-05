import pygame
import math
from constants import *
from pathfinding import astar

AVOIDANCE_RADIUS = TILE_SIZE
SEPARATION_STRENGTH = 1.5

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, TILE_SIZE//2, TILE_SIZE//2 )
        self.rect.center = self.pos

        self.velocity = pygame.Vector2(0, 0)
        self.speed = 100
        self.health = 10
        self.is_alive = True

        self.path = []
        self.path_index = 0
        self.path_recalc_delay = 1000
        self.last_path_recalc_time = 0

    def update(self, dt, player, world, enemy_list):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_path_recalc_time > self.path_recalc_delay:
            self.last_path_recalc_time = current_time

            start_grid = (int(self.pos.x // TILE_SIZE), int(self.pos.y// TILE_SIZE))
            end_grid = (int(player.pos.x // TILE_SIZE), int(player.pos.y // TILE_SIZE))

            if start_grid != end_grid:
                grid_path = astar(world, start_grid, end_grid)
                if grid_path and len(grid_path) > 1:
                    self.path = [pygame.Vector2(x*TILE_SIZE + TILE_SIZE/2, y*TILE_SIZE + TILE_SIZE/2) for x, y in grid_path[1:]]
                    self.path_index = 0
                else:
                    self.path = []

        # --- Low-Level: Steering (runs every frame) ---

        seek_force = pygame.Vector2(0, 0)

        # A) Path-Following
        if self.path_index < len(self.path):
            target_pos = self.path[self.path_index]
            direction_to_target = target_pos - self.pos

            if direction_to_target.magnitude() < TILE_SIZE * 0.5:
                self.path_index += 1

            if direction_to_target.magnitude() > 0:
                seek_force = direction_to_target.normalize()

        # B) Fallback: No Path (or path finished)
        else:
            direction_to_player = player.pos - self.pos
            if direction_to_player.magnitude() > 0:
                seek_force = direction_to_player.normalize()

        # Force 2: Separate from other enemies
        separation_force = pygame.Vector2(0, 0)
        for enemy in enemy_list:
            if enemy is not self:
                distance = (self.pos - enemy.pos).magnitude()
                if 0 < distance < AVOIDANCE_RADIUS:
                    push_away = (self.pos - enemy.pos)
                    separation_force += push_away.normalize() / (distance / AVOIDANCE_RADIUS)

        if separation_force.magnitude() > 0:
            separation_force = separation_force.normalize()

        # Combine forces
        total_force = seek_force + (separation_force * SEPARATION_STRENGTH)

        # Set final velocity
        if total_force.magnitude() > 0:
            self.velocity = total_force.normalize()
        else:
            self.velocity = pygame.Vector2(0, 0)

        # move on X
        self.pos.x += self.velocity.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)

        # collisions on X
        collidable_tiles = world.get_collidable_tiles_near(self.rect)
        self.collide_horizontally(collidable_tiles)

        # move on Y
        self.pos.y += self.velocity.y * self.speed * dt
        self.rect.centery = round(self.pos.y)

        # collisions on Y
        collidable_tiles = world.get_collidable_tiles_near(self.rect)
        self.collide_vertically(collidable_tiles)

        if self.rect.colliderect(player.rect):
            print("Enemy hit the player!")

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_alive = False

    def collide_horizontally(self, tiles):
            for tile in tiles:
                if self.rect.colliderect(tile.world_rect):
                    if self.velocity.x > 0: # moving right
                        self.rect.right = tile.world_rect.left
                    if self.velocity.x < 0: # moving left
                        self.rect.left = tile.world_rect.right

                    self.pos.x = self.rect.centerx

    def collide_vertically(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.world_rect):
                if self.velocity.y > 0: # moving down
                    self.rect.bottom = tile.world_rect.top
                if self.velocity.y < 0: # moving up
                    self.rect.top = tile.world_rect.bottom

                self.pos.y = self.rect.centery

    def draw(self, surface, camera):
        screen_rect = camera.set_target(self.rect)
        pygame.draw.rect(surface, "red", screen_rect)
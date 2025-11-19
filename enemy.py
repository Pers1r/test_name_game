import pygame
import math
from constants import *
from pathfinding import astar

AVOIDANCE_RADIUS = TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, ENEMY_SIZE, ENEMY_SIZE)
        self.rect.center = self.pos

        self.velocity = pygame.Vector2(0, 0)
        self.speed = ENEMY_SPEED
        self.health = ENEMY_HEALTH
        self.is_alive = True

        # --- Targeting & Attack ---
        self.target = None # Will store a Player or Building object
        self.damage = ENEMY_DAMAGE
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN
        self.attack_timer = 0

        self.path = []
        self.path_index = 0
        self.path_recalc_delay = PATH_RECALC_DELAY
        self.last_path_recalc_time = 0

    def find_new_target(self, player, world, main_crystal):
        """Sets self.target based on priority: Crystal > Player > Buildings."""

        if main_crystal and main_crystal.is_alive:
            self.target = main_crystal
            self.path = []
            return

        if player.is_alive:
            self.target = player
            self.path = []
            return

        closest_building = None
        min_dist = float('inf')

        for building in world.buildings_list:
            if building.is_alive:
                try:
                    dist = (self.pos - building.rect.center).magnitude_squared()
                except AttributeError:
                    dist = (self.pos - building.world_rect.center).magnitude_squared()
                if dist < min_dist:
                    min_dist = dist
                    closest_building = building

        if closest_building:
            self.target = closest_building
            self.path = []
            return

    def update(self, dt, player, world, enemy_list, main_crystal):
        current_time = pygame.time.get_ticks()
        self.attack_timer -= dt

        if self.target and not self.target.is_alive:
            self.target = None
            self.path = []

        # "Target Lock" for buildings
        if self.target and hasattr(self.target, 'item_id') and self.target.item_id != "main_crystal":
            # Target is a non-crystal building, stay locked
            pass
        else:
            # Re-evaluate target if no target, or if target is player/crystal
            if self.target is None:
                self.find_new_target(player, world, main_crystal)

        target_rect = None
        target_center = None
        if self.target:
            try:
                target_rect = self.target.rect
            except AttributeError:
                target_rect = self.target.world_rect
            target_center = pygame.Vector2(target_rect.center)

# --- 2. PATHFINDING (if target exists) ---
        if self.target:
            if not self.path or current_time - self.last_path_recalc_time > self.path_recalc_delay:
                self.last_path_recalc_time = current_time
                start_grid = (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))

                # Path to the target's rect center (using our helper)
                end_grid = (int(target_center.x // TILE_SIZE), int(target_center.y // TILE_SIZE))

                if start_grid != end_grid:
                    # This call is now safe and will not freeze the game
                    grid_path = astar(world, start_grid, end_grid)
                    if grid_path and len(grid_path) > 1:
                        self.path = [pygame.Vector2(x*TILE_SIZE + TILE_SIZE/2, y*TILE_SIZE + TILE_SIZE/2) for x, y in grid_path[1:]]
                        self.path_index = 0
                    else:
                        self.path = [] # No path found

        # --- 3. MOVEMENT & ATTACKING ---
        seek_force = pygame.Vector2(0, 0)

        if self.target:
            # Check for attack range (using helper rect)
            if self.rect.colliderect(target_rect):
                # --- IN ATTACK RANGE ---
                self.velocity = pygame.Vector2(0, 0) # Stop moving
                if self.attack_timer <= 0:
                    self.target.take_damage(self.damage)
                    self.attack_timer = self.attack_cooldown
            else:
                # --- OUTSIDE ATTACK RANGE: MOVE ---
                # A) Path-Following
                if self.path_index < len(self.path):
                    target_pos = self.path[self.path_index]
                    direction_to_target = target_pos - self.pos

                    if direction_to_target.magnitude() < TILE_SIZE * 0.5:
                        self.path_index += 1
                    if direction_to_target.magnitude() > 0:
                        seek_force = direction_to_target.normalize()

                # B) Fallback: No Path (using helper center)
                else:
                    direction_to_target = target_center - self.pos
                    if direction_to_target.magnitude() > 0:
                        seek_force = direction_to_target.normalize()
        else:
            self.velocity = pygame.Vector2(0, 0)


        # --- 4. APPLY FORCES (Separation) ---
        separation_force = pygame.Vector2(0, 0)
        for enemy in enemy_list:
            if enemy is not self:
                distance = (self.pos - enemy.pos).magnitude()
                if 0 < distance < AVOIDANCE_RADIUS:
                    push_away = (self.pos - enemy.pos)
                    separation_force += push_away.normalize() / (distance / AVOIDANCE_RADIUS)

        if separation_force.magnitude() > 0:
            separation_force = separation_force.normalize()

        total_force = seek_force + (separation_force * SEPARATION_STRENGTH)
        if total_force.magnitude() > 0:
            self.velocity = total_force.normalize()

        # --- 5. PHYSICS & COLLISION ---
        self.pos.x += self.velocity.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        collidable_tiles = world.get_collidable_tiles_near(self.rect)
        self.collide_horizontally(collidable_tiles)

        self.pos.y += self.velocity.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        collidable_tiles = world.get_collidable_tiles_near(self.rect)
        self.collide_vertically(collidable_tiles)

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
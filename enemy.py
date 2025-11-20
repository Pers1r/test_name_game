import pygame
import math
from constants import *
from pathfinding import astar

AVOIDANCE_RADIUS = TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, ENEMY_SIZE-1, ENEMY_SIZE-1)
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

    def get_target_center(self, target):
        """Helper to safely get center of target (Player uses .rect, Buildings use .world_rect)"""
        if hasattr(target, 'rect'):
            return pygame.Vector2(target.rect.center)
        elif hasattr(target, 'world_rect'):
            return pygame.Vector2(target.world_rect.center)
        return pygame.Vector2(0, 0)

    def find_new_target(self, player, world, main_crystal):
        """
        Sets self.target based on Distance first, then Priority.
        Priority Order: Crystal (0) > Player (1) > Buildings (2)
        Logic: Find the closest object. Anything else within +TILE_SIZE distance
               is considered 'equal' distance, and we pick based on priority.
        """
        candidates = [] # Stores dicts: {'obj': object, 'dist': float, 'priority': int}

        # 1. Evaluate Main Crystal (Priority 0)
        if main_crystal and main_crystal.is_alive:
            dist = (self.pos - self.get_target_center(main_crystal)).magnitude()
            candidates.append({'obj': main_crystal, 'dist': dist, 'priority': 0})

        # 2. Evaluate Player (Priority 1)
        if player.is_alive:
            dist = (self.pos - self.get_target_center(player)).magnitude()
            candidates.append({'obj': player, 'dist': dist, 'priority': 1})

        # 3. Evaluate Closest Building (Priority 2)
        closest_b = None
        min_b_dist = float('inf')
        # Optimization: Check buildings, but we only care about the closest one to add to candidates
        for building in world.buildings_list:
            if building.is_alive and building.item_id != "main_crystal":
                if building.item_id in ["tree_small", "tree_large", "bush"]:
                    continue
                d = (self.pos - building.world_rect.center).magnitude()
                if d < min_b_dist:
                    min_b_dist = d
                    closest_b = building

        if closest_b:
            candidates.append({'obj': closest_b, 'dist': min_b_dist, 'priority': 2})

        # --- Decision Logic ---
        if not candidates:
            self.target = None
            return

        # Sort by distance to find the absolute closest
        candidates.sort(key=lambda x: x['dist'])
        min_dist = candidates[0]['dist']

        # Filter: Keep only targets that are within the "mostly equal" range (Min Dist + TILE_SIZE)
        # e.g., if Player is 100px away and Crystal is 120px, 120 < 100+32, so Crystal is valid.
        valid_options = [c for c in candidates if c['dist'] <= min_dist + TILE_SIZE]

        # Sort valid options by Priority (Low number = High Priority)
        valid_options.sort(key=lambda x: x['priority'])

        # Pick the winner
        self.target = valid_options[0]['obj']
        self.path = [] # Reset path for new target

    def update(self, dt, player, world, enemy_list, main_crystal):
        current_time = pygame.time.get_ticks()
        self.attack_timer -= dt

        if self.target and not self.target.is_alive:
            self.target = None
            self.path = []

        # "Target Lock" for buildings
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

        # --- 2. PATHFINDING ---
        if self.target:
            dist_to_target = (self.pos - target_center).magnitude()

            # Recalculate path only if far away
            if dist_to_target > TILE_SIZE * 1.5:
                if not self.path or current_time - self.last_path_recalc_time > self.path_recalc_delay:
                    self.last_path_recalc_time = current_time
                    start_grid = (int(self.pos.x // TILE_SIZE), int(self.pos.y // TILE_SIZE))
                    end_grid = (int(target_center.x // TILE_SIZE), int(target_center.y // TILE_SIZE))

                    if start_grid != end_grid:
                        grid_path = astar(world, start_grid, end_grid)
                        if grid_path and len(grid_path) > 1:
                            self.path = [pygame.Vector2(x*TILE_SIZE + TILE_SIZE/2, y*TILE_SIZE + TILE_SIZE/2) for x, y in grid_path[1:]]
                            self.path_index = 0
                        else:
                            self.path = []
            else:
                self.path = []

        # --- 3. MOVEMENT & ATTACKING ---
        seek_force = pygame.Vector2(0, 0)

        if self.target:
            # FIX: Use inflate(4, 4) to detect collision even if just touching
            # This fixes the issue where enemies stand next to crystal but don't attack
            attack_range_rect = self.rect.inflate(4, 4)

            if attack_range_rect.colliderect(target_rect):
                # --- IN ATTACK RANGE ---
                self.velocity = pygame.Vector2(0, 0) # Stop moving
                if self.attack_timer <= 0:
                    # Ensure target has take_damage method
                    if hasattr(self.target, 'take_damage'):
                        self.target.take_damage(self.damage)
                    self.attack_timer = self.attack_cooldown
            else:
                # --- OUTSIDE ATTACK RANGE: MOVE ---
                if self.path_index < len(self.path):
                    target_pos = self.path[self.path_index]
                    direction_to_target = target_pos - self.pos

                    if direction_to_target.magnitude() < TILE_SIZE * 0.5:
                        self.path_index += 1
                    if direction_to_target.magnitude() > 0:
                        seek_force = direction_to_target.normalize()
                else:
                    # Fallback: Direct seek
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
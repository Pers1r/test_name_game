import pygame
import math

from bullet import Bullet
from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, debug=False):
        super().__init__()
        self.radius = PLAYER_RADIUS

        self.pos = pygame.Vector2(x, y)
        rect_size = PLAYER_RADIUS*2  # This is 16
        self.rect = pygame.Rect(0, 0, rect_size, rect_size)
        self.rect.center = (x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.angle = 0

        self.debug = debug

        self.update_zoom_properties(ZOOM_LEVEL)

        # self.shoot_delay = PLATER_SHOOT_DELAY
        self.last_shoot_time = 0

        self.health = PLAYER_HEALTH
        self.is_alive = True
        self.is_invulnerable = False
        self.invulnerability_timer = 0

        self.aim_offset = 2 / ZOOM_LEVEL
        self.aim_size = 8 / ZOOM_LEVEL

        self.original_aim_triangle = pygame.Surface((self.aim_size*2, self.aim_size*2), pygame.SRCALPHA)
        self.update_zoom_properties(ZOOM_LEVEL)

    def update_zoom_properties(self, zoom_level):
        if zoom_level == 0:
            zoom_level = 0.8
        self.aim_offset = 2 / ZOOM_LEVEL
        self.aim_size = 8 / ZOOM_LEVEL

        self.original_aim_triangle = pygame.Surface((self.aim_size*2, self.aim_size*2), pygame.SRCALPHA)

        size = self.aim_size
        p1 = (size*2, size)
        p2 = (size*0.5, size*0.5)
        p3 = (size*0.5, size*1.5)
        pygame.draw.polygon(self.original_aim_triangle, (0, 0, 0), [p1, p2, p3])


    def update(self, dt, world, camera):
        # --- Handle Invulnerability ---
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False

        # --- Don't move if dead ---
        if not self.is_alive:
            self.velocity.x, self.velocity.y = 0, 0
            return

        # Get input
        self.velocity.x, self.velocity.y = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1

        # Normalize velocity (so diagonal isn't faster)
        if self.velocity.magnitude() != 0:
            self.velocity = self.velocity.normalize()

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

    def take_damage(self, damage):
        if self.is_invulnerable or not self.is_alive:
            return

        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            print("Player has died!")

    def respawn(self, respawn_pos):
        """Called by the Game class to reset the player."""
        self.pos = pygame.Vector2(respawn_pos)
        self.rect.center = self.pos
        self.health = PLAYER_HEALTH
        self.is_alive = True
        self.is_invulnerable = True
        self.invulnerability_timer = PLAYER_INVULNERABILITY_TIME
        print("Player has respawned!")

    def draw(self, surface, camera, mouse_pos):
        if not self.is_alive:
            return

        # 1. Find stable screen rectangle
        screen_rect = camera.set_target(self.rect)
        screen_center = screen_rect.center

        # 2. Draw the main circle
        pygame.draw.circle(surface, (234,182,118), screen_rect.center, self.radius)

        # 3. Get mouse position on screen
        screen_mx, screen_my = mouse_pos
        dx = screen_mx - screen_center[0]
        dy = screen_my - screen_center[1]

        if dx != 0 or dy != 0:
            self.angle = math.atan2(dy, dx)

        # 4. Rotate original triangle
        rotated_triangle = pygame.transform.rotate(self.original_aim_triangle, -math.degrees(self.angle))

        # 5. Get new rotated rect
        rotated_rect = rotated_triangle.get_rect()

        # 6. Calculate orbit position
        orbit_dist = self.radius + self.aim_offset + (self.aim_size / 2)
        orbit_x = screen_center[0] + math.cos(self.angle) * orbit_dist
        orbit_y = screen_center[1] + math.sin(self.angle) * orbit_dist

        # 7. Set the rotated rect's center to the stable, rounded orbit position
        rotated_rect.center = (round(orbit_x), round(orbit_y))

        # 8. Blit the rotated triangle to the screen
        surface.blit(rotated_triangle, rotated_rect)

        if self.debug:
            pygame.draw.rect(surface, "purple", screen_rect, width=1)

    def shoot(self, tool_item):
        """
        Shoots a bullet using the stats from the provided tool_item.
        """
        if not self.is_alive:
            return None

        current_time = pygame.time.get_ticks()

        if current_time - self.last_shoot_time > tool_item.shoot_delay:
            self.last_shoot_time = current_time
            orbit_dist = self.radius + self.aim_offset + (self.aim_size / 2) + 5

            start_x = self.rect.centerx + math.cos(self.angle) * orbit_dist
            start_y = self.rect.centery + math.sin(self.angle) * orbit_dist

            new_bullet = Bullet(start_x, start_y, self.angle, tool_item.enemy_damage, tool_item.block_damage)
            return new_bullet
        return None

import pygame

from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # self.image = pygame.Surface((32, 32))
        # self.image.fill("red")
        self.radius = TILE_SIZE//4

        self.pos = pygame.Vector2(x, y)
        # 'self.rect' stores the player's TRUE position in the game WORLD
        self.rect = pygame.Rect(x - self.radius, y - self.radius, TILE_SIZE//2, TILE_SIZE//2)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 200

    def update(self, dt, world):
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

        # --- COLLISION LOGIC ---
        # --- MOVEMENT LOGIC ---
        # We multiply by 'dt' (delta time) for frame-rate independent movement

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

    def draw(self, screen, camera):
        """
        To draw the player, we MUST apply the camera offset.
        We ask the camera "where on the SCREEN should I draw this world rect?"
        """
        screen_rect = camera.set_target(self.rect)
        pygame.draw.circle(screen, "red", screen_rect.center, self.radius)
        # screen.blit(self.image, screen_rect)
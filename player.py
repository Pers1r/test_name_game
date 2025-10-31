import pygame

from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill("red")

        self.pos = pygame.Vector2(x, y)
        # 'self.rect' stores the player's TRUE position in the game WORLD
        self.rect = self.image.get_rect(center=self.pos)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 400

    def update(self, dt):
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

        # Update world position
        # We multiply by 'dt' (delta time) for frame-rate independent movement
        self.pos += self.velocity * self.speed * dt

        self.rect.center = self.pos

    def draw(self, screen, camera):
        """
        To draw the player, we MUST apply the camera offset.
        We ask the camera "where on the SCREEN should I draw this world rect?"
        """
        screen_rect = camera.set_target(self.rect)
        screen.blit(self.image, screen_rect)
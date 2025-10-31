import pygame



class Camera:
    def __init__(self, width, height):
        """
        Initializes the camera.
        The camera is just a pygame.Rect that we move around.
        Its topleft (x, y) is the "offset" for the entire world.
        """
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def set_target(self, target_rect):
        """
        This is the most important method.
        It takes a pygame.Rect in *world coordinates* (like a player or tile)
        and returns a *new* Rect in *screen coordinates*.

        How it works:
        It subtracts the camera's topleft (x, y) from the target's (x, y).
        """
        return target_rect.move(-self.rect.x, -self.rect.y)

    def update(self, target):
        """
        This method makes the camera follow a target (like the player).
        It centers the camera on the target.
        """
        x = int(-self.width / 2 + target.rect.centerx)
        y = int(-self.height / 2 + target.rect.centery)

        self.rect.x = x
        self.rect.y = y

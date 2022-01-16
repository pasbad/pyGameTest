import pygame

white = (255, 255, 255)

### Characters ###
class Elsa(pygame.sprite.Sprite):
    """
    This class represents the main player
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/testElsa.png")
        self.image.set_colorkey(white)     # Set our transparent color
        self.rect = self.image.get_rect()

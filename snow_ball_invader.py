# Import pygame module
import pygame

# Get clock
clock = pygame.time.Clock()

# Import pygame.locals ... for reading keyboard inputs?
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT
)

# Initialize pygame
pygame.init()

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
        self.lastShot = pygame.time.get_ticks()

    def update(self, pressedKeys):
        # Move
        if pressedKeys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressedKeys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressedKeys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressedKeys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Keep Elsa on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screenWidth:
            self.rect.right = screenWidth
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screenHeight:
            self.rect.bottom = screenHeight

        # Shoot
        cooldown = 500 # ms
        if pressedKeys[pygame.K_SPACE] and pygame.time.get_ticks() - self.lastShot > cooldown: # and cooldown?
            self.lastShot = pygame.time.get_ticks()
            snowBall = PlayerSnowBall(self.rect.centerx, self.rect.centery)
            playerSnowBalls.add(snowBall)

class PlayerSnowBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # To replace with a snowball image?
        #pygame.draw.circle(self.image, self.color, (self.width // 2, self.height // 2), 5)
        self.image = pygame.Surface([5, 5])
        self.image.fill(white)
        self.image.set_colorkey((0, 0, 0))

        pygame.draw.circle(self.image, white, (3,3), 6)

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x += 3
        if self.rect.x > screenWidth:
            self.kill()

class Opponent(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("sprites/testOlaf.png")
        self.image.set_colorkey(white)  # Set our transparent color
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.y += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75: # This should be a parameter of the screen
            self.move_direction *= -1
            self.rect.x -= 5 # Should we make this smoother?
            self.move_counter *= self.move_direction

def createOpponents(group):
    # Create a group of opponents... should be a function of the level?
    rows = 7
    cols = 5
    for row in range(rows):
        for item in range(cols):
            opponent = Opponent(screenWidth - 60 - item * 60, 120 + row * 60) # y -> row... start at screenHeight + opponent max height  + y moving path (75)
            group.add(opponent)


# Define screen constants ... to tweak for full screen
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))

# Sprite list creation and player sprite creation
sprites = pygame.sprite.Group()
elsa = Elsa()
elsa.rect.x = 200
elsa.rect.y = 300

opponents = pygame.sprite.Group()
createOpponents(opponents)

playerSnowBalls = pygame.sprite.Group()

# Set the status of the main loop
isGameRunning = True

while isGameRunning:

    # Look for events
    for event in pygame.event.get():

        # Close window
        if event.type == QUIT:
            isGameRunning = False
            break

        # Key pressed
        if event.type == KEYDOWN:
            # Escape
            if event.key == K_ESCAPE:
                isGameRunning = False
                break

    # Update Elsa based on pressed keys
    pressedKeys = pygame.key.get_pressed()
    elsa.update(pressedKeys)

    ### Draw background ###
    screen.fill((0,0,0))

    ### Draw enemies and mobs ###
    opponents.update()
    opponents.draw(screen)

    ### Draw snowballs ###
    playerSnowBalls.update()
    playerSnowBalls.draw(screen)

    ### Draw characters ###
    screen.blit(elsa.image, elsa.rect)

    pygame.display.flip()
    clock.tick(60)


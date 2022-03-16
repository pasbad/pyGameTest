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
font = pygame.font.SysFont("Segoe UI", 35)
debug = True

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((800, 600))
screenWidth = screen.get_width()
screenHeight = screen.get_height()
xSpeed = 5 #int(screenWidth*5/600)
ySpeed = 5 #int(screenHeight*5/800)

opponentHeight = 60
opponentWidth = 60
opponentRow = 12
opponentCol = 5

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
            self.rect.move_ip(0, -ySpeed)
        if pressedKeys[K_DOWN]:
            self.rect.move_ip(0, ySpeed)
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
        self.image = pygame.Surface([7, 7])
        pygame.draw.circle(self.image, white, (4,4), 3)
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x += xSpeed
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
        self.move_direction = 3

    def update(self):
        self.rect.y += self.move_direction
        self.move_counter += self.move_direction

    def checkDirection(self):
        reverse = self.rect.bottom >= screenHeight
        reverse |= self.rect.top <= 0
        return reverse

    def checkCollisions(self):
        for snowBall in playerSnowBalls:
            if pygame.Rect.colliderect(self.rect, snowBall.rect):
                snowBall.kill()
                self.kill()

def createOpponents(group):
    # Create a group of opponents... should be a function of the level?
    for row in range(opponentRow):
        for item in range(opponentCol):
            opponent = Opponent(screenWidth - 60 - item * opponentWidth, 30 + row * opponentHeight) # y -> row... start at screenHeight + opponent max height  + y moving path (75)
            group.add(opponent)

def displayDebug():
    fps = str(int(clock.get_fps()))
    w = "Width: " + str(screen.get_width())
    h = "Height: " + str(screen.get_height())
    textsurface = font.render(fps + " " + w + " " + h , False, white)  # "text", antialias, color
    text_rect = textsurface.get_rect(topleft=(0, 0))
    screen.blit(textsurface, text_rect)
    return

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

    ### Debug constants ###
    if debug:
        displayDebug()

    ### Draw snowballs ###
    playerSnowBalls.update()
    playerSnowBalls.draw(screen)

    ### Draw enemies and mobs ###
    opponents.update()
    opponents.draw(screen)
    rev = False
    for opponent in opponents:
        opponent.checkCollisions()
        rev |= opponent.checkDirection()

    ### Direction change + advance ###
    if rev:
        for opponent in opponents:
            opponent.move_direction *= -1
            opponent.rect.x -= screenWidth / 100

    ### Draw characters ###
    screen.blit(elsa.image, elsa.rect)

    ### Flip to screen and refresh rate ###
    pygame.display.flip()
    clock.tick(60)


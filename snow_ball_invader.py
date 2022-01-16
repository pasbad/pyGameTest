# Import pygame module
import pygame
from characters import Elsa

# Get clock
clock = pygame.time.Clock()

# Import pygame.locals ... for reading keyboard inputs?
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

# Initialize pygame
pygame.init()

# Define screen constants ... to tweak for full screen
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))

# Sprite list creation and player sprite creation
sprites = pygame.sprite.Group()
elsa = Elsa()
elsa.rect.x = 200
elsa.rect.y = 300

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
            # Up
            if event.key == K_UP:
                elsa.rect.y -= 5
            # Down
            if event.key == K_DOWN:
                elsa.rect.y += 5
            # Left
            if event.key == K_LEFT:
                elsa.rect.x -= 5
            # Right
            if event.key == K_RIGHT:
                elsa.rect.x += 5

    ### Draw background ###
    screen.fill((0,0,0))

    ### Draw enemies and mobs ###

    ### Draw characters ###
    screen.blit(elsa.image, elsa.rect)

    pygame.display.flip()
    clock.tick(60)

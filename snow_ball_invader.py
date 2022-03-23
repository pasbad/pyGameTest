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

# Controller initialization
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
    joysticks[-1].init()

# General variables
white = (255, 255, 255)
font = pygame.font.SysFont("Segoe UI", 35)
debug = False

# Screen management (and speed)
if debug:
    screen = pygame.display.set_mode((800, 600))
else:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # for some reason, fullscreen cannot debug

screenWidth = screen.get_width()
screenHeight = screen.get_height()
xSpeed = 5 #int(screenWidth*5/600)
ySpeed = 5 #int(screenHeight*5/800)
xGameOver = 0

# Opponents parameters
opponentHeight = 60
opponentWidth = 60
opponentRow = 12
opponentCol = 5

### Characters ###
class Hero(pygame.sprite.Sprite):
    def __init__(self, imageLocation, joystickId):
        super().__init__()
        self.image = pygame.image.load(imageLocation) # pygame.image.load("sprites/testElsa.png")
        self.image.set_colorkey(white)     # Set our transparent color
        self.rect = self.image.get_rect()

        self.lastShot = pygame.time.get_ticks()
        self.startPressed = False
        self.movement = [0,0]
        self.joystickId = joystickId

    def update(self, pressedKeys, events):
        shoot = False

        # Move with keyboard
        if pressedKeys[K_UP]:
            self.movement[1] = -1
        elif pressedKeys[K_DOWN]:
            self.movement[1] = 1

        if pressedKeys[K_LEFT]:
            self.movement[0] = -1
        elif pressedKeys[K_RIGHT]:
            self.movement[0] = 1

        for event in events:
            # Move with gamepad
            if event.type == pygame.JOYAXISMOTION and event.joy == self.joystickId:
                if debug:
                    print(event)
                if event.axis == 0:
                    if abs(event.value) > 0.5:
                        if event.value > 0:
                            self.movement[0] = 1
                        else:
                            self.movement[0] = -1
                    else:
                        self.movement[0] = 0
                if event.axis == 4:
                    if abs(event.value) > 0.5:
                        if event.value < 0:
                            self.movement[1] = -1
                        else:
                            self.movement[1] = 1
                    else:
                        self.movement[1] = 0

            if event.type == pygame.JOYBUTTONDOWN and event.joy == self.joystickId:
                if debug:
                    print(event)
                if event.button == 2:
                    shoot = True

            # Stop keyboard movement
            if event.type == pygame.KEYUP:
                if event.key == K_UP or event.key == K_DOWN:
                    self.movement[1] = 0
                if event.key == K_LEFT or event.key == K_RIGHT:
                    self.movement[0] = 0

        # Use movement decoded
        self.rect.move_ip(xSpeed*self.movement[0], ySpeed*self.movement[1])

        # Keep hero on screen
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
        if (pressedKeys[pygame.K_SPACE] or shoot) and pygame.time.get_ticks() - self.lastShot > cooldown: # and cooldown?
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
    def __init__(self, x, y, opponentLevel):
        super().__init__()

        shootFreq = float("inf")

        if opponentLevel < 1:
            imageLocation = "sprites/testOlaf.png"
        elif opponentLevel < 2:
            imageLocation = "sprites/testAnna.png"
        elif opponentLevel < 3:
            imageLocation = "sprites/testElsa.png"
        elif opponentLevel < 4:
            imageLocation = "sprites/testAnna.png"
            shootFreq = 1000
        else:
            imageLocation = "sprites/testElsa.png"
            shootFreq = 500

        self.image = pygame.image.load(imageLocation)
        self.image.set_colorkey(white)  # Set our transparent color
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.lives = min(opponentLevel+1, 3)
        self.shootFreq = shootFreq

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
                if self.lives < 2:
                    snowBall.kill()
                else:
                    self.lives -= 1
                self.kill()

    def checkGameOver(self):
        if self.rect.x <= xGameOver:
            return True
        return False

def createOpponents(group):
    # Create a group of opponents... should be a function of the level?
    for row in range(opponentRow):
        for item in range(opponentCol):
            opponent = Opponent(screenWidth - 60 - item * opponentWidth, 30 + row * opponentHeight, 0) # y -> row... start at screenHeight + opponent max height  + y moving path (75)
            group.add(opponent)

class Life(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("sprites/testCoeur.png")
        self.image.set_colorkey(white)  # Set our transparent color
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [x, y]

def AddLives(group, count):
    x_offset = 5
    x_width = 30

    for n in range(count):
        if len(group) < 1:
            life = Life(x_offset, screenHeight)
            group.add(life)
        else:
            x = x_width*len(group) + x_offset*(len(group)+1)
            life = Life(x, screenHeight)
            group.add(life)

def displayDebug():
    fps = str(int(clock.get_fps()))
    w = "Width: " + str(screen.get_width())
    h = "Height: " + str(screen.get_height())
    textsurface = font.render(fps + " " + w + " " + h , False, white)  # "text", antialias, color
    text_rect = textsurface.get_rect(topleft=(0, 0))
    screen.blit(textsurface, text_rect)
    return

def displayButton(events):
    string = ""

    for event in events:
        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYAXISMOTION:
            if event.joy == 0:
                string += "Player 1 - "
            else:
                string += "Player 2 - "

            if event.type == pygame.JOYBUTTONDOWN:
                string += "Button Down"
            else:
                string += "Dpad"

    if string:
        textsurface = font.render(string, False, white)  # "text", antialias, color
        text_rect = textsurface.get_rect(topleft=(0, 30))
        screen.blit(textsurface, text_rect)

    return

def checkExit(joysticks_with_start_pressed, events):
    for event in events:
        if event.type == QUIT:
            return True

        # Key pressed
        if event.type == KEYDOWN:
            # Escape
            if event.key == K_ESCAPE:
                return True

        if event.type == pygame.JOYBUTTONDOWN:
            if debug:
                print(event)
            if event.button == 9:
                joysticks_with_start_pressed.append(event.joy)
            if joysticks_with_start_pressed.__contains__(event.joy) and event.button == 8:
                return True

        if event.type == pygame.JOYBUTTONUP and event.button == 9:
            if joysticks_with_start_pressed.__contains__(event.joy):
                joysticks_with_start_pressed.remove(event.joy)

    return False

def showStartScreen():
    screen.fill((0, 0, 0)) # Background
    text_surface = font.render("Appuie sur un bouton pour jouer!", True, white)
    text_rect = text_surface.get_rect(center=(screenWidth/2,screenHeight/2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    done = False
    joysticks_with_start_pressed = []

    while not done:
        events = pygame.event.get()
        exit = checkExit(joysticks_with_start_pressed, events)
        if exit:
            return True
        for event in events:
            if event.type == pygame.KEYDOWN:
                done = True
            if event.type == pygame.JOYBUTTONDOWN and event.button != 8 and event.button != 9:
                done = True

        clock.tick(60)

def showGameOverScreen():
    screen.fill((0, 0, 0)) # Background
    text_surface = font.render("Appuie sur un bouton pour recommencer", True, white)
    text_rect = text_surface.get_rect(center=(screenWidth/2,screenHeight/2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    done = False
    joysticks_with_start_pressed = []

    while not done:
        events = pygame.event.get()
        exit = checkExit(joysticks_with_start_pressed, events)
        if exit:
            return True
        for event in events:
            if event.type == pygame.KEYDOWN:
                done = True
            if event.type == pygame.JOYBUTTONDOWN and event.button != 8 and event.button != 9:
                done = True

        clock.tick(60)

# Sprite list creation and player sprite creation
sprites = pygame.sprite.Group()

elsa = Hero("sprites/testElsa.png", 0)
elsa.rect.x = 200
elsa.rect.y = 300
sprites.add(elsa)

anna = Hero("sprites/testAnna.png", 1)
anna.rect.x = 250
anna.rect.y = 350
sprites.add(anna)

opponents = pygame.sprite.Group()
createOpponents(opponents)

lives = pygame.sprite.Group()
AddLives(lives, 5)

playerSnowBalls = pygame.sprite.Group()

# Set the status of the main loop
isGameRunning = not showStartScreen()
isGameOverShown = False
joysticks_with_start_pressed = []

while isGameRunning:

    stop = False
    isGameOver = False

    # Look for events
    events = pygame.event.get()
    stop = checkExit(joysticks_with_start_pressed, events)

    # Update heros based on pressed keys
    pressedKeys = pygame.key.get_pressed()
    elsa.update(pressedKeys, events)
    anna.update(pressedKeys, events)

    ### Draw background ###
    screen.fill((0,0,0))

    ### Debug constants ###
    if debug:
        displayDebug()
        displayButton(events)

    ### Draw snowballs ###
    playerSnowBalls.update()
    playerSnowBalls.draw(screen)

    ### Draw lives ###
    lives.draw(screen)

    ### Draw enemies and mobs ###
    opponents.update()
    opponents.draw(screen)
    rev = False

    for opponent in opponents:
        opponent.checkCollisions()
        rev |= opponent.checkDirection()
        isGameOver |= opponent.checkGameOver()

    ### Direction change + advance ###
    if rev:
        for opponent in opponents:
            opponent.move_direction *= -1
            opponent.rect.x -= screenWidth / 100

    if isGameOver:

        # Show game over screen
        stop = showGameOverScreen()

        # Reset opponents
        for opponent in opponents:
            opponent.kill()
        createOpponents(opponents)

        # Remove snowballs
        for snowball in playerSnowBalls:
            snowball.kill()

        # Reset score
        # Reset lives
        for life in lives:
            life.kill()
        AddLives(lives, 5)

    if stop:
        isGameRunning = False
        break

    ### Draw characters ###
    screen.blit(elsa.image, elsa.rect)
    screen.blit(anna.image, anna.rect)

    ### Flip to screen and refresh rate ###
    pygame.display.flip()
    clock.tick(60)

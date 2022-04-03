# Import pygame module
import random

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
bottomOffset = 30
white = (255, 255, 255)
pink = (244, 147, 242)
font = pygame.font.SysFont("Segoe UI", 35)
scoreFont = pygame.font.SysFont("Segoe UI", bottomOffset - 5)
startingLevel = -1
startingLives = 5
debug = True

# Screen management (and speed)
if debug:
    screen = pygame.display.set_mode((1200, 800))
else:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # for some reason, fullscreen cannot debug
screenWidth = screen.get_width()
screenHeight = screen.get_height()

xSpeed = 5 #int(screenWidth*5/600)
ySpeed = 5 #int(screenHeight*5/800)
gracePeriod = 3000 #ms
blinkFreq = 200 # ms

# Opponents parameters
opponentHeight = 60
opponentWidth = 60
opponentRow = 12
opponentCol = 5
uniqueOpponents = 5
opponentYspeed = 4 #3
if debug:
    opponentYspeed = 1
opponentXspeed = screenWidth/50
xGameOver = 0

def GenerateOpponentLevelArray(row, col, maxOpponentLevel, currentLevel):
    array = [[0 for _ in range(col)] for _ in range(row)]
    for level in range(maxOpponentLevel):

        maxCol = currentLevel - level - 1

        for r in range(row):
            for c in range(col):

                nbRows = 2*(maxCol - c +1)
                firstRow = (row - nbRows)/2
                lastRow = firstRow + nbRows
                if c <= maxCol and r >= firstRow and r < lastRow:
                    array[r][c] += 1

    return array

### Characters ###
class Hero(pygame.sprite.Sprite):
    def __init__(self, imageLocation, joystickId):
        super().__init__()
        self.imageLocation = imageLocation
        self.image = pygame.image.load(self.imageLocation) # pygame.image.load("sprites/testElsa.png")
        self.image.set_colorkey(white)     # Set our transparent color
        self.rect = self.image.get_rect()

        self.lastShot = pygame.time.get_ticks()
        self.lastCollision = pygame.time.get_ticks() - gracePeriod

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
            snowBall = SnowBall(self.rect.centerx, self.rect.centery, True)
            playerSnowBalls.add(snowBall)

        # Check collisions
        # Collisions - snowballs
        ticksFromLastCollision = pygame.time.get_ticks() - self.lastCollision
        if ticksFromLastCollision > gracePeriod:
            for snowBall in opponentSnowBalls:
                if pygame.Rect.colliderect(self.rect, snowBall.rect):
                    RemoveLife(lives)
                    snowBall.kill()
                    self.lastCollision = pygame.time.get_ticks()
                    ticksFromLastCollision = 0

        if ticksFromLastCollision < gracePeriod:
            if round(ticksFromLastCollision/blinkFreq) % 2 == 0:
                ChangeRed(self.image, 50)
            else:
                self.ResetImage()

        # Collisions - opponents

    def ResetImage(self):
        self.image = pygame.image.load(self.imageLocation)

def ChangeRed(surface, redAddition):
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            initialColor = surface.get_at((x, y))
            initialColor[0] = max(min(redAddition+initialColor[0], 255), 0)
            surface.set_at((x, y), pygame.Color(initialColor))

class SnowBall(pygame.sprite.Sprite):
    def __init__(self, x, y, isPlayers):
        super().__init__()
        # To replace with a snowball image?
        #pygame.draw.circle(self.image, self.color, (self.width // 2, self.height // 2), 5)
        color = white
        self.speed = xSpeed
        if not isPlayers:
            color = pink
            self.speed *= -1
        self.image = pygame.Surface([7, 7])
        pygame.draw.circle(self.image, color, (4,4), 3)
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > screenWidth or self.rect.x < 0:
            self.kill()

class Opponent(pygame.sprite.Sprite):
    def __init__(self, x, y, opponentLevel, firstShot):
        super().__init__()

        shootFreq = float("inf")
        self.lastShot = firstShot

        if opponentLevel < 1:
            imageLocation = "sprites/testOlaf.png"
        elif opponentLevel < 2:
            imageLocation = "sprites/testAnna.png"
        elif opponentLevel < 3:
            imageLocation = "sprites/testElsa.png"
        elif opponentLevel < 4:
            imageLocation = "sprites/testAnna.png"
            shootFreq = 15000
        else:
            imageLocation = "sprites/testElsa.png"
            shootFreq = 7000

        self.image = pygame.image.load(imageLocation)
        self.image.set_colorkey(white)  # Set our transparent color
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.lives = min(opponentLevel+1, 3)
        self.value = opponentLevel+1
        self.shootFreq = shootFreq

        self.move_counter = 0
        self.move_direction = opponentYspeed

    def update(self):
        self.rect.y += self.move_direction
        self.move_counter += self.move_direction
        if pygame.time.get_ticks() - self.lastShot > self.shootFreq:
            self.lastShot = pygame.time.get_ticks()
            snowBall = SnowBall(self.rect.centerx, self.rect.centery, False)
            opponentSnowBalls.add(snowBall)

    def checkDirection(self):
        reverse = self.rect.bottom >= screenHeight - bottomOffset
        reverse |= self.rect.top <= 0
        return reverse

    def checkCollisions(self):
        for snowBall in playerSnowBalls:
            if pygame.Rect.colliderect(self.rect, snowBall.rect):
                snowBall.kill()
                if self.lives < 2:
                    self.kill()
                    return self.value
                else:
                    self.lives -= 1
                    ChangeRed(self.image, 30)
        return 0

    def checkGameOver(self):
        if self.rect.x <= xGameOver:
            return True
        for hero in heros:
            if pygame.Rect.colliderect(self.rect, hero.rect):
                return True
        return False

def createOpponents(group, level, firstShotTime):

    opponentLevels = GenerateOpponentLevelArray(opponentRow, opponentCol, uniqueOpponents, level)

    # Create a group of opponents... should be a function of the level?
    for row in range(opponentRow):
        for col in range(opponentCol):
            additionnalTime = random.uniform(0, 15000)
            opponentLevel = opponentLevels[row][col]
            opponent = Opponent(screenWidth - 60 - col * opponentWidth, 30 + row * opponentHeight, opponentLevel, firstShotTime+additionnalTime) # y -> row... start at screenHeight + opponent max height  + y moving path (75)
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

def RemoveLife(group):
    length = len(group)
    if length > 0:
        group.empty()
        AddLives(group, length-1)

def displayScore():
    textSurf = scoreFont.render(str(score), False,white)
    textRect = textSurf.get_rect(bottomright=(screenWidth - 5, screenHeight))
    screen.blit(textSurf, textRect)
    return

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

def showStartScreen(level, pts):
    # Background
    screen.fill((0, 0, 0))

    # Niveau + Pts
    text_surface = font.render("Niveau: " + str(level) + " - Points: " + str(pts), True, white)
    text_rect = text_surface.get_rect(center=(screenWidth/2,screenHeight/2))
    screen.blit(text_surface, text_rect)

    # Instruction
    text_surface2 = font.render("Appuie sur un bouton pour jouer", True, white)
    text_rect2 = text_surface2.get_rect(center=(screenWidth / 2, screenHeight / 2 + 50))
    screen.blit(text_surface2, text_rect2)

    # Display
    pygame.display.flip()
    done = False
    joysticks_with_start_pressed = []

    # Set cooldown
    displayTime = pygame.time.get_ticks()
    displayCoolDown = 750

    # Listen to input
    while not done:

        events = pygame.event.get()
        exit = checkExit(joysticks_with_start_pressed, events)
        if exit:
            return True
        if pygame.time.get_ticks() - displayTime > displayCoolDown:
            for event in events:
                if event.type == pygame.KEYDOWN: # and event.key != K_DOWN and event.key != K_UP and event.key != K_LEFT and event.key != K_RIGHT and event.key != K_SPACE:
                    done = True
                if event.type == pygame.JOYBUTTONDOWN: # and event.button != 2 and event.button != 8 and event.button != 9:
                    done = True

        clock.tick(60)

def showGameOverScreen(level, pts):
    # High scores
    currentScore = (pts, level)
    score_index, highScores = WriteHighScore(currentScore)

    # Background
    screen.fill((0, 0, 0))

    # Instruction
    text_surface2 = font.render("Partie terminée!", True, white)
    text_rect2 = text_surface2.get_rect(center=(screenWidth / 2, screenHeight / 2 - 50))
    screen.blit(text_surface2, text_rect2)

    # Niveau + Pts
    text_surface = font.render("Niveau: " + str(level) + " - Points: " + str(pts), True, white)
    text_rect = text_surface.get_rect(center=(screenWidth / 2, screenHeight / 2))
    screen.blit(text_surface, text_rect)

    # Instruction
    text_surface2 = font.render("Appuie sur un bouton pour recommencer", True, white)
    text_rect2 = text_surface2.get_rect(center=(screenWidth / 2, screenHeight / 2 + 50))
    screen.blit(text_surface2, text_rect2)

    # Display
    pygame.display.flip()
    done = False
    joysticks_with_start_pressed = []

    # Set cooldown
    displayTime = pygame.time.get_ticks()
    displayCoolDown = 750

    # Listen to input
    while not done:
        events = pygame.event.get()
        exit = checkExit(joysticks_with_start_pressed, events)
        if exit:
            return True
        if pygame.time.get_ticks() - displayTime > displayCoolDown:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key != K_ESCAPE:
                    done = True
                if event.type == pygame.JOYBUTTONDOWN and event.button != 8 and event.button != 9:
                    done = True

        clock.tick(60)

def WriteHighScore(scoreLevel):
    highscores = []

    # Create file if does not exist
    try:
        with open("scores.txt", 'x') as f:
            highscores = []
    except: pass
        #highscores = []
        # file already created

    # Read scores
    with open("scores.txt", 'r') as f:
        try:
            for line in f:
                p = line.strip('()\n').split(',')
                highscores.append((int(p[0]), int(p[1])))
        except: pass

    # Add new highscore and sort
    highscores.append(scoreLevel)
    highscores = sorted(highscores, key=lambda tup: tup[0], reverse=True)
    highscores = highscores[0:5]

    # Write highscores
    with open("scores.txt", 'w') as f:
        for s in highscores:
            f.write(str(s) + '\n')

    if highscores.__contains__(scoreLevel):
        index = highscores.index(scoreLevel)
    else:
        index = -1

    return index, highscores

def CreateHeros(group):
    elsa = Hero("sprites/testElsa.png", 0)
    elsa.rect.x = 200
    elsa.rect.y = 300
    heros.add(elsa)

    anna = Hero("sprites/testAnna.png", 1)
    anna.rect.x = 250
    anna.rect.y = 350
    heros.add(anna)

# Sprite list creation and player sprite creation
heros = pygame.sprite.Group()
CreateHeros(heros)

opponents = pygame.sprite.Group()
currentLevel = startingLevel

lives = pygame.sprite.Group()
AddLives(lives, startingLives)

score = 0

playerSnowBalls = pygame.sprite.Group()
opponentSnowBalls = pygame.sprite.Group()

# Set the status of the main loop
isGameRunning = True
isGameOverShown = False
joysticks_with_start_pressed = []

while isGameRunning:

    # Change level
    if len(opponents) < 1:
        currentLevel += 1
        for snowball in playerSnowBalls:
            snowball.kill()
        for snowball in opponentSnowBalls:
            snowball.kill()
        isGameRunning = not showStartScreen(currentLevel, score)
        createOpponents(opponents, currentLevel, pygame.time.get_ticks())

    stop = False
    isGameOver = False

    # Look for events
    events = pygame.event.get()
    isGameOver = checkExit(joysticks_with_start_pressed, events)

    # Update heros based on pressed keys
    pressedKeys = pygame.key.get_pressed()
    for hero in heros:
        hero.update(pressedKeys, events)

    ### Draw background ###
    screen.fill((0,0,0))

    ### Debug constants ###
    if debug:
        displayDebug()
        displayButton(events)

    ### Draw Score ###
    displayScore()

    ### Draw snowballs ###
    playerSnowBalls.update()
    playerSnowBalls.draw(screen)
    opponentSnowBalls.update()
    opponentSnowBalls.draw(screen)

    ### Draw lives ###
    lives.draw(screen)
    if len(lives) < 1:
        isGameOver = True

    ### Draw enemies and mobs ###
    opponents.update()
    opponents.draw(screen)
    rev = False

    for opponent in opponents:
        score += opponent.checkCollisions()
        rev |= opponent.checkDirection()
        isGameOver |= opponent.checkGameOver()

    ### Direction change + advance ###
    if rev:
        for opponent in opponents:
            opponent.move_direction *= -1
            opponent.rect.x -= opponentXspeed

    if isGameOver:
        # Show game over screen
        stop = showGameOverScreen(currentLevel, score)

        # Reset level
        currentLevel = startingLevel

        # Reset players collisions
        for hero in heros:
            hero.kill()
        CreateHeros(heros)

        # Reset opponents
        for opponent in opponents:
            opponent.kill()
        currentLevel = 0
        createOpponents(opponents, currentLevel, pygame.time.get_ticks())

        # Remove snowballs
        for snowball in playerSnowBalls:
            snowball.kill()
        for snowball in opponentSnowBalls:
            snowball.kill()

        # Reset score
        score = 0

        # Reset lives
        for life in lives:
            life.kill()
        AddLives(lives, startingLives)

    if stop:
        isGameRunning = False
        break

    ### Draw characters ###
    for hero in heros:
        screen.blit(hero.image, hero.rect)

    ### Flip to screen and refresh rate ###
    pygame.display.flip()
    clock.tick(60)

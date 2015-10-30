import pygame
from pygame.locals import *

# Luke's defined classes
import player
from helper import *

class AbsorbBeam(pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE*2,TILE_SIZE*2)) # our sprite is 16x16
        self.image = self.image.convert()
        self.image.set_colorkey(COLOR_KEY, RLEACCEL)
        self.rect = self.image.get_rect()
        self.name = "absorbBeam"
        self.absorbTime = 0
        
        # Copy the BEAM from the ROM
        self.image.blit(owner.ROM, (0,0), Rect(6*(TILE_SIZE*2),0,TILE_SIZE*2,TILE_SIZE*2))
       
        # Flip the image
        if owner.facing == 0:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.owner = owner
        self.secondImage = self.image.copy() # used when we flicker        
        self.flicker = 0 # flicker the sprite to be old school
        self.lockedOn = 0 # are we locked on?
        self.lockTimer = 0 # timer!
        self.target = None # enemy we've locked onto
        
    def update(self, level, game):
        # do some business here... do we actually need to do anything?
        self.flicker = (self.flicker + 1)%2
        if self.flicker == 0:
            self.image.blit(self.secondImage,(0,0))
        if self.flicker == 1:
            self.image.fill(COLOR_KEY) # empty the image
        if self.lockedOn == 1:
            self.lockTimer = self.lockTimer + 1 # set our lock on timer
            if self.lockTimer > self.absorbTime: # 3 second timer
                self.owner.absorbEnemy(self.target, game)
    
    def setPos(self, x, y):
        self.rect.topleft = (x,y)
        
    def lockOn(self, enemy):
        self.lockedOn = 1 # we've locked on
        self.target = enemy
        self.absorbTime = self.target.absorbTime

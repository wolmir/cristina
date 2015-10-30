import pygame
from pygame.locals import *

# Luke's defined classes
import player, level

from helper import *

class FlameBall(pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE*2,TILE_SIZE*2)) # our sprite is 16x16
        self.image = self.image.convert()
        self.image.set_colorkey(COLOR_KEY, RLEACCEL)
        self.rect = self.image.get_rect()
        self.name = "flameBall"

        # Who's the owner of this slime ball?
        self.owner = owner

        # Match the owner's position
        self.rect.topleft = owner.rect.topleft
        
        self.image.blit(owner.ROM, (0,0), Rect(TILE_SIZE*12,TILE_SIZE*6,TILE_SIZE*2,TILE_SIZE*2))
        
        if owner.facing == 0: # threw it left
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.secondImage = self.image.copy()
        self.flicker = 0

    def update(self, level, game):
        self.rect.topleft = self.owner.rect.topleft

    def setSprite(self,num,auto_flip=1):
        # set which sprite to load? 0-6, something like that
        if num != self.spriteNum:
            self.spriteNum = num
            self.image.fill(COLOR_KEY) # blank the sprite
            self.image.blit(self.ROM, (0,0),
                Rect((num%2)*TILE_SIZE+TILE_SIZE*12,
                (num/2)*TILE_SIZE+TILE_SIZE*2,TILE_SIZE*2,TILE_SIZE*2))
            if self.vel[0] < 0.0: # flip it automagically
                self.flipSprite()
        
    def flipSprite(self):
        ''' Flip the sprite horizontally '''
        self.image = pygame.transform.flip(self.image, True, False)
        
    def setGround(self):
        # Bounce!!
        self.ground = 0
        self.vel = (self.vel[0], self.jumpY)
    
    def setFall(self):
        self.ground = 0
        self.vel = (0.0, 0.0) # iunno why it would get here
            

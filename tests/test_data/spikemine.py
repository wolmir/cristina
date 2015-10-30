import pygame
from pygame.locals import *

# Luke's defined classes
import player, level

from helper import *

class SpikeMine(pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE,TILE_SIZE)) # our sprite is 16x16
        self.image = self.image.convert()
        self.image.set_colorkey(COLOR_KEY, RLEACCEL)
        self.rect = self.image.get_rect()
        self.name = "spikeMine"

        # Who's the owner of this slime ball?
        self.owner = owner
        
        # set down right below the player
        self.rect.topleft = (owner.rect.topleft[0]+TILE_SIZE/4, owner.rect.topleft[1]+TILE_SIZE)
        
        # Physics
        self.ground = 1 # always start on the ground
        self.platform = None
        self.lifeSpan = 180 # 3 seconds per mine

        # Copy the SPRITE from the ROM
        self.spriteNum = -1
        self.ROM = owner.ROM
        self.setSprite(0)
        
        # we got triggered
        self.triggered = 0
        self.triggerTime = 0 # count-down for updating the mine

    def update(self, level, game):
        # physics updates, if we collide we want to kill this object
        if self.triggered == 0:
            self.lifeSpan = self.lifeSpan - 1
            if self.lifeSpan == 0: # we've expired
                self.owner.removeSpike(game)
                game.playerProjectiles.remove(self)
        elif self.triggered == 1:
            # update the sprite animation
            self.triggerTime = self.triggerTime + 1
            if self.triggerTime == 20: # at step 4, kill it
                game.playerProjectiles.remove(self)
            elif (self.triggerTime % 5) == 0: # trigger up our trap animation
                self.setSprite((self.spriteNum+1)%4)

    def setSprite(self,num):
        # set which sprite to load? 0-6, something like that
        if num != self.spriteNum:
            self.spriteNum = num
            self.image.fill(COLOR_KEY) # blank the sprite
            self.image.blit(self.ROM, (0,0),
                Rect((num%2)*TILE_SIZE+TILE_SIZE*12,
                (num/2)*TILE_SIZE+TILE_SIZE*4,TILE_SIZE,TILE_SIZE))

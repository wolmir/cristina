import pygame
from pygame.locals import *

# Luke's defined classes
import player, level

from helper import *

class SlimeBall(pygame.sprite.Sprite):
    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE,TILE_SIZE)) # our sprite is 16x16
        self.image = self.image.convert()
        self.image.set_colorkey(COLOR_KEY, RLEACCEL)
        self.rect = self.image.get_rect()
        self.name = "slimeBall"

        # Who's the owner of this slime ball?
        self.owner = owner
        
        # Physics
        self.ground = 0
        self.platform = None
        self.speed = 2.0 # make it kinda slow (not very good)
        self.jumpY = 2.7 # momentary velocity influence
        self.maxY = 2.0 # max falling speed
        self.gravity = 0.15625
        self.lifeSpan = 120 # 2 seconds per ball
        self.tick = 0
        
        if owner.facing == 0: # threw it left
            self.pos = (float(owner.rect.topleft[0]-TILE_SIZE),float(owner.rect.topleft[1]+TILE_SIZE/2))
            self.vel = (-self.speed, -self.gravity)
        else: # threw it right
            self.pos = (float(owner.rect.topleft[0]+TILE_SIZE*2),float(owner.rect.topleft[1]+TILE_SIZE/2))
            self.vel = (self.speed,-self.gravity)

        # Copy the SPRITE from the ROM
        self.spriteNum = -1
        self.ROM = owner.ROM
        self.setSprite(0)

    def update(self, level, game):
        # physics updates, if we collide we want to kill this object
        self.ground = 0 # don't ever ground this thing
        
        # apply gravity and slow it down
        self.vel = (self.vel[0], self.vel[1]-self.gravity)

        # max out the falling speed
        if self.vel[1] < -self.maxY:
            self.vel = (self.vel[0], -self.maxY)
        
        # kill it if it looped
        if self.pos[0] < -TILE_SIZE or self.pos[0] > MAP_WIDTH*TILE_SIZE - TILE_SIZE: # off the left side
            self.owner.removeSlime(game)
        
        # Check vertical
        old_y = self.pos[1]
        self.pos = (self.pos[0],self.pos[1]-self.vel[1])
        level.collision_vert(self)
        self.rect.topleft = (int(self.pos[0]),int(self.pos[1]))

        # Don't care about horizontal hit
        old_x = self.pos[0]
        self.pos = (self.pos[0]+self.vel[0],self.pos[1])
        pre_x = self.pos[0]
        level.collision_horiz(self)
        self.rect.topleft = (int(self.pos[0]),int(self.pos[1]))
        
        if pre_x != self.pos[0]:
            self.owner.removeSlime(game)
        
        self.lifeSpan = self.lifeSpan - 1
        if self.lifeSpan == 0: # we've expired
            self.owner.removeSlime(game)
        
        # update the sprite animation
        self.tick = (self.tick + 1) % 5
        if self.tick == 0:
            self.setSprite((self.spriteNum+1)%4)
        
        # slow our ball down each frame
        newVX = self.vel[0]*0.99
        self.vel = (newVX,self.vel[1])

    def setSprite(self,num,auto_flip=1):
        # set which sprite to load? 0-6, something like that
        if num != self.spriteNum:
            self.spriteNum = num
            self.image.fill(COLOR_KEY) # blank the sprite
            self.image.blit(self.ROM, (0,0),
                Rect((num%2)*TILE_SIZE+TILE_SIZE*12,
                (num/2)*TILE_SIZE+TILE_SIZE*2,TILE_SIZE,TILE_SIZE))
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
            

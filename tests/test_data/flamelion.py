import pygame
from pygame.locals import *

from helper import *

class FlameLion(pygame.sprite.Sprite):
    def __init__(self, ROM, x, y, startFacing):
        pygame.sprite.Sprite.__init__(self)
        self.ROM = ROM
        self.image = pygame.Surface((TILE_SIZE*2,TILE_SIZE*2)) # our sprite is 16x16
        self.image = self.image.convert()
        self.image.set_colorkey(COLOR_KEY, RLEACCEL)
        self.rect = self.image.get_rect()
        self.platform = None # don't use platforms for slimes... could use later
        self.name = "flameLion"
        self.pos = (float(x), float(y))
        self.origPos = self.pos
        self.vel = (0.0, 0.0)
        self.gravity = 0.15625
        self.moveX = 0.75 # not as fast as slimes
        self.maxY = 3.0
        self.angry = 0
        self.facing = startFacing # which way do we start moving?
        self.spriteAnim = 0 # for animating our sprite
        self.spriteNum = -1 # used for our sprite drawing
        self.autoFlip = -1
        self.setSprite(0)
        self.stunned = 0 # tell the stunned item we've been stunned
        self.aiState = 0 # what do slimes do? 0 = fall, 1 = move, 2 = waiting to unsplat, 3 = STUNNED!
        self.aiTick = 0 # used for AI changing
        self.ground = 1 # assume we start falling
        self.absorbTime = 160 # how long does it take to absorb this?
        self.selfWorth = 1000 # contemplate this
        self.fallNoise = load_sound("fall3.wav")
        self.bounceNoise = load_sound("bounce1.wav")
        self.dieNoise = load_sound('roar1.wav')
        self.life = 6 # 6 slime balls to die, 3 mines
        
    def update(self,level):
        if self.ground == 0: # falling!
            self.vel = (self.vel[0],self.vel[1] - self.gravity)
            if self.vel[1] > self.maxY: # prevent super drop
                self.vel = (self.vel[0], self.maxY)
        else:
            if self.aiState == 1:
                # moving around
                if self.facing == 0:
                    self.vel = (-self.moveX, self.vel[1])
                else:
                    self.vel = (self.moveX, self.vel[1])
                if self.spriteAnim < 20:
                    self.setSprite(0)
                else:
                    self.setSprite(1)
                self.spriteAnim = (self.spriteAnim + 1 ) % 40
            elif self.aiState == 2:
                # waiting to unhide
                self.aiTick = self.aiTick + 1
                if self.aiTick == 120:
                    self.aiTick = 0
                    self.aiState = 1 # move!
                    self.setSprite(0)
            elif self.aiState == 3:
                # getting sucked in
                self.setSprite(3) # some kinda shocked sprite
            
        # wrap around
        if self.pos[0] < -TILE_SIZE: # off the left side
            self.pos = (float(MAP_WIDTH*TILE_SIZE - TILE_SIZE),self.pos[1]) # move to the other side
        elif self.pos[0] > MAP_WIDTH*TILE_SIZE - TILE_SIZE: # off the right side
            self.pos = (float(-TILE_SIZE),self.pos[1]) # move to the other side

        self.pos = (self.pos[0],self.pos[1]-self.vel[1])
        level.collision_vert(self)
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))
        
        self.pos = (self.pos[0]+self.vel[0], self.pos[1])
        level.collision_horiz(self)
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))
        
        # debug AI
        if (self.pos[1] >= 192.0 and self.pos[0] >= 240.0) or (self.pos[1] >= 192.0 and self.pos[0] < 16.0):
            self.setAngry()
            self.setFall()
            self.pos = self.origPos # reset!
        
    def setSprite(self,num,auto_flip=1,force=0):
        # set which sprite to load? 0-6, something like that
        if force or num != self.spriteNum or (auto_flip==1 and self.facing != self.autoFlip):
            self.autoFlip = self.facing # we want to update a sprite if the facing has changed
            self.spriteNum = num
            self.image.fill(COLOR_KEY) # blank the sprite
            self.image.blit(self.ROM, (0,0), Rect(num*(TILE_SIZE*2)+self.angry*TILE_SIZE*8,TILE_SIZE*12,TILE_SIZE*2,TILE_SIZE*2))
            if auto_flip == 1 and self.facing == 0: # flip it automagically
                self.flipSprite()
        
    def flipSprite(self):
        ''' Flip the sprite horizontally '''
        self.image = pygame.transform.flip(self.image, True, False)
        
    def setGround(self):
        self.setSprite(0) # set to first frame
        self.aiState = 1 # move
        self.ground = 1
    
    def setFall(self):
        self.aiState = 0 # don't do anything while falling
        self.ground = 0
        self.setSprite(0,1,1)
        self.vel = (0.0, 0.0) # don't move!
        pygame.mixer.Channel(3).play(self.fallNoise)
        
    def setStun(self):
        if self.ground == 1: # dont stun an airborne slime..
            self.stunned = 1
            self.vel = (0.0, 0.0) # do not move, ur under arrest!
            self.aiState = 3 # we got stunned!
            self.aiTick = 0 # reset our AI ticker
            
    def releaseStun(self):
        if self.ground == 1: # unstun on the ground
            self.stunned = 0
            self.aiState = 1 # quickly wake-up if we're a blob
            self.aiTick = 0 # reset our AI ticker
            
    def setAngry(self):
        self.angry = 1
        self.moveX = 1.0 # FAST
            
    def takeDamage(self, game, projName):
        if projName == "slimeBall":
            self.life = self.life - 1
            # face the player
            if self.rect.topleft[0] < game.player_1.rect.topleft[0]:
                self.facing = 1
            else:
                self.facing = 0
        elif projName == "spikeMine":
            self.life = self.life - 2
        elif projName == "flameBall":
            self.life = 0
        if self.life == 0: # we died... :*(
            # death! add to the player's score
            game.enemySprites.remove(self)
            game.addToScore(self.selfWorth)
            pygame.mixer.Channel(3).play(self.dieNoise)

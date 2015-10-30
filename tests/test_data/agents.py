#
# a starting sprite type class
# *lazy loading
# *position, rotation
# * returns a rect that can be used for collision
# 
# a = Agent(art="path/to/image") to create
# a.pos = [150,50] to set position
# a.rot = [-1,0] to set direction vector
# image is drawn by the world, if image not yet loaded it is loaded
# multiple agents with the same image will only load the image once
#
# centered on agent.hotspot, default is [0,0] for upper left corner
# change to modify the hotspot, such as putting it in the center if you want to

import pygame
import math
import random

memory = {}
class Agent(object):
    def __init__(self,art=None,pos=None,rot=None):
        if not pos:
            pos = [0,0]
        if not rot:
            rot = [1,0]
        self.graphics = None
        self.surface = None
        self.pos = pos
        self.rot = rot
        self.art = art
        self.hotspot = [0,0]
        self.rotation_on_rot = False
        self.visible = True
        self.gfd = {}
        self.gft = {}
        self.init()
    def init(self):
        pass
    def load(self,art=None):
        if not art:
            art = self.art
        if not art in memory:
            memory[art] = pygame.image.load(art).convert(8)
            palette = memory[art].get_palette()
            for c in palette:
                c.g = int((c.r+c.b+c.g)/3.0)
                c.r = 0
                c.b = 0
            memory[art].set_palette(palette)
            memory[art].set_colorkey([255,0,255])
        self.graphics = memory[art]
        self.surface = self.graphics
        return self
    def update(self,world):
        if self.rotation_on_rot and self.surface:
            ang = math.atan2(-self.rot[1],self.rot[0])*180.0/math.pi
            self.surface = pygame.transform.rotate(self.graphics,ang)
        if self.graphics:
            palette = self.graphics.get_palette()
            for i,c in enumerate(palette):
                if i not in self.gft:
                    self.gfd[i] = 1
                    self.gft[i] = 62
                if self.gft[i]:
                    if self.gfd[i]==1:
                        if c.g<220-2:
                            c.g=c.g+1
                        else:
                            self.gft[i] = 1
                    if self.gfd[i]==-1:
                        if c.g>80+2:
                            c.g=c.g-1
                        else:
                            self.gft[i] = 1
                    self.gft[i]-=1
                else:
                    self.gfd[i] = -self.gfd[i]
                    self.gft[i] = 62
            self.graphics.set_palette(palette)
    def draw(self,engine):
        if not self.surface and self.art:
            self.load()
        engine.surface.blit(self.surface,[self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1]])
    def rect(self):
        if not self.surface:
            return pygame.Rect([[0,0],[0,0]])
        r = self.surface.get_rect()
        r = r.move(self.pos[0]-self.hotspot[0],self.pos[1]-self.hotspot[1])
        return r
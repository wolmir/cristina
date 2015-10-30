import pygame
from pygame.locals import *

import functions

class Explosion(pygame.sprite.Sprite):

    def __init__(self, pos, screen, type):

        pygame.sprite.Sprite.__init__(self)
        ###TYPE OF EXPLOSION
        t = {
            1 : ("ex001.png", (7, 5), 128),
            2 : ("ex002.png", (14, 0), 64)
            }

        self.image = functions.load_image(t[type][0], "alpha")
        self.screen = screen

        self.wh = t[type][2]
        self.maxXY = t[type][1]
        self.rect = pygame.Rect(0, 0, self.wh, self.wh)
        self.rect.center = pos
        self.x = 0
        self.y = 0

    def update(self):

        ###DRAW
        self.screen.blit(self.image, self.rect, (self.wh * self.x, self.wh * self.y, \
                         self.wh, self.wh))

        ###UPDATE ANIM
        self.x += 1
        if self.x > self.maxXY[0]:
            if self.y < self.maxXY[1]:
                self.x = 0
                self.y += 1
            else:
                self.kill()

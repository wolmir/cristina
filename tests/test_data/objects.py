import pygame
from pygame.locals import *

import functions
import globals

class Pills(pygame.sprite.Sprite):

    def __init__(self, pos, _screen, type):

        pygame.sprite.Sprite.__init__(self)
        self.image = functions.load_image("pills.png")
        self.rect = pygame.Rect(0, 0, 11, 23)
        self.rect.topleft = pos[0], pos[1] + 8
        self.screen = _screen
        self.anim_delay = 5
        self.frame = 0
        self.type = (type * -1) - 1

    def update(self):

        self.screen.blit(self.image, self.rect, (11 * self.frame, 23 * self.type, 11, 23))

        ###UPDATE ANIM
        self.anim_delay -= 1
        if not self.anim_delay:
            self.frame += 1
            if self.frame > 6:
                self.frame = 0
            self.anim_delay = 5

class Portal(pygame.sprite.Sprite):

    def __init__(self, pos, _screen, side):

        pygame.sprite.Sprite.__init__(self)
        self.image = functions.load_image("portal.png", "colorkey")
        self.rect = pygame.Rect(pos[0], pos[1] - 20, 32, 50)
        self.screen = _screen
        self.anim_delay = 5
        self.frame = 0
        self.side = side

    def update(self):

        self.screen.blit(self.image, self.rect, (32 * self.frame, 0, 32, 50))

        self.anim_delay -= 1
        if not self.anim_delay:
            self.frame += 1
            if self.frame > 3:
                self.frame = 0
            self.anim_delay = 5

    def teleport(self, obj):

        for sprite in globals.OBJECTS:
            if isinstance(sprite, Portal):
                if sprite != self:
                    obj.rect.center = (sprite.rect.center[0] + (32 * sprite.side), \
                                       sprite.rect.center[1] - 20)
                    break










import pygame

import rstore
from const import *

# cell types
C_PLAYER = 'player'
C_GUN = 'gun'
C_GOAL = 'goal'
C_MOVE = 'move'
C_OBSTACLE = 'obstacle'

# directions for the gun
D_UP = 'up'
D_LEFT = 'left'
D_RIGHT = 'right'
D_DOWN = 'down'


class BulletSprite(object):
    _SPEED = 500
    def __init__(self, pos, direction):
        self.image = pygame.Surface((CSIZE - 2 * OUTLINE, CSIZE - 2 * OUTLINE))
        self.image.fill(BULLETCOL)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.direction = direction
    def update(self, dt):
        if self.direction == D_RIGHT:
            self.rect.x += self._SPEED * dt
        elif self.direction == D_LEFT:
            self.rect.x -= self._SPEED * dt
        elif self.direction == D_UP:
            self.rect.y -= self._SPEED * dt
        elif self.direction == D_DOWN:
            self.rect.y += self._SPEED * dt


class CellSprite(object):
    """Base class, a sprite that is confined to a cell"""
    def __init__(self, pos):
        # pos is cell index
        self.pos = pos
        self.image = pygame.Surface((CSIZE - 2 * OUTLINE, CSIZE - 2 * OUTLINE))

        self.rect = self.image.get_rect()
        self.rect.topleft = (self.pos[0] * CSIZE + OUTLINE, 
                             self.pos[1] * CSIZE + OUTLINE)
        # can we move onto the sprite?
        self.canmove = True

    def update(self, dt):
        pass


class GunCellSprite(CellSprite):
    def __init__(self, pos, **kwargs):
        super(GunCellSprite, self).__init__(pos)
        self.ctype = C_GUN
        self.direction = kwargs['direction']
        self.image = rstore.images['arrow' + self.direction]
        self.canmove = False


class GoalCellSprite(CellSprite):
    def __init__(self, pos, **kwargs):
        super(GoalCellSprite, self).__init__(pos)
        self.ctype = C_GOAL
        self.done = False
        self.nbits = kwargs['nbits']
        self.set_image()

    def set_image(self):
        self.image.fill(GCOL)
        txt = rstore.fonts['main'].render(str(self.nbits), True, BLACK)
        if (self.nbits > 1):
            self.image.blit(txt, (0, 0))
    
    def decrement(self):
        self.nbits -= 1
        self.set_image()

class ObstacleCellSprite(CellSprite):
    def __init__(self, pos):
        super(ObstacleCellSprite, self).__init__(pos)
        self.ctype = C_OBSTACLE
        self.image.fill(OCOL)
        self.canmove = False


class PlayerCellSprite(CellSprite):
    # we only flash to help the tutorial
    _FLASHTIME = 0.8
    def __init__(self, pos, **kwargs):
        super(PlayerCellSprite, self).__init__(pos)
        self.ctype = C_PLAYER
        self.health = kwargs['health']
        self.canmove = False
        # can be selected (clicked on)
        self.selected = False
        # the scene sets me to flash
        self.set_flash(False)
        # image for when cell selected and when cell not selected
        self.set_image()

    def set_flash(self, fl):
        self.tstate = 0
        self.on = True
        self.flashing = fl 
    
    def set_image(self):
        # draw the health value to the middle of the 
        txt = rstore.fonts['main'].render(str(self.health), True, WHITE)
        # need different colors here for the different numbers!

        if self.selected:
            self.image.fill(SELCOL)
            pygame.draw.rect(self.image, pygame.Color(PCOL[self.health]), 
                             (OUTLINE, OUTLINE, CSIZE - 4 * OUTLINE, CSIZE - 4 * OUTLINE))
            self.image.set_alpha(128)
        else:
            self.image.fill(pygame.Color(PCOL[self.health]))
            if self.on:
                self.image.set_alpha(255)
            else: # for tutorial
                self.image.set_alpha(0)

        self.image.blit(txt, (0, 0))
    
    def update(self, dt):
        if self.flashing:
            self.tstate += dt
            if (self.tstate > self._FLASHTIME):
                self.tstate = 0
                self.on = not self.on
        self.set_image()


class PlayerMoveCellSprite(CellSprite):
    _FLASHTIME = 0.8
    def __init__(self, pos, **kwargs):
        super(PlayerMoveCellSprite, self).__init__(pos)
        self.ctype = C_MOVE
        self.flashing = kwargs['flash']
        # time in the current state (only relevant if flashing).
        self.tstate = 0
        self.on = True
        self.set_image()

    def set_flash(self, fl):
        if self.flashing == fl:
            return
        self.tstate = 0
        self.on = True
        self.flashing = fl 

    def set_image(self):
        if self.on:
            self.image.fill(MOVCOL)
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)

    def update(self, dt):
        if not self.flashing:
            return
        self.tstate += dt
        if (self.tstate > self._FLASHTIME):
            self.tstate = 0
            self.on = not self.on
            self.set_image()


# mapping of cell type to class object
CMAP = {C_PLAYER: PlayerCellSprite,
        C_GUN: GunCellSprite,
        C_GOAL: GoalCellSprite,
        C_MOVE: PlayerMoveCellSprite,
        C_OBSTACLE: ObstacleCellSprite}


# mapping of input symbol in text file to cell type and any other
# parameters needed in constructor.
IMAP = {'E': (C_GOAL, {}),
        'O': (C_OBSTACLE, {}),
        # wasd are guns shooting in the expected directions
        'W': (C_GUN, {'direction': D_UP}),
        'A': (C_GUN, {'direction': D_LEFT}),
        'S': (C_GUN, {'direction': D_DOWN}),
        'D': (C_GUN, {'direction': D_RIGHT}),
        '1': (C_PLAYER, {'health': 1}),
        '2': (C_PLAYER, {'health': 2}),
        '3': (C_PLAYER, {'health': 3}),
        '4': (C_PLAYER, {'health': 4}),
        '5': (C_PLAYER, {'health': 5}),
        '6': (C_PLAYER, {'health': 6})}

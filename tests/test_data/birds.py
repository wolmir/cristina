#! /usr/bin/env python

#    Copyright (C) 2014  Benoit <benoxoft> Paquet
#
#    This file is part of Bomberbirds.
#
#    Bomberbirds is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import pygame
from pygame.sprite import Sprite

import bomb
import media
import movement

import gamelib as gl

class Bird(Sprite):
    
    def __init__(self,
                 bird,
                 birdflyup,
                 birdflydown,
                 minibird,
                 initx,
                 inity, 
                 init_dir,
                 game):
        Sprite.__init__(self)
        
        self.imgflip = init_dir == -1
        self.init_dir = init_dir
        
        self.wing = 0 
        self.has_bomb = False
        self.dead = False
        self.counter_resurrect = 0
        self.counter_invincible = 0
        self.invisible = False
        self.brain = None
        self.bomb = None

        self.bird = bird
        self.birdflyup = birdflyup
        self.birdflydown = birdflydown
        self.minibird = minibird
        self.deadbird = media.deadbird
        self.initx = initx
        self.inity = inity
        self.dir = init_dir

        self.move = movement.Movement(self, 
                             thrust_strength = 1000 * gl.RESIZE_FACTOR,
                             accelx = 700 * gl.RESIZE_FACTOR,
                             accely = 200 * gl.RESIZE_FACTOR,
                             maxspeedx = 120 * gl.RESIZE_FACTOR,
                             maxspeedy = 160 * gl.RESIZE_FACTOR,
                             gravity = 400 * gl.RESIZE_FACTOR,
                             posx=self.initx,
                             posy=self.inity)

        self.add_bomb = game.add_bomb_event
        
        self.firstupdate = False
        self.image = self.bird
        self.rect = self.image.get_rect()
        self.rect.width /= 2
        self.rect.height -= 4
        self.lives = 3
        
    def set_init_pos(self):
        self.move.posx = self.initx
        self.move.posy = self.inity
        self.move.speedx = 0
        self.move.speedy = 0
        self.dir = self.init_dir
        self.flip()
        
    def nuke(self):
        if self.dead:
            return
        
        if not self.has_bomb:
            self.create_bomb()
            self.has_bomb = True
        else:
            self.throw_bomb()
    
    def create_bomb(self):
        self.bomb = bomb.Bomb(self)
        self.add_bomb(self.bomb)
        
    def throw_bomb(self):
        self.has_bomb = False
        self.bomb.launch(self.move.speedx, self.move.speedy)
    
    def flip(self):
        if not self.imgflip and self.dir == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.imgflip = True
        elif self.imgflip and self.dir == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.imgflip = False
        
    def moveleft(self, tick):
        if self.dead:
            return
        
        self.dir = -1
        self.flip()

        self.move.moveleft(tick)
        
    def moveright(self, tick):
        if self.dead:
            return
        
        self.dir = 1
        self.flip()
        #if self.move.speedy == 0:
        self.move.moveright(tick)
        
    def thrust(self, tick):
        if self.dead:
            return
        
        self.wing += 1
        if self.wing == 3:
            self.image = self.birdflydown
            self.flyup = False
            self.imgflip = False
            self.flip()
        elif self.wing == 6:
            self.image = self.birdflyup
            self.flyup = True
            self.imgflip = False
            self.flip()
        elif self.wing > 6:
            self.wing = 0
            
        self.firstupdate = True
        self.move.thrust(tick)
        
    def kill(self):
        if self.dead:
            return 
        if self.counter_invincible > 0:
            return 
        
        self.dead = True
        self.has_bomb = False
        self.lives -= 1
        media.kill.play()
        self.counter_resurrect = 3000

    def update(self, tick):
        if self.counter_invincible > 0:
            self.counter_invincible -= tick
            
        if self.dead and self.lives > 0:
            self.counter_resurrect -= tick
            if self.counter_resurrect < 0:
                if self.lives > 0:
                    self.dead = False
                    self.set_init_pos()
                    self.counter_invincible = 1000
                    
        if self.brain is not None:
            self.brain.update(tick)

        if not self.firstupdate:
            if self.dead:
                self.image = self.deadbird
            else:
                self.image = self.bird
            self.imgflip = False
            self.flip()
        self.firstupdate = False
        
        self.move.calculate_movement(tick)

        self.rect.x = self.move.posx
        self.rect.y = self.move.posy

class GreenBird(Bird):
    def __init__(self, game):
        Bird.__init__(self,
                      media.bird1,
                      media.birdflyup1,
                      media.birdflydown1,
                      media.minibird1,
                      32 * gl.RESIZE_FACTOR,
                      32 * gl.RESIZE_FACTOR,
                      1,
                      game)

class RedBird(Bird):
    def __init__(self, game):
        Bird.__init__(self,
                      media.bird2,
                      media.birdflyup2,
                      media.birdflydown2,
                      media.minibird2,
                      192 * gl.RESIZE_FACTOR,
                      32 * gl.RESIZE_FACTOR,
                      -1, 
                      game)

class PurpleBird(Bird):
    def __init__(self, game):
        Bird.__init__(self,
                      media.bird3,
                      media.birdflyup3,
                      media.birdflydown3,
                      media.minibird3,
                      32 * gl.RESIZE_FACTOR,
                      192 * gl.RESIZE_FACTOR,
                      1,
                      game)

class CyanBird(Bird):
    def __init__(self, game):
        Bird.__init__(self,
                      media.bird4,
                      media.birdflyup4,
                      media.birdflydown4,
                      media.minibird4,
                      192 * gl.RESIZE_FACTOR,
                      192 * gl.RESIZE_FACTOR,
                      -1, 
                      game)

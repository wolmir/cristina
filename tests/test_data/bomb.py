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

import media
import movement

import gamelib as gl

class Bomb(Sprite):
    
    def __init__(self, bird):
        Sprite.__init__(self)
        media.createbomb.play()
        self.bird = bird
        self.bomb = media.bomb.convert()
        self.bomb2 = media.bomb2.convert()
        self.boom = media.boom.convert()        
        self.rect = pygame.rect.Rect(self.bird.rect.x, bird.rect.y + 16 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR)
        self.image = self.bomb
        self.move = movement.Movement(self,
                             accelx = 1000 * gl.RESIZE_FACTOR,
                             accely = 1000 * gl.RESIZE_FACTOR,
                             maxspeedx = 200 * gl.RESIZE_FACTOR,
                             maxspeedy = 200 * gl.RESIZE_FACTOR,
                             gravity = 1000 * gl.RESIZE_FACTOR,
                             decrease_speed_ratio = 2                        
                             )
        self.move.add(self.bird.move.sprites())
        self.timeout = 3400
        self.explode_event = None
        self.delete_bomb = None
        self.exploded = False
        self.bombstate = 4
        self.attached = True
        
    def launch(self, speedx, speedy):
        self.attached = False
        media.throw.play()
        self.move.speedx = speedx * 2.2
        if self.move.speedy <= 0:
            self.move.speedy = speedy * 2
        else:
            self.move.speedy = speedy * 2.5
        self.move.posx = self.rect.x
        self.move.posy = self.rect.y
        
    def explode(self):
        self.timeout = 400
        self.exploded = True
        self.explode_event(self)
        media.explode.play()
        self.attached = False
        self.rect.height = 64 * gl.RESIZE_FACTOR
        self.rect.width = 64 * gl.RESIZE_FACTOR
        self.rect.x -= 16 * gl.RESIZE_FACTOR
        self.rect.y -= 16 * gl.RESIZE_FACTOR
        self.image = self.boom
        
    def update(self, tick):
            
        self.timeout -= tick
        if 400 < self.timeout < 800:
            if self.bombstate == 4:
                self.image = self.bomb2
            elif self.bombstate == 2:
                self.image = self.bomb
            self.bombstate -= 1
            if self.bombstate == 0:
                self.bombstate = 4
                
        if self.timeout < 400 and not self.exploded:
            self.explode()
        if self.timeout < 0:
            self.delete_bomb(self)
            
        if self.attached:
            self.rect.x = self.bird.rect.x
            self.rect.y = self.bird.rect.y + 16 * gl.RESIZE_FACTOR
        elif not self.exploded:
            self.move.calculate_movement(tick)
    
            self.rect.x = self.move.posx
            self.rect.y = self.move.posy

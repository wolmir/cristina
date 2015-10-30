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

from pygame.sprite import Group
from pygame.rect import Rect

import math

import gamelib as gl

class Movement(Group):
    def  __init__(self, moving_sprite,
                  speedx = 0,
                  maxspeedx = -1,
                  speedy = 0,
                  maxspeedy = -1,
                  posx = 0,
                  posy = 0,
                  thrust_strength = 0,
                  accelx = 0,
                  accely = 0,
                  gravity = 1000,
                  decrease_speed_ratio = 2.0):
        Group.__init__(self)
        self.moving_sprite = moving_sprite
        self.speedx = speedx
        self.speedy = speedy
        self.maxspeedx = maxspeedx
        self.maxspeedy = maxspeedy
        self.posx = posx
        self.posy = posy
        self.thrust_strength = thrust_strength
        self.accelx = accelx
        self.accely = accely
        self.gravity = gravity
        self.decrease_speed_ratio = decrease_speed_ratio
        self.bumping_walls = []
        
    def get_speed(self):
        return math.sqrt(self.speedx**2 + self.speedy**2)
    
    def thrust(self, tick):
        self.speedy -= self.thrust_strength * tick / 1000.0
        if self.maxspeedy != -1 and abs(self.speedy) > self.maxspeedy:
            self.speedy = -self.maxspeedy
        
    def moveleft(self, tick):
        self.speedx -= self.accelx * tick / 1000.0
        if self.maxspeedx != -1 and abs(self.speedx) > self.maxspeedx:
            self.speedx = -self.maxspeedx
        
    def moveright(self, tick):
        self.speedx += self.accelx * tick / 1000.0
        if self.maxspeedx != -1 and self.speedx > self.maxspeedx:
            self.speedx = self.maxspeedx

    def movedown(self, tick):
        self.speedy += self.accely * tick / 1000.0
        if self.maxspeedy != -1 and abs(self.speedy) > self.maxspeedy:
            self.speedy = self.maxspeedy
    
    def calculate_movement(self, tick):
        self.speedy += self.gravity * tick / 1000.0
        if self.maxspeedy != -1 and self.speedy > self.maxspeedy:
            self.speedy = self.maxspeedy
        self.check_collision(tick)
        self.posy = self.get_new_posy(tick)
        self.posx = self.get_new_posx(tick)

        if self.posx < -16 * gl.RESIZE_FACTOR:
            self.posx = 272 * gl.RESIZE_FACTOR
        if self.posx > 272 * gl.RESIZE_FACTOR:
            self.posx = -16 * gl.RESIZE_FACTOR
        if self.posy < -16 * gl.RESIZE_FACTOR:
            self.posy = 256 * gl.RESIZE_FACTOR
        if self.posy > 256 * gl.RESIZE_FACTOR:
            self.posy = -16 * gl.RESIZE_FACTOR
            
    def get_new_posx(self, tick):
        return self.posx + self.speedx * tick / 1000.0

    def get_new_posy(self, tick):
        return self.posy + self.speedy * tick / 1000.0

    def check_collision(self, tick):
        oldrect = self.moving_sprite.rect
        newrect = Rect(self.get_new_posx(tick), self.get_new_posy(tick), oldrect.width, oldrect.height)
        collisions = [col for col in self.sprites() if col.rect.colliderect(newrect)]
        if len(collisions) > 0:
            for coll in collisions:
                col = coll.rect
                if newrect.right >= col.x and oldrect.right <= col.x:
                    self.posx = col.x - oldrect.width
                    self.speedx = -self.speedx / 2
                    if -30 * gl.RESIZE_FACTOR < self.speedx < 30 * gl.RESIZE_FACTOR:
                        self.speedx = 0 
                if newrect.x <= col.right and oldrect.x >= col.right:
                    self.posx = col.right
                    self.speedx = -self.speedx / 2
                    if -30 * gl.RESIZE_FACTOR < self.speedx < 30 * gl.RESIZE_FACTOR:
                        self.speedx = 0 
                if newrect.bottom >= col.y and oldrect.bottom <= col.y:
                    self.posy = col.y - oldrect.height
                    self.speedy = -self.speedy / 2
                    if -30 * gl.RESIZE_FACTOR < self.speedy < 30 * gl.RESIZE_FACTOR:
                        self.speedy = 0 
                    self.speedx /= self.decrease_speed_ratio
                    if self.speedx < 1 and self.speedx > -1:
                        self.speedx = 0
                if newrect.y <= col.bottom and oldrect.y >= col.bottom:
                    self.posy = col.bottom
                    self.speedy = -self.speedy / 2
                    if -30 * gl.RESIZE_FACTOR < self.speedy < 30 * gl.RESIZE_FACTOR:
                        self.speedy = 0 
                    self.speedx /= self.decrease_speed_ratio
                    if self.speedx < 1 and self.speedx > -1:
                        self.speedx = 0

        self.bumping_walls = collisions
        

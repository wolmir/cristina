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

import random

class BirdBrain:
    
    def __init__(self, owner, birds):
        self.owner = owner
        self.birds = birds
        self.next_action = 0
        self.decision = 0
        self.direction = 0
        self.nuke = 0
        self.thrust = 0
        self.launch = False
        self.nuke_time = 0
        
    def update(self, tick):
        self.next_action -= tick
        if self.next_action < 0:
            self.next_action = random.randint(500, 3000)
            self.direction = random.randint(0, 1)
            self.thrust = random.randint(0, 4)
        self.nuke = random.randint(0, 50)
        if self.direction == 0:
            self.owner.moveleft(tick)
        elif self.direction == 1:
            self.owner.moveright(tick)
            
        if self.thrust != 0:
            self.owner.thrust(tick)
        
        if self.nuke == 0 and not self.launch:
            self.owner.nuke()
            self.nuke_time = random.randint(200, 1600)
            self.launch = True
            self.nuke = 1
        if self.launch and self.nuke_time < 0:
            self.owner.nuke()
            self.launch = False
        elif self.launch and self.nuke_time >= 0:
            self.nuke_time -= tick
            





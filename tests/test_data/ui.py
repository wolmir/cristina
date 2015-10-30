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

import pygame
from pygame.sprite import Sprite, Group 
import random

from bomb import Bomb
import media

import gamelib as gl

class UI:
    
    def __init__(self):
        self.tiles = Group()
        self.bg = []
        self.tntcrate = TNTCrate()
        
        self.tiles.add(Grass(96 * gl.RESIZE_FACTOR, 176 * gl.RESIZE_FACTOR, 64 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR))
        
        self.tiles.add(Grass(32 * gl.RESIZE_FACTOR, 64 * gl.RESIZE_FACTOR, 32 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR))
        self.tiles.add(Grass(192 * gl.RESIZE_FACTOR, 64 * gl.RESIZE_FACTOR, 32 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR))

        self.tiles.add(Grass(32 * gl.RESIZE_FACTOR, 224 * gl.RESIZE_FACTOR, 32 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR))
        self.tiles.add(Grass(192 * gl.RESIZE_FACTOR, 224 * gl.RESIZE_FACTOR, 32 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR))

        for i in xrange(0, 50):
            self.bg.append(Star())

        self.bg.append(self.tntcrate)
        
    def update(self, tick):
        pass
    
class MenuManager:

    def __init__(self, screen):
        self.screen = screen
        self.current_screen = 0
        self.cursor_pos = 0
        self.game_over = 0
        self.birds = 0
        
    def next_screen(self):
        if self.current_screen == 2:
            return False
        self.current_screen += 1
        return True
    
    def cursor_up(self):
        self.cursor_pos -= 1
        if self.cursor_pos == -1:
            self.cursor_pos = 2
    
    def cursor_down(self):
        self.cursor_pos += 1
        if self.cursor_pos == 3:
            self.cursor_pos = 0
    
    def reset(self):
        self.current_screen = 0
        self.cursor_pos = 0
        self.game_over = 0
        
    def show_game_title(self):
        font = media.get_font(8 * gl.RESIZE_FACTOR)
        s = font.render("BOMBERBIRDS", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 20 * gl.RESIZE_FACTOR))
        s = font.render("entry for pyweek #18", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 30 * gl.RESIZE_FACTOR))
        s = font.render("by Benoit <benoxoft> Paquet", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 40 * gl.RESIZE_FACTOR))

        s = font.render("music from opengameart.org", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 194 * gl.RESIZE_FACTOR))
        s = font.render("title song by bart", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 204 * gl.RESIZE_FACTOR))
        s = font.render("game song by FoxSynergy", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 214 * gl.RESIZE_FACTOR))
                
    def show_demo_message(self):
        self.show_game_title()
        font = media.get_font(8 * gl.RESIZE_FACTOR)
        s = font.render("press <space> to start", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 90 * gl.RESIZE_FACTOR))
        s = font.render("press <ESC> to quit anytime", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 100 * gl.RESIZE_FACTOR))
        s = font.render("1,2,3 change screen resolution", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 110 * gl.RESIZE_FACTOR))
        
    def show_menu(self):
        self.show_game_title()
        font = media.get_font(8 * gl.RESIZE_FACTOR)
        s = font.render("Select how many birds", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 90 * gl.RESIZE_FACTOR))
        if self.cursor_pos == 0:
            s = font.render("-> 2 birds", True, (255,255,255))
        else:
            s = font.render("   2 birds", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 100 * gl.RESIZE_FACTOR))
        
        if self.cursor_pos == 1:
            s = font.render("-> 3 birds", True, (255,255,255))
        else:
            s = font.render("   3 birds", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 110 * gl.RESIZE_FACTOR))
        if self.cursor_pos == 2:
            s = font.render("-> 4 birds", True, (255,255,255))
        else:
            s = font.render("   4 birds", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 120 * gl.RESIZE_FACTOR))
    
    def show_help(self):
        self.show_game_title()
        font = media.get_font(8 * gl.RESIZE_FACTOR)
        s = font.render("You are the green bird", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 90 * gl.RESIZE_FACTOR))
        s = font.render("Use a, d and w to move", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 100 * gl.RESIZE_FACTOR))
        s = font.render("<space> create a bomb", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 110 * gl.RESIZE_FACTOR))
        s = font.render("press it again to throw it", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 120 * gl.RESIZE_FACTOR))
        s = font.render("press <space> to continue", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 130 * gl.RESIZE_FACTOR))
    
    def show_game_over(self):
        font = media.get_font(8 * gl.RESIZE_FACTOR)
        
        if self.game_over == 1:
            s = font.render("GAME OVER!", True, (255,255,255))
        elif self.game_over == 2:
            s = font.render("YOU WON!", True, (255,255,255))
        elif self.game_over == 3:
            s = font.render("EVERYBIRD IS DEAD!", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 90 * gl.RESIZE_FACTOR))
        
        if self.cursor_pos == 0:
            s = font.render("-> play again       ", True, (255,255,255))
        else:
            s = font.render("   play again       ", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 100 * gl.RESIZE_FACTOR))
        
        if self.cursor_pos == 1:
            s = font.render("-> back to main menu", True, (255,255,255))
        else:
            s = font.render("   back to main menu", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 110 * gl.RESIZE_FACTOR))
        if self.cursor_pos == 2:
            s = font.render("-> quit             ", True, (255,255,255))
        else:
            s = font.render("   quit             ", True, (255,255,255))
        self.screen.blit(s, ((256 * gl.RESIZE_FACTOR - s.get_width()) / 2, 120 * gl.RESIZE_FACTOR))
        
    def update(self, tick):
        if self.game_over == 0:
            if self.current_screen == 0:
                self.show_demo_message()
            elif self.current_screen == 1:
                self.show_help()
            elif self.current_screen == 2:
                self.show_menu()
        else:
            self.show_game_over()
            
class Minibird(Sprite):
    def __init__(self, image, x):
        Sprite.__init__(self)
        self.rect = pygame.rect.Rect(x, 4 * gl.RESIZE_FACTOR, 8 * gl.RESIZE_FACTOR, 8 * gl.RESIZE_FACTOR)
        self.image = image.convert()
        
class LifeCounter:
    def __init__(self, birds, screen):
        self.birds = birds
        self.screen = screen
        
    def update(self, tick):
        x = 24 * gl.RESIZE_FACTOR
        for b in self.birds:
            for i in xrange(0, 3):
                if i < b.lives:
                    mb = Minibird(b.minibird, x)
                    self.screen.blit(mb.image, pygame.rect.Rect(mb.rect.x, mb.rect.y, mb.rect.w, mb.rect.h))
                else:
                    mb = Minibird(media.minibirddead, x)
                    self.screen.blit(mb.image, pygame.rect.Rect(mb.rect.x, mb.rect.y, mb.rect.w, mb.rect.h))
                x += 10 * gl.RESIZE_FACTOR
            x += 30 * gl.RESIZE_FACTOR
            
    def bird_kill(self, bird):
        pass
    
class TNTCrate(Sprite):
    def __init__(self):
        Sprite.__init__(self)
        self.rect = pygame.rect.Rect(96 * gl.RESIZE_FACTOR, 112 * gl.RESIZE_FACTOR, 64 * gl.RESIZE_FACTOR, 64 * gl.RESIZE_FACTOR)
        self.image = media.tntcrate.convert()
        
    def explode(self, bird):
        for i in xrange(0, random.randint(5, 10)):
            b = Bomb(bird)
            bird.add_bomb(b)
            b.timeout = 1600
            b.rect.x = self.rect.x
            b.rect.y = self.rect.y - 32 * gl.RESIZE_FACTOR
            b.launch(random.randint(-200 * gl.RESIZE_FACTOR, 200 * gl.RESIZE_FACTOR), -random.randint(50 * gl.RESIZE_FACTOR, 300 * gl.RESIZE_FACTOR))
        self.rect = pygame.rect.Rect(10000, 10000, 0, 0)
            
    def update(self, tick):
        pass
    
class Tile(Sprite):
    
    def __init__(self, image, x, y, h, w):
        Sprite.__init__(self)
        tile = image.convert()
        rtile = tile.get_rect()
        self.rect = pygame.rect.Rect(x, y, h, w)
        self.image = pygame.surface.Surface((self.rect.width, self.rect.height))
                        
        columns = int(self.rect.width / rtile.width) + 1
        rows = int(self.rect.height / rtile.height) + 1
        
        for y in xrange(rows):
            for x in xrange(columns):
                if x == 0 and y > 0:
                    rtile = rtile.move([-(columns -1 ) * rtile.width, rtile.height])
                if x > 0:
                    rtile = rtile.move([rtile.width, 0])
                self.image.blit(tile, rtile)

class Grass(Tile):    
    def __init__(self, x, y, h, w):
        Tile.__init__(self, media.grass3, x, y, h, w)
    
class Dirt(Tile):
    def __init__(self, x, y, h, w):
        Tile.__init__(self, media.dirt, x, y, h, w)
        
class Water(Tile):
    def __init__(self, x, y, h, w):
        Tile.__init__(self, media.water, x, y, h, w)
         
class Star(Sprite):
    
    def __init__(self):
        Sprite.__init__(self)
        self.rect = pygame.rect.Rect(random.randint(16 * gl.RESIZE_FACTOR, 240 * gl.RESIZE_FACTOR), random.randint(16 * gl.RESIZE_FACTOR, 224 * gl.RESIZE_FACTOR), 16 * gl.RESIZE_FACTOR, 16 * gl.RESIZE_FACTOR)
        self.star0 = media.star0.convert()
        self.star1 = media.star1.convert()
        self.star2 = media.star2.convert()
        self.star3 = media.star3.convert()
        self.current_star = random.randint(0, 10)
        self.image = self.star0.convert()

        self.next_update = 0
        
    def update(self, tick):
        self.next_update -= tick
        
        if self.next_update < 0:
            self.next_update = random.randint(500, 2000)
            if self.current_star == 0:
                self.image = self.star1
            elif self.current_star == 1:
                self.image = self.star2
            elif self.current_star == 2:
                self.image = self.star3
            elif self.current_star == 3:
                self.image = self.star2
            elif self.current_star == 4:
                self.image = self.star1
            elif self.current_star < 10:
                self.image = self.star0
            else:
                self.current_star = -1
            self.current_star += 1
                
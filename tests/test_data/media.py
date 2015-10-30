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
import os
import sys

import gamelib as gl

m = sys.modules[__name__]

def load_image(img):
    image = pygame.image.load(img)
    return pygame.transform.scale(image, (image.get_width() * gl.RESIZE_FACTOR, image.get_height() * gl.RESIZE_FACTOR))
    #return pygame.transform.scale2x(pygame.image.load(img))

def load_all_images():
    for f in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'media', 'images')):
        filename, _ = os.path.splitext(f)
        fullf = os.path.abspath(os.path.join('media', 'images', f))
        if hasattr(m, filename):
            delattr(m, filename)
        setattr(m, filename, load_image(fullf))

def load_sound(snd):
    return pygame.mixer.Sound(snd)

def load_all_sounds():
    for f in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'media', 'sounds')):
        filename, _ = os.path.splitext(f)
        fullf = os.path.abspath(os.path.join('media', 'sounds', f))
        setattr(m, filename, load_sound(fullf))
        setattr(m, filename + '_file', fullf)
        
def get_font(size):
    return pygame.font.Font(os.path.join('.', 'media', 'fonts', 'PressStart2P.ttf'), size)

def load_all_fonts():
    pass

load_all_images()
load_all_sounds()
load_all_fonts()
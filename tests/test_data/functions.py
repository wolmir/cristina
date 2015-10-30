import pygame
from pygame.locals import *

import os
import sys

from globals import *

def load_image(name, alpha_color=False):
    ruta = os.path.join("data", "images", name)
    try:
        image = pygame.image.load(ruta)
    except:
        print "Error while trying to load the image", ruta
        sys.exit(1)

    if alpha_color == "alpha":
        image = image.convert_alpha()
    elif alpha_color == "colorkey":
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    else:
        image = image.convert()

    return image

def update_groups():

    ###UPDATE ALL GROUPS
    OBJECTS.update()
    ENEMIES.update()
    PLAYER.update()
    EFFECTS.update()
    MAP.update()
    HUD.update()

def empty_groups():

    ENEMIES.empty()
    OBJECTS.empty()
    HUD.empty()
    PLAYER.empty()
    MAP.empty()
    EFFECTS.empty()










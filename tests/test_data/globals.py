import pygame
from pygame.locals import *

###GROUPS OF SPRITES
ENEMIES = pygame.sprite.Group()
OBJECTS = pygame.sprite.Group()
EFFECTS = pygame.sprite.Group()
PLAYER = pygame.sprite.GroupSingle()
HUD = pygame.sprite.GroupSingle()
MAP = pygame.sprite.GroupSingle()

###GLOBALS
TILE_SIZE = 32

MENU = 1
LEVEL_SELECT = 2
ON_GAME = 3
GAME_OVER = 4
GAME_MODE = MENU
MAX_LEVELS = 15

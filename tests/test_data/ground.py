from entity_sys import EntitySystem
from entity import base_entity
from material import MatSys
from vector2d import Vector2D

from pygame.locals import *

class Ground(base_entity):
	texture="data/platform_test.tga"
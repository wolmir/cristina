#7444
#BG

from entity import base_entity
from vector2d import Vector2D

class Background(base_entity):
	texture="data/stars.tga"
	position = Vector2D(960,540)
	def move(self, vec):
		self.position += vec
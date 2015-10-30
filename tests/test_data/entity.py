#7444
#Base Entity

from entity_sys import EntitySystem
from material import MatSys
from vector2d import Vector2D
from pygame.locals import *
from logger import Log

class base_entity:
	parent = None
	position = Vector2D(0, 0)
	texture = None
	name = None
	box = None
	health = 100

	def load(self, engine, position = Vector2D(0,0)): #load() - add assets to the material system
		self.position = position
		if self.texture:
			MatSys.AddMaterial(self.texture)

	def update(self, dt, engine): #update(dt: time since last frame(integer)) - doing AI, etc.
		pass
		
	def draw(self, engine): #draw() - draw the entity
		if self.texture:
			engine.DrawImage(MatSys.GetMaterial(self.texture), self.position)

	def set_pos(self, new_pos):
		self.position = new_pos

	def hurt(self, hp):
		self.health -= hp
from entity import base_entity
from entity_sys import EntitySystem as EntSys
from logger import Log
import math
from vector2d import Vector2D

class PhotonTorpedo(base_entity):
	texture="data/torpedo.tga"
	target = None
	velocity = 0.8
	def update(self, dt, engine):
		if self.velocity < 100:
			self.velocity *= 1.1
		else:
			EntSys.RemoveEntity(self.name)
		self.position += self.target * self.velocity
		EntSys.CollisionCheck(self, 25, True)
	def shoot(self, start, target):
		self.position = start
		self.target = target
#7444
#Entity System

import pygame
from logger import Log
from vector2d import Vector2D
import random
from material import MatSys

class EntitySystem:
	entities = {}
	spawnqueue = {}
	draw_over = True
	name = None
	@staticmethod
	def AddEntity(entity, name = None, position = Vector2D(0,0), physics = False, engine = None):
		nname = None
		if EntitySystem.draw_over:
			nname = name if name else str(entity).split('.')[1] + str(random.randint(0, 4563564575785745))
			Log.Message("Spawning entity " + str(entity) + " with name " + str(nname))
			ent = entity()
			ent.name = nname
			ent.load(engine, position)
			ent.set_pos(position)
			EntitySystem.entities[nname] = ent
			return EntitySystem.EntityByName(nname)
		else:
			Log.Warning("Think or draw is not over, adding to queue")
			EntitySystem.spawnqueue[nname] = (entity, nname, position)


	@staticmethod
	def Think(dt, engine):
		try:
			for ent in EntitySystem.entities:
				EntitySystem.entities[ent].update(dt, engine)
		except RuntimeError:
			pass

	@staticmethod
	def Draw(engine):
		EntitySystem.draw_over = False
		EntitySystem.entities["background"].draw(engine)

		for ent in EntitySystem.entities:
			if ent == "player" or ent == "background":
				pass
			else:
				EntitySystem.entities[ent].draw(engine)

		EntitySystem.entities["player"].draw(engine)
		EntitySystem.draw_over = True
		for ent in EntitySystem.spawnqueue:
			entity = EntitySystem.spawnqueue[nname]
			EntitySystem.AddEntity(entity[0], entity[1], entity[2])

	@staticmethod
	def ClearEntities(engine = None):
		EntitySystem.entities = {}

	@staticmethod
	def EntityByName(name):
		return EntitySystem.entities[name] if EntitySystem.entities[name] else None

	@staticmethod
	def RemoveEntity(name):
		try:
			del EntitySystem.entities[name]
		except KeyError:
			Log.Error("Entity with name " + name + " doesn't exists")

	@staticmethod
	def CollisionCheck(me, hp = 50, selfdestroy = False, countplayer = False):
		me_rect = MatSys.GetMaterial(me.texture).get_rect()
		me_x = me.position.x
		me_y = me.position.y
		me_w = me_rect.right
		me_h = me_rect.bottom
		for ent in EntitySystem.entities:
			if not ent == me.name:
				if ent == "background" or (ent == "player" and (not countplayer)) or "PhotonTorpedo" in ent:
					pass
				else:
					entity = EntitySystem.entities[ent]
					if entity.texture:
						mat = MatSys.GetMaterial(entity.texture)
						mat_w = mat.get_width()
						mat_h = mat.get_height()
						if not ((me_y + me_h <= entity.position.y) or (me_y >= entity.position.y + mat_h) or (me_x >= entity.position.x + mat_w) or (me_x + me_w <= entity.position.x)): 
							Log.Message("Collision between " + str(me.name) + " and " + str(ent))
							if countplayer: me.hurt(hp) 
							else: entity.hurt(hp)
							if selfdestroy: EntitySystem.RemoveEntity(me.name)

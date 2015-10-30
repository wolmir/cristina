from math import *
from random import *
import state, settings

class Thing(object):

	layers = [
		["brown", 0],
	]
	alive = True
	flashtime = 0
	cooltime = 0
	hp0 = 1
	alwaysinrange = False
	tlive = 0
	ascale = None
	h = 1
	casts = True
	
	dhp = 1

	def __init__(self, pos):
		self.x, self.y, self.z = pos
		self.vx, self.vy, self.vz = 0, 0, 0
		self.ax, self.ay, self.az = 0, 0, 0
		self.theta = 0
		self.tilt = None
		self.hp = self.hp0
		self.t = 0

	def think(self, dt):
		self.t += dt
		if self.flashtime:
			self.flashtime = max(self.flashtime - dt, 0)
		if self.cooltime:
			self.cooltime = max(self.cooltime - dt, 0)
		if self.tlive and self.t > self.tlive:
			self.alive = False
		if self.hp <= 0:
			self.alive = False
		if not self.alwaysinrange and self.y < state.yc:
			self.alive = False
		self.move(dt)

	def move(self, dt):
		vx0, vy0, vz0 = self.vx, self.vy, self.vz
		self.vx += dt * self.ax
		self.vy += dt * self.ay
		self.vz += dt * self.az
		self.constrainvelocity()
		self.x += 0.5 * dt * (self.vx + vx0)
		self.y += 0.5 * dt * (self.vy + vy0)
		self.z += 0.5 * dt * (self.vz + vz0)

	def constrainvelocity(self):
		pass

	def getlayers(self):
		if self.flashtime and self.flashtime ** 1.4 * 20 % 2 < 1:
			return
		if self.tilt:
			dxdy, dzdy = self.tilt
			for layername, dy in self.layers:
				x = self.x + dy * dxdy
				y = self.y + dy
				z = self.z + dy * dzdy
				yield layername, x, y, z, self.theta, self.ascale, self
		else:
			for layername, dy in self.layers:
				yield layername, self.x, self.y + dy, self.z, self.theta, self.ascale, self

	def causedamage(self):
		pass

	def getshadows(self):
		if self.casts and self.z > self.h / 2:
			yield self.x, self.y, self.r

class Rock(Thing):
	casts = False
	def __init__(self, pos, size):
		Thing.__init__(self, pos)
		self.size = self.w, self.h = size
		w0, h0 = self.w, self.h + 0.7
		w1, h1 = w0 - 0.2, h0 - 0.2
		w2, h2 = w0 - 0.4, h0 - 0.4
		self.r = self.w / 2
		self.layers = [
			["rock%s,%s" % (w2, h2), 0.2],
			["rock%s,%s" % (w1, h1), 0.1],
			["rock%s,%s" % (w0, h0), 0],
			["rock%s,%s" % (w1, h1), -0.1],
			["rock%s,%s" % (w2, h2), -0.2],
		]
		if settings.lowres:
			self.layers = self.layers[2:3]
	def hitany(self, objs):
		for h in objs:
			if not h.alive:
				continue
			if h.z > self.h/2:
				continue
			dx, dy = h.x - self.x, h.y - self.y
			if dx ** 2 + dy ** 2 < (self.r + h.r) ** 2:
				h.causedamage()


class Shipwreck(Thing):
	r = 0.7
	h = 0.5
	layers = [["shipwreck.png", 0]]
	smokes = 1
	ascale = 2
	def hitany(self, objs):
		for h in objs:
			if not h.alive:
				continue
			if h.z > self.r:
				continue
			dx, dy = h.x - self.x, h.y - self.y
			if dx ** 2 + dy ** 2 < (self.r + h.r) ** 2:
				self.alive = False
				state.addsmoke(self, self.smokes)
				state.addsilver(self)
				h.causedamage()

class Mine(Thing):
	layers = [
		["mine", 0],
	]
	h = 0.1
	r = 0.05
	def __init__(self, pos, vel):
		Thing.__init__(self, pos)
		self.vx, self.vy, self.vz = vel
		self.landed = False
		self.az = -30
		self.t = uniform(0, 100)

	def think(self, dt):
		Thing.think(self, dt)
		if self.landed:
			self.z = -0.05 + 0.15 * sin(3 * self.t)
		if not self.landed and self.z <= 0 and self.vz < 0:
			self.landed = True
			self.vy = 0
			self.vz = 0
			self.vx = 0
			self.z = 0.05
			self.az = 0

	def causedamage(self):
		self.alive = False
		import effect
		state.effects.append(effect.Splode((self.x, self.y, self.z)))

	def hitany(self, objs):
		pass

class Projectile(Thing):
	vy0 = 12
	tlive = 1
	r = 0.1
	h = 0.2
	layers = [["cannonball", 0]]
	def __init__(self, obj, (dx, dy, dvx, dvy)):
		Thing.__init__(self, (obj.x + dx, obj.y + dy, obj.z + 0.2))
		self.vy = state.vyc + self.vy0 + dvy
		self.vx = (obj.vx / obj.vy * self.vy if obj.vy else 0) + dvx
		#self.vz = obj.vz / obj.vy * self.vy if obj.vy else 0
		self.move(0.001)
	def causedamage(self):
		self.alive = False

class Silver(Thing):
	layers = [["silver.png", 0]]
	dhp = -1
	r = 0.5
	h = 2
	def __init__(self, pos):
		Thing.__init__(self, pos)
		self.vx = 0
		self.vy = state.vyc + 2
		self.vz = 30
		self.az = -60
	def think(self, dt):
		Thing.think(self, dt)
		if self.vz < 0 and self.z < 2:
			self.vy = self.vz = self.az = 0
			self.z = 2
	def causedamage(self):
		self.alive = False
	def hitany(self, objs):
		pass

class Slinker(Thing):
	tlive = 4
	casts = False
	def __init__(self, obj):
		self.obj = obj
		Thing.__init__(self, (obj.x, obj.y, obj.z))
		self.vx = obj.vx
		self.vy = obj.vy
		self.vz = 0
		self.az = -1
		self.ascale = obj.ascale
	def getlayers(self):
		for imgname, x, y, z, theta, ascale, obj in self.obj.getlayers():
			yield imgname, self.x, self.y, self.z, theta, ascale, obj



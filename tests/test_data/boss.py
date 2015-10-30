from random import *
from math import *
from thing import *
from ship import *
import state, settings, sound

class Boss(Ship):
	hp0 = 50
	tflash = 0.2
	kx = 2
	ky = 4
	betax = 1
	betay = 4
	firetime = 0.5
	def __init__(self, pos, dytarget):
		Ship.__init__(self, pos)
		self.dytarget = dytarget
		self.xtarget = 0
	def move(self, dt):
		self.ytarget = state.yc + self.dytarget
		self.ay = self.ky * (self.ytarget - self.y)
		self.ax = self.kx * (self.xtarget - self.x)
		Ship.move(self, dt)
		self.vy += (state.vyc - self.vy) * self.betay * dt
		self.vx += (0 - self.vx) * self.betax * dt
		self.vx = min(max(self.vx, -4), 4)
	def constrainvelocity(self):
		self.vy = max(self.vy, 1)
	def think(self, dt):
		if abs(self.xtarget - self.x) < 0.1:
			self.xtarget = uniform(-settings.lwidth, settings.lwidth)
		if abs(self.ay) < 1:
			self.fire(dt)
		Ship.think(self, dt)

	def fire(self, dt):
		if random() * self.firetime < dt:
			pos = self.x, self.y + 0.1, 0.2
			vel = uniform(-5, 5), self.vy + 4, 10
			state.hazards.append(Mine(pos, vel))

class Boss1(Boss):
	hp0 = 12
	firetime = 1
	level = 3
	firetime = 0.35
	def __init__(self, pos, dytarget):
		Boss.__init__(self, pos, dytarget)
		self.layers = piratelayers(1)
		self.ascale = 2
		self.r *= 2

class Bosslet(Boss1):
	hp0 = 16
	level = 2
	firetime = 0.2
	def fire(self, dt):
		nboss = sum(b.alive for b in state.bosses)
		if random() * self.firetime * nboss < dt:
			pos = self.x, self.y + 0.1, 0.2
			vel = uniform(-5, 5), self.vy + 4, 10
			state.hazards.append(Mine(pos, vel))
	

class Balloon(Boss):
	alwaysinrange = True
	ky = 1
	betax = 1.2
	kx = 1
	r = 0.7
	h = 6
	ascale = 2
	hp0 = 20
	firetime = 0.8
	def __init__(self, pos, dytarget):
		Boss.__init__(self, pos, dytarget)
		self.layers = [
			["baloon-body-0.png", 0.5],
			["baloon-body-1.png", -0.5],
			["baloon-gondola.png", 0.5],
			["baloon-gondola.png", 0.375],
			["baloon-gondola.png", 0.25],
			["baloon-gondola.png", 0.125],
			["baloon-gondola.png", 0],
			["baloon-gondola.png", -0.125],
			["baloon-gondola-sails.png", -0.25],
			["baloon-gondola.png", -0.375],
			["baloon-gondola.png", -0.5],
		]
		self.xtarget = 0
		self.z = 6
	def constrainvelocity(self):
		self.vy = max(self.vy, 1)
		if abs(self.ytarget - self.y) > 1:
			self.ax = self.vx = self.x = 0
	def think(self, dt):
		Boss.think(self, dt)
		self.z = 6 + 1.4 * sin(self.t * 1)
	def fire(self, dt):
		if random() * self.firetime < dt:
			pos = self.x, self.y, self.z - 1
			vel = uniform(-5, 5), self.vy + uniform(-2, 2), 4
			state.hazards.append(Mine(pos, vel))
	def getlayers(self):
		for layername, x, y, z, theta, ascale, obj in Boss.getlayers(self):
			yield layername, x, y, z, -2 * theta, ascale, obj

class Ghost(Boss):
	alwaysinrange = True
	hp0 = 60
	ascale = 2
	r = 2
	layers = [
		["ghost-body-1.png", -0.6],
		["ghost-body-2.png", -0.4],
		["ghost-body-3.png", -0.2],
		["ghost-body-4.png", 0],
		["ghost-body-3.png", 0.2],
		["ghost-body-2.png", 0.4],
		["ghost-face.png", -0.6],
		["ghost-mast-1.png", -0.25],
		["ghost-mast-2.png", 0],
		["ghost-mast-3.png", 0.25],
		["ghost-wing-1.png", -0.25],
		["ghost-wing-2.png", 0.25],
	]
	def __init__(self, pos, dytarget):
		Boss.__init__(self, (0, dytarget, -8), dytarget)
		self.vz = 1
		self.form = 0
		self.kx = 0.5
		self.ky = 4
		self.betax = 2
		self.betay = 4
		self.firetime = 0.1
	def think(self, dt):
		Boss.think(self, dt)
		if self.form == 0 and self.z > 0 and self.vz > 0:
			self.z = self.vz = 0
			self.form = 1
		if self.form == 2 and self.z < -5 and self.vz < 0:
			self.vz = 8
			self.hp = self.hp0
			self.kx = 10
			self.betax = 0.25
			self.firetime = 0.1
			sound.playsound("addboss")
		if self.form == 2 and self.z > 5 and self.vz > 0:
			self.vz, self.z = 0, 5
			self.form = 3
	def land(self):
		pass
	def hurt(self, dhp):
		if self.form == 0 or self.form == 2:
			return
		if self.form == 1 and self.hp <= 1:
			sound.playsound("killboss")
			self.form = 2
			self.vz = -1
			self.az = 0
			self.z = 0
			return
		Boss.hurt(self, dhp)	
	def fire(self, dt):
		if self.form in [1, 3] and random() * self.firetime < dt:
			pos = self.x, self.y, self.z
			vel = uniform(-5, 5), self.vy + uniform(0, 3), 20
			state.hazards.append(Mine(pos, vel))
	def getlayers(self):
		for imgname, x, y, z, theta, ascale, obj in Boss.getlayers(self):
			dz = 1.4 * sin(self.t + 2 * (y - self.y))
			yield imgname, x, y, z + dz, theta, ascale, obj


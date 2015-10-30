from __future__ import division
from random import *
from math import *
from thing import *
from effect import *
import settings, state, sound

def piratelayers(level):
	if level == 1 or level == 2:
		return [
			["pirate-back.png", -0.2],
			["pirate-body-2.png", -0.1],
			["pirate-body-3.png", 0],
			["pirate-body-3.png", 0.1],
			["pirate-body-2.png", 0.2],
			["pirate-body-1.png", 0.3],
			["pirate-sail-%s.png" % choice([1, 2, 3]), 0],
			["pirate-sail-%s.png" % choice([1, 2, 3]), 0.2],
			["pirate-nest.png", 0.1],
		]	
	if level == 3:
		return [
			["pirate-back.png", -0.3],
			["pirate-body-2.png", -0.2],
			["pirate-body-3.png", -0.1],
			["pirate-body-3.png", 0],
			["pirate-body-3.png", 0.1],
			["pirate-body-2.png", 0.2],
			["pirate-body-2.png", 0.3],
			["pirate-body-1.png", 0.4],
			["pirate-sail-%s.png" % choice([1, 2, 3]), -0.2],
			["pirate-sail-%s.png" % choice([1, 2, 3]), 0],
			["pirate-sail-%s.png" % choice([1, 2, 3]), 0.2],
			["pirate-nest.png", 0.1],
			["pirate-nest.png", -0.1],
		]	

class Ship(Thing):
	shottype = Projectile
	tcooldown = 2
	tflash = 1
	smokes = 2
	twake = 0.1
	r = 0.4
	h = 1
	jumps = 1

	def __init__(self, pos):
		Thing.__init__(self, pos)
		self.njump = 0
		self.tilt = [0, 0]
		self.flashtime = 0
		self.cooltime = 0
		self.waket = 0
		if settings.lowres:
			self.twake = None

	def think(self, dt):
		Thing.think(self, dt)
		tiltx = 0.75 * min(max(self.vx, -3), 3)
		tilty = 0.75 * self.vz
		self.tilt[0] += (tiltx - self.tilt[0]) * 5 * dt
		self.tilt[1] += (tilty - self.tilt[1]) * 5 * dt
		theta = min(max(0.03 * self.ax, -0.2), 0.2)
		self.theta += (theta - self.theta) * 5 * dt
		if self.z <= 0 and self.twake:
			self.waket += dt
			while self.waket > self.twake:
				state.effects.append(Wake((self.x, self.y, self.z)))
				self.waket -= self.twake
		if self.z < 0 and self.vz < 0:
			self.land()
	
	def land(self):
		self.z = self.vz = self.az = 0
		self.njump = 0
		sound.playsound("splash")
		state.addsplash(self)
		if not settings.lowres:
			state.addsplash(self)

	def jump(self, f=1):
		if self.njump >= self.jumps:
			return
		self.njump += 1
		self.vz = 12 * f
		self.az = -30
		self.z = max(self.z, 0)
		sound.playsound("jump")

	def fire(self):
		if self.cooltime > 0:
			return
		state.projectiles.append(self.shottype(self))
		self.cooltime = self.tcooldown

	def hurt(self, dhp=1):
		self.hp -= dhp
		self.flashtime = self.tflash
		if self.hp <= 0:
			self.die()
		else:
			sound.playsound("hurt")
			if self.smokes:
				state.addsmoke(self, self.smokes)

	def die(self):
		state.effects.append(Corpse(self))

	def hitany(self, objs):
		if self.flashtime:
			return
		for h in objs:
			if not h.alive:
				continue
			dx, dy = h.x - self.x, h.y - self.y
			if dx ** 2 + dy ** 2 < (self.r + h.r) ** 2 and abs(self.z - h.z) < (self.h + h.h) / 2:
				self.hurt(h.dhp)
				h.causedamage()


class PirateShip(Ship):
	hp0 = 1
	tflash = 0.01
	firerate = 1
	def __init__(self, pos, v, level):
		self.hp = self.hp0 = level
		Ship.__init__(self, pos)
		self.vx, self.vy = v
		self.level = level
		self.firerate = 1 / level
		self.layers = piratelayers(level)
	def think(self, dt):
		Ship.think(self, dt)
	def die(self):
		Ship.die(self)
		sound.playsound("kill")


class MineShip(PirateShip):
	def fire(self, dt):
		if random() * self.firerate < dt:
			pos = self.x, self.y + 0.1, 0.2
			vel = uniform(-5, 5), self.vy + 4, 10
			state.hazards.append(Mine(pos, vel))
	def think(self, dt):
		if abs(self.x) < settings.lwidth + 3:
			self.fire(dt)
		PirateShip.think(self, dt)
	def die(self):
		PirateShip.die(self)
		if random() < 0.2:
			state.addsilver(self)

class JumpShip(MineShip):
	def think(self, dt):
		MineShip.think(self, dt)
		if random() * 3 < dt:
			self.jump(0.6)


class Blockade(Ship):
	hp0 = 999999
	tflash = 0
	layers = [["rock2,5", 0]]
	twake = 0
	r = 1
	h = 5

	def __init__(self, x0, dx, y0, omega):
		self.x0 = x0
		self.omega = omega
		self.dx = dx
		Ship.__init__(self, (x0, y0 + state.yc, -2))
		self.vy = state.vyc
		self.vz = 0.5
		self.t = uniform(0, 1000)
	
	def think(self, dt):
		self.vx = 0
		Ship.think(self, dt)
		self.x = self.x0 + self.dx * cos(self.omega * self.t)
		if self.z >= 0:
			self.z = 0
			self.vz = 0

	def hurt(self, dhp=1):
		pass


def randomcolor():
	return "rgb%s,%s,%s" % (randint(100, 200), randint(100, 200), randint(100, 200))

class PlayerShip(Ship):
	alwaysinrange = True
	smokes = 6
	twake = 0.02
	
	def __init__(self, pos):
		Ship.__init__(self, pos)
		self.layers = []
		self.layers = [
			["you-back.png", -0.18],
			["you-body-2.png", -0.15],
			["you-body-2.png", -0.12],
			["you-sail-1.png", -0.12],
			["you-body-3.png", -0.09],
			["you-body-3.png", -0.06],
			["you-sail-2.png", -0.06],
			["you-body-3.png", -0.03],
			["you-body-3.png", 0],
			["you-body-2.png", 0.03],
			["you-sail-1.png", 0.03],
			["you-body-2.png", 0.06],
			["you-body-2.png", 0.09],
			["you-sail-2.png", 0.09],
			["you-body-1.png", 0.12],
			["you-body-1.png", 0.15],
			["you-body-1.png", 0.18],
			["you-front.png", 0.21],
		]
		if settings.lowres:
			self.layers = [
				["you-back.png", -0.18],
				["you-body-2.png", -0.15],
				["you-sail-1.png", -0.12],
				["you-body-3.png", -0.09],
				["you-body-3.png", -0.03],
				["you-body-2.png", 0.03],
				["you-body-2.png", 0.09],
				["you-sail-2.png", 0.09],
				["you-body-1.png", 0.12],
				["you-body-1.png", 0.15],
				["you-front.png", 0.21],
			]
		self.falling = False
		self.cannontick = 0
		self.tblitz = 0
		self.grace = 0

	def think(self, dt):
		Ship.think(self, dt)
		if self.tblitz:
			self.tblitz = max(self.tblitz - dt, 0)

	def move(self, dt):
		ytarget = state.yc + (settings.dyfall if self.falling else settings.dyjump if self.z > 0 else settings.dynormal)
		self.ay = 6 * (ytarget - self.y)
		self.vy += self.ay * dt
		self.y += self.vy * dt
		ax = self.ax
		vx0 = self.vx
		if self.ax and self.ax * self.vx >= 0:
			self.vx += self.ax * dt
		elif self.vx:
			dvx = settings.xslow * dt
			if dvx > abs(self.vx):
				self.vx = 0
			else:
				self.vx -= dvx * cmp(self.vx, 0)
		self.vx = min(max(self.vx, -settings.vxmax), settings.vxmax)
		self.x += 0.5 * (self.vx + vx0) * dt
		self.x = min(max(self.x, -settings.lwidth), settings.lwidth)
		self.vy += (state.vyc - self.vy) * 3 * dt
		self.z += self.vz * dt + 0.5 * self.az * dt * dt
		self.vz += self.az * dt

	def control(self, dx, jumping, shooting):
		if self.falling:
			self.ax = 0
			return
		self.ax = dx * settings.ax
		if jumping:
			self.jump()
		if shooting:
			self.fire()

	def fire(self):
		if self.cooltime > 0:
			return False
		state.projectiles.append(self.shottype(self, self.cannons[self.cannontick]))
		sound.playsound("shoot")
		self.cannontick += 1
		self.cannontick %= len(self.cannons)
		self.cooltime = self.tcooldown
		if self.tblitz:
			self.cooltime /= 10

	def hurt(self, dhp=1):
		if dhp >= 0:
			if settings.easy:
				self.grace += 1
				if self.grace == 3:
					self.grace = 0
				else:
					dhp = 0
			return Ship.hurt(self, dhp)
		state.addhp(-dhp)

	def die(self):
		Ship.die(self)
		state.gameover()


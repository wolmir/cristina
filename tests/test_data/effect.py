from random import *
from math import *
from thing import *
import state
tau = 2 * pi

class Particles(Thing):
	nparticle = 5
	vz0 = 10
	az0 = -30
	vspread = 4
	tlive = 1
	vy = 0
	aspread = 3
	casts = False

	def __init__(self, pos):
		Thing.__init__(self, pos)
		self.particles = [
			(uniform(-1, 1), uniform(-1, 1), uniform(-1, 1), uniform(-1, 1))
			for _ in range(self.nparticle)
		]
		self.vz = self.vz0
		self.az = self.az0

	def getlayers(self):
		a = self.t * self.vspread
		self.ascale = 1 + self.t * self.aspread
		for px, py, pz, theta in self.particles:
			yield self.imgname, self.x + a * px, self.y + a * py, self.z + a * pz, theta, self.ascale, self


class Splash(Particles):
	imgname = "splash"
	vz0 = 16

class Wake(Thing):
	casts = False
	layers = [["wake", 0]]
	tlive = 1
	def __init__(self, pos):
		Thing.__init__(self, pos)
		self.vx = uniform(-5, 5)
		self.vy = uniform(-5, 5)
		self.vz = 2
		self.az = -8
		self.z = -0.1
		

class Smoke(Particles):
	imgname = "smoke"
	vz0 = 12
	az0 = 0
	def __init__(self, pos, level):
		self.nparticles = level
		Particles.__init__(self, pos)

class Heal(Particles):
	imgname = "heal"
	vz0 = 5
	az0 = -20
	vspread = 1
	aspread = 1
	def __init__(self, *args, **kwargs):
		Particles.__init__(self, *args, **kwargs)
		self.vy = state.vyc

class Splode(Thing):
	casts = False
	tlive = 0.3
	layers = [["mine", 0]]
	def think(self, dt):
		Thing.think(self, dt)
		self.ascale = 1 + 20 * self.t

class Decoration(Thing):
	casts = False

class Island(Decoration):
	layers = [["island.png", 0]]
	ascale = 4

class Flock(Decoration):
	casts = False
	def __init__(self, pos, vel):
		Decoration.__init__(self, pos)
		self.vx, self.vy, self.vz = vel
		self.birds = [
			(uniform(-3, 3), uniform(-3, 3), uniform(-0.3, 0.3), uniform(0, 1000))
			for _ in range(16 if settings.lowres else 40)
		]
		self.omega = 10
	def getlayers(self):
		for dx, dy, dz, phi0 in self.birds:
			phi = (phi0 + self.t * self.omega) % tau
			x, y, z0 = self.x + dx, self.y + dy, self.z + dz - 0.2 * tau/4
			if phi < tau/2:
				yield "bird-up.png", x, y, z0 + 0.2 * phi, 0, 1, self
			else:
				yield "bird-down.png", x, y, z0 + 0.2 * (tau - phi), 0, 1, self

class Cloud(Decoration):
	casts = False
	layers = [["cloud.png", 0]]
	def __init__(self, pos, vel):
		Decoration.__init__(self, pos)
		self.vx, self.vy, self.vz = vel
		self.ascale = uniform(8, 15)

class Whale(Decoration):
	casts = False
	layers = [["whale.png", 0]]
	tlive = 5
	def __init__(self, pos):
		Decoration.__init__(self, pos)
		self.vx, self.vy, self.vz = 2, 0, 4
		self.az = -self.vz / 2
		self.ascale = 4
		self.landed = False
	def think(self, dt):
		Decoration.think(self, dt)
		if self.z < 0 and self.vz < 0 and not self.landed:
			state.addsplash(self)
			self.landed = True
		self.theta = 0.1 * self.vz
		

class Instructions(Thing):
	casts = False
	r = 2
	def __init__(self, text, y):
		Thing.__init__(self, (0, y, 5))
		self.layers = [
			["text:" + text, 0],
#			["text0:" + text, 0.05],
		]
		self.tilt = 1, -1
	def think(self, dt):
		self.vy = state.vyc - 8
		Thing.think(self, dt)
		self.z = state.zc

class Corpse(Thing):
	tlive = 2
	def __init__(self, obj):
		Thing.__init__(self, (obj.x, obj.y, obj.z))
		self.layers = obj.layers
		self.vx = obj.vx
		self.vy = obj.vy
		self.vz = 10
		self.az = -20
		self.tilt = obj.tilt or (0, 0)
		self.theta0 = obj.theta
		self.thetas = [uniform(-2, 2) for _ in self.layers]
		self.ds = [(uniform(-3, 3), uniform(-1, 1)) for _ in self.layers]
		self.r = obj.r
		self.ascale = obj.ascale
		
	def think(self, dt):
		Thing.think(self, dt)

	def getlayers(self):
		dxdy, dzdy = self.tilt
		for (layername, dy), dtheta, (dx, dz) in zip(self.layers, self.thetas, self.ds):
			theta = self.theta0 + self.t * dtheta
			x = self.x + self.t * dx + dy * dxdy
			y = self.y + dy
			z = self.z + self.t * dz + dy * dzdy
			yield layername, x, y, z, theta, self.ascale, self



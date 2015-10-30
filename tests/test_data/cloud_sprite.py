import pygame

from padlib import particle_system
from albow.resource import get_image

from mutate_sprite import MutateSprite

class CloudSprite(MutateSprite):
	def __init__( self, color, pos ):
		MutateSprite.__init__( self, color, pos )
		self.color = color
		self.isSun = False
		self.rect = pygame.Rect(pos,(1,1))
		self.redraw()

		position = pos
		colors = [(255,0,0), (0,255,0), (0,0,255)]
		speeds = [1,4]
		disperse = 180
		direction = 90
		density = 8
		framestolast = 200
		#make the particle system object
		self.rain = particle_system(position,colors,speeds,disperse,direction,density,framestolast)
		entropy = 0.5
		gravity = (0.0,0.01)
		randomness = 0.1
		self.rain.set_occluders([])
		self.rain.set_bounce(entropy,randomness)
		self.rain.set_gravity(gravity)

	def update(self):
		MutateSprite.update(self)
		#self.rain.change_position( self.rect.center )
		#self.rain.update()

	def setColor(self, color):
		self.color = color
		self.redraw()

	def redraw(self):
		SURFACE_WIDTH = 333
		SURFACE_HEIGHT = 187

		self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		self.imageMaster.fill((255,0,255))
		image = get_image("cloud.png").convert()
		image.set_colorkey((255,0,255))
		self.imageMaster.blit( image, (0,0))

		self.imageMaster.set_colorkey((255,0,255))

		self.image = self.imageMaster

		#self.image = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		#pygame.draw.circle(self.image, (128,128,128), (30,65), 15 )
		#pygame.draw.circle(self.image, (128,128,128), (50,50), 30 )
		#pygame.draw.circle(self.image, (128,128,128), (60,15), 20 )
		#pygame.draw.circle(self.image, (128,128,128), (85,35), 30 )
		#self.image.set_colorkey((0,0,0))

		pos = self.rect.center
		self.rect = self.image.get_rect()
		self.rect.center = pos	
import pygame

from albow.resource import get_image
from albow.utils import blit_tinted

from mutate_sprite import MutateSprite

class SunSprite(MutateSprite):

	def __init__( self, color, pos ):
		MutateSprite.__init__( self, color, pos )
		self.color = color
		self.isSun = True
		self.rect = pygame.Rect(pos,(1,1))
		self.redraw()

	def setColor(self, color):
		self.color = color
		self.redraw()

	def redraw(self):
		SURFACE_WIDTH = 200
		SURFACE_HEIGHT = 200
		oldAlpha = self.image.get_alpha()

		self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		self.imageMaster.fill((255,0,255))
		image = get_image("sun.png").convert()
		image.set_colorkey((255,0,255))
		blit_tinted( self.imageMaster, image, (0,0), (self.color.r, self.color.g, self.color.b ) )

		#outline = get_image("sun_outline.png").convert()
		#outline.set_colorkey((255,0,255))
		#self.imageMaster.blit( outline, (0,0))
		#pygame.draw.circle(self.imageMaster, self.color, (SURFACE_WIDTH/2,SURFACE_HEIGHT/2), SURFACE_WIDTH/2 )
		#self.imageMaster.set_colorkey((255,0,255))

		#self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		#pygame.draw.circle(self.imageMaster, self.color, (SURFACE_WIDTH/2,SURFACE_HEIGHT/2), SURFACE_WIDTH/2 )
		self.imageMaster.set_colorkey((255,0,255))

		self.image = self.imageMaster

		pos = self.rect.center
		self.rect = self.image.get_rect()
		self.rect.center = pos

		self.image.set_alpha(oldAlpha)


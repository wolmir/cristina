import pygame

from albow.resource import get_image

from mutate_sprite import MutateSprite

class BloomPlusOne( MutateSprite ):
	def __init__( self, pos ):
		MutateSprite.__init__( self, pos=pos )
		SURFACE_WIDTH = 100
		SURFACE_HEIGHT = 20

		self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		self.imageMaster.fill((255,0,255))
		image = get_image("bloom_plus_one.png").convert()
		image.set_colorkey((255,0,255))
		self.imageMaster.blit( image, (0,0))

		self.imageMaster.set_colorkey((255,0,255))

		self.image = self.imageMaster
		
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.image.set_alpha(255)
import pygame

from albow.resource import get_image
from albow.utils import blit_tinted

from sun_sprite import SunSprite
from mutate_color import MutateColor

class Day():
	def __init__( self, weather=None ):
		#self.weather = weather
		self.weather = weather
		self.color = MutateColor(0,0,0).sequence("RRR")
		self.desc = "Sun - " + str(self.color)

	def setWeatherColor(self, color):
		self.color = color
		#self.weather.color = color
		self.desc = "Sun - " + str(self.color)

	def affect_flowers(self, flowers):
		if self.weather.isSun:
			for flower in flowers:
				flower.photosynthesis(self)
		else:
			for flower in flowers:
				flower.water(self)

	def getIcon(self):
		self.iconSize = 50
		SURFACE_WIDTH = self.iconSize
		SURFACE_HEIGHT = self.iconSize
		icon = pygame.Surface((SURFACE_WIDTH, SURFACE_HEIGHT))
		icon.fill( (255,255,255) )

		if self.weather.isSun:
			self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
			self.imageMaster.fill((255,0,255))
			image = get_image("sun_icon.png").convert()
			image.set_colorkey((255,0,255))
			blit_tinted( self.imageMaster, image, (0,0), (self.color.r, self.color.g, self.color.b ) )

			self.imageMaster.set_colorkey((255,0,255))

			icon = self.imageMaster

			return icon

			#pygame.draw.circle( icon,
			#                    self.color,
			#                    (SURFACE_WIDTH/2,SURFACE_HEIGHT/2),
			#                    SURFACE_HEIGHT/2)
		else:
			self.imageMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
			self.imageMaster.fill((255,0,255))
			image = get_image("cloud_icon.png").convert()
			image.set_colorkey((255,0,255))
			blit_tinted( self.imageMaster, image, (0,0), (self.color.r, self.color.g, self.color.b ) )

			self.imageMaster.set_colorkey((255,0,255))

			icon = self.imageMaster

			return icon
			#pygame.draw.circle( icon,
			#					(128,128,128),
			#					(SURFACE_WIDTH/2,SURFACE_HEIGHT/2),
			#					SURFACE_HEIGHT/2)

			#pygame.draw.circle( icon,
			#					self.color,
			#					(SURFACE_WIDTH/4,SURFACE_HEIGHT/4),
			#					SURFACE_HEIGHT/4)
		return icon

	def draw(self, surface):
		pass
		#self.weather.draw(surface)
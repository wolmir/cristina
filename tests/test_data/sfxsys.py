import pygame

class SfxSys:

	sounds = {}

	@staticmethod
	def LoadSound(filename):
		SfxSys.sounds[filename] = pygame.mixer.Sound(filename)
		SfxSys.sounds[filename].set_volume(SfxSys.sounds[filename].get_volume() * 2)

	@staticmethod
	def Play(filename, loop = False):

		SfxSys.sounds[filename].play(-1 if loop else 0)
#7444
#Material System
import pygame
from logger import Log
import os.path

class MatSys:

	materials = {} # path (str) : image (Surface)
	@staticmethod
	def AddMaterial(filepath):
		Log.Message("Loading material " + filepath)
		try:
			try:
				blahblahblah = MatSys.materials[filepath]
			except KeyError:
				MatSys.materials[filepath] = pygame.image.load(os.path.join(os.path.dirname(__file__), filepath))
		except pygame.error:
			Log.Error("Material " + filepath + " not found!!")
			MatSys.materials[filepath] = pygame.image.load(os.path.join(os.path.dirname(__file__), "data/error.tga"))
	
	@staticmethod
	def GetMaterial(filepath):
		try:
			return MatSys.materials[filepath]
		except KeyError:
			Log.Warning("Material " + filepath + " is not loaded")
			MatSys.AddMaterial(filepath)
			return MatSys.materials[filepath]

	@staticmethod
	def RemoveAllMaterial():
		MatSys.materials.clear()

	@staticmethod
	def Init():
		Log.Message("Material system started")

	@staticmethod
	def Shutdown():
		MatSys.RemoveAllMaterial()

	@staticmethod
	def RotateAroundCenter(image, angle):
		orig_rect = image.get_rect()
		rot_image = pygame.transform.rotate(image, angle)
		rot_rect = orig_rect.copy()
		rot_rect.center = rot_image.get_rect().center
		rot_image = rot_image.subsurface(rot_rect).copy()
		return rot_image

	@staticmethod
	def RotateTexture(name, angle):
		if MatSys.materials[name]:
			MatSys.materials[name] = MatSys.RotateAroundCenter(MatSys.materials[name], angle)
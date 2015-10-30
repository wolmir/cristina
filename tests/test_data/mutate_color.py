import pygame

class MutateColor( pygame.Color ):
	COLOR_FACTOR = 85
	
	def sequence(self, color_seq):
		cnt_red = color_seq.count('R')
		cnt_green = color_seq.count('G')
		cnt_blue = color_seq.count('B')
		
		if( cnt_red == 1 and cnt_green == 1 and cnt_blue == 1 ):
			self.r = 255
			self.g = 255
			self.b = 0
			return self
			
		if( cnt_red == 2 and cnt_green == 1 ):
			self.r = 255
			self.g = 69
			self.b = 0
			return self
			
		self.r = (cnt_red * self.COLOR_FACTOR) % 256
		self.g = (cnt_green * self.COLOR_FACTOR) % 256
		self.b = (cnt_blue * self.COLOR_FACTOR) % 256
			
		return self
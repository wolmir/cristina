import pygame
from interpolator import *

class MutateSprite( pygame.sprite.Sprite ):
	def __init__( self, color=(255,255,255), pos=(0,0) ):
		pygame.sprite.Sprite.__init__( self )
		self.moveToSet = False
		self.scaleToSet = False
		self.origSize = (30, 30)
		self.flowerArg = None
		#self.imageMaster = pygame.Surface( self.origSize )
		#self.imageMaster.fill( color )
		#self.imageMaster.set_alpha(255)
		#self.image = self.imageMaster
		#
		#self.rect = self.image.get_rect()
		#self.rect.center = pos
		self.imageMaster = pygame.Surface( (1,1) )
		self.image = pygame.Surface( (1,1) )
		self.image.set_alpha(255)
		self.line = Interpolator( pos )
		self.alpha = Interpolator( self.image.get_alpha() )
		self.scale = Interpolator( self.origSize )
		
	def update( self ):
		#screen.fill( (0, 0, 0), self.rect )
		if self.line.next() == None:
			if self.moveToSet:
				#print "Arrived"
				self.moveToSet = False
				if self.moveToCallback:
					self.moveToCallback()
				if self.shouldKill:
					self.kill()
		else:
			self.rect.center = self.line.pos
		#screen.blit( self.image, self.rect )
		
		if self.alpha.next() != None:
		#	#print self.alpha.pos
			alpha, alpha = self.alpha.pos
			self.image.set_alpha( int(alpha) )
			
		#if self.scaleToSet:
		#	print "Set"
		#else:
		#	print "Not Set"
		if self.scale.next() == None:
			if self.scaleToSet:
				#print "Scaled"
				self.scaleToSet = False
				if self.scaleToCallback:
					if self.flowerArg:
						self.scaleToCallback(self.flowerArg)
					else:
						self.scaleToCallback()
		else:
			#oldPos = self.rect.center
			scaleX, scaleY = self.scale.pos
			self.image = pygame.transform.scale(self.imageMaster, (int(scaleX), int(scaleY)))
			self.rect = self.image.get_rect()
			self.rect.bottom = self.root_position.centery
			self.rect.centerx = self.root_position.centerx
			#print "check"
		#if self.scale.next() != None:
		#	#print self.alpha.pos
		#	scaleX, scaleY = self.scale.pos
		#	self.image = pygame.transform.scale(self.image, (int(scaleX), int(scaleY)))

	def moveTo(self, x, y, time, fps, callback=None, kill=False ):
		self.moveToSet = True
		self.moveToCallback = callback
		self.shouldKill = kill
		self.line = Interpolator(
									self.rect.center,
									(x, y),
									time,
									fps,
									1.0,
									0.5
									)
									
	def fadeTo(self, alpha, time, fps):
		#print self.image.get_alpha()
		self.alpha = Interpolator(
									(self.image.get_alpha(), self.image.get_alpha()),
									(alpha, alpha),
									time,
									fps,
									1.0,
									0.5
									)	

	def scaleTo( self, scaleX, scaleY, time, fps, callback=None, flowerArg=None):
		self.scaleToSet = True
		self.scaleToCallback = callback
		self.flowerArg = flowerArg
		self.scale = Interpolator(
									self.rect.size,
									(scaleX, scaleY),
									time,
									fps,
									1.0,
									0.5 )
		#print "here"

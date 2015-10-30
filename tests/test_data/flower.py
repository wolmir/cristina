import pygame, random

from albow.utils import blit_tinted
from albow.resource import get_image

from mutate_sprite import MutateSprite
from double_helix import Double_Helix
from mutate_color import MutateColor
from floating_text import FloatingText
from bloom_plus_one import BloomPlusOne
from bloom_minus_one import BloomMinusOne
from immune import Immune
import state
import game_screen


class Flower(MutateSprite):
	MAX_BLOOM_RADIUS = 30
	NORM_BLOOM_RADIUS = 20
	MIN_BLOOM_RADIUS = 10
	BLOOM_INCREMENT = 2

	MAX_PLANT_SIZE = (70, 100)
	NORM_PLANT_SIZE = (65, 100) #(55, 110) #(100,200)
	MIN_PLANT_SIZE = (50, 100)
	GROW_PLANT_SIZE = (25, 50)
	PLANT_SIZE_INCREMENT = 2

	COLOR_FACTOR = 85

	STEM_LENGTH_BASE = 30
	STEM_LENGTH_MIN_BASE = 15
	RED_STEM_LENGTH_FACTOR = 10
	GREEN_STEM_LENGTH_FACTOR = 25
	BLUE_STEM_LENGTH_FACTOR = -10

	LEAF_LENGTH_BASE = 20
	LEAF_WIDTH_BASE = 10
	RED_LEAF_REDUCTION_FACTOR = -8
	GREEN_LEAF_WIDTH_FACTOR = 8
	BLUE_LEAF_LENGTH_FACTOR = 10

	PHOTOSYNTHESIS_COLOR_RANGE = 50

	MAX_LIFE = MAX_BLOOM_RADIUS
	MIN_LIFE = MIN_BLOOM_RADIUS
	lifebarColor = (255,0,0)
	lifebarBorderColor = (255,255,255)

	def __init__(self, state_arg, player):
		MutateSprite.__init__( self )
		self.player = player
		self.mouseActive = False
		self.selected = False

		self.life = self.NORM_BLOOM_RADIUS
		self.dna = Double_Helix([ 'R','R','R','G','G','G','B','B','B','R','R','R']) 
		self.bloomCenter = pygame.Rect((15,15),(0,0))
		self.bloomRadius = self.NORM_BLOOM_RADIUS

		if self.player == state.PLAYER:
			self.stemColor = (0,255,0)
		else:
			self.stemColor = (0,255,255)

		self.stemLength = 75
		self.stemWidth = 6

		if self.player == state.PLAYER:
			self.leafColor = (0,255,0)
		else:
			self.leafColor = (0,255,255)

		self.leafWidth = 30
		self.leafLength = 30
		self.root_position = pygame.Rect((320,380), self.GROW_PLANT_SIZE)
		self.root_position_index_x = 0
		self.root_position_index_y = 0
		self.rootWidth = 25

		#Genomes
		self.bloomColor = MutateColor(255,255,255)
		self.sunColorBonus = MutateColor(255,255,255)
		self.rainColorBonus = MutateColor(255,255,255)
		self.pollinationBonus = 0

		self.fps = 30
		self.bloomPlusOne = BloomPlusOne( self.root_position.center ) 
		#FloatingText( MutateColor(0,0,0).sequence("RRR"), self.root_position.center )
		self.bloomMinusOne = BloomMinusOne( self.root_position.center ) 
		self.sunImmunity = Immune( self.root_position.center ) 
		#FloatingText( MutateColor(0,0,0).sequence("RRR"), self.root_position.center )
		self.pollinateBonus = FloatingText( MutateColor(0,0,0).sequence("RRR"), self.root_position.center )
		self.rainBloomReset = FloatingText( MutateColor(0,0,0).sequence("RRR"), self.root_position.center )
		self.messageSprites = pygame.sprite.OrderedUpdates()

		self.bloomImage = get_image("bloom.png").convert()
		self.bloomImage.set_colorkey((255,0,255))

		self.rect = self.root_position
		self.state = state_arg
		self.sequence_dna()

	def update(self, fps):
		MutateSprite.update(self)
		self.fps = fps
		self.messageSprites.update()
		#if pygame.mouse.get_pressed() == (1,0,0):
		#	if self.rect.collidepoint(pygame.mouse.get_pos()):
		#		self.mouseActive = True

		#if self.mouseActive == True:
		#	if pygame.mouse.get_pressed() == (0,0,0):
		#		self.mouseActive = False
		#		if self.rect.collidepoint(pygame.mouse.get_pos()):
		#			print "Clicked"
		#			self.selected = True
		#			self.redraw()

	def setPosition(self, row, column, pos ):
		self.root_position_index_x = row
		self.root_position_index_y = column
		self.root_position = pygame.Rect( pos, (0,0) )
		self.bloomPlusOne.rect = pygame.Rect( pos, (0,0) )
		self.redraw()

	def reset(self):
		self.sequence_dna()
		self.redraw()

	def redraw(self):
		size = self.rect.size

		SURFACE_WIDTH = 100
		SURFACE_HEIGHT = 150
		self.imageMaster = pygame.Surface((SURFACE_WIDTH, SURFACE_HEIGHT))
		self.bloomCenter.centerx = SURFACE_WIDTH / 2
		
		self.imageMaster.fill( (0,0,0) )
		self.imageMaster.set_colorkey( (0,0,0))
		
		root_pos = SURFACE_HEIGHT - 8

		#if self.selected:
		#	pygame.draw.rect(self.imageMaster, 
		#					 self.rainColorBonus, 
		#						( self.bloomCenter.centerx - ( self.rootWidth / 2), 
		#						root_pos,
		#						self.rootWidth, 
		#						self.rootWidth ) )

		#stem
		pygame.draw.rect(self.imageMaster, 
						 self.stemColor, 
							( self.bloomCenter.centerx - ( self.stemWidth / 2), 
							root_pos,
							self.stemWidth, 
							-self.stemLength ) )

		#right leaf
		pygame.draw.ellipse(self.imageMaster,
							self.leafColor,
								( self.bloomCenter.centerx + ( self.stemWidth / 2),
								root_pos - (self.stemLength / 2) - (self.leafWidth / 2),
								self.leafLength,
								self.leafWidth ))

		#right leaf
		pygame.draw.ellipse(self.imageMaster,
							(255,255,255),
								( self.bloomCenter.centerx + ( self.stemWidth / 2),
								root_pos - (self.stemLength / 2) - (self.leafWidth / 2),
								self.leafLength,
								self.leafWidth ),
							2)

		#left leaf
		pygame.draw.ellipse(self.imageMaster,
							self.leafColor,
								( self.bloomCenter.centerx - ( self.stemWidth / 2) - self.leafLength,
								root_pos - (self.stemLength / 2) - (self.leafWidth / 2),
								self.leafLength,
								self.leafWidth ))

		#left leaf outline
		pygame.draw.ellipse(self.imageMaster,
							(255,255,255),
								( self.bloomCenter.centerx - ( self.stemWidth / 2) - self.leafLength,
								root_pos - (self.stemLength / 2) - (self.leafWidth / 2),
								self.leafLength,
								self.leafWidth ),
							2)

		##sun Bonus
		pygame.draw.circle(self.imageMaster, 
						   self.sunColorBonus, 
						   (self.bloomCenter.centerx, root_pos - self.stemLength),
						   self.bloomRadius + 5 )

		#BLOOM_SURFACE_WIDTH = self.MAX_BLOOM_RADIUS
		#BLOOM_SURFACE_HEIGHT = self.MAX_BLOOM_RADIUS
		#self.bloomMaster = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
		#self.bloomMaster.fill((255,0,255))
		#self.bloomMaster.set_colorkey((255,0,255))
		#blit_tinted( self.bloomMaster, 
		#	  self.bloomImage, 
		#	  (0, 0), 
		#	  (self.bloomColor.r, self.bloomColor.g, self.bloomColor.b ) )

		#self.bloomMaster = pygame.transform.scale( self.bloomMaster, (self.bloomRadius, self.bloomRadius))

		#self.imageMaster.blit( self.bloomMaster, (0, 0) )

		#bloom
		pygame.draw.circle(self.imageMaster, 
						   self.bloomColor, 
						   (self.bloomCenter.centerx, root_pos - self.stemLength),
						   self.bloomRadius )

		#bloom outline
		pygame.draw.circle(self.imageMaster, 
						   (255,255,255), 
						   (self.bloomCenter.centerx, root_pos - self.stemLength),
						   self.bloomRadius,
						   2 )

		#stamen
		#if( self.pollinationBonus > 0 ):
		#	pygame.draw.circle(self.imageMaster, 
		#					   (255,255,255), 
		#					   (self.bloomCenter.centerx, (root_pos - self.stemLength) - 5),
		#					   self.bloomRadius/5)
		#if( self.pollinationBonus > 1 ):
		#	pygame.draw.circle(self.imageMaster, 
		#					   (255,255,255), 
		#					   (self.bloomCenter.centerx + 5, (root_pos - self.stemLength) + 5),
		#					   self.bloomRadius/5)
		#if( self.pollinationBonus > 2 ):
		#	pygame.draw.circle(self.imageMaster, 
		#					   (255,255,255), 
		#					   (self.bloomCenter.centerx - 5, (root_pos - self.stemLength) + 5),
		#					   self.bloomRadius/5)


		#life bar
		LIFEBAR_SURFACE_WIDTH = 50
		LIFEBAR_SURFACE_HEIGHT = 10
		LIFEBAR_POS_X = 25

		pygame.draw.rect(self.imageMaster, 
		                 self.lifebarColor, 
		                    ( LIFEBAR_POS_X, (root_pos - self.stemLength - (self.bloomRadius * 2)), 
		                     LIFEBAR_SURFACE_WIDTH * ((self.life-self.MIN_LIFE) / float(self.MAX_LIFE-self.MIN_LIFE))+5,
		                    LIFEBAR_SURFACE_HEIGHT ))

		pygame.draw.rect(self.imageMaster, 
		                 self.lifebarBorderColor, 
		                    ( LIFEBAR_POS_X, (root_pos - self.stemLength - (self.bloomRadius * 2)), 
		                    LIFEBAR_SURFACE_WIDTH, 
		                    LIFEBAR_SURFACE_HEIGHT ), 
		                 2)

		#Selected
		if self.selected:
			pygame.draw.rect(self.imageMaster, 
							 (255,255,255), 
							 ((0,0),(SURFACE_WIDTH-2, SURFACE_HEIGHT-2)), 
							 2)
		
		self.image = pygame.transform.scale( self.imageMaster, size)

		self.rect = self.image.get_rect()  #
		#self.rect.top = 10

		self.rect.bottom = self.root_position.centery
		self.rect.centerx = self.root_position.centerx

	def rotate_dna_left(self):
		self.dna.rotate_left()
		self.sequence_dna()

	def rotate_dna_right(self):
		self.dna.rotate_right()
		self.sequence_dna()

	def swap_dna_pair_1(self):
		self.dna.swap_pair_1()
		self.sequence_dna()

	def swap_dna_pair_2(self):
		self.dna.swap_pair_2()
		self.sequence_dna()

	def random_dna_mutation(self, nucleobases):
		self.dna.random_mutation(nucleobases);
		self.sequence_dna()

	def sequence_gene_1(self):
		gene_1 = self.dna[0:3]
		self.bloomColor.sequence(gene_1)

	def sequence_gene_2(self):
		gene_2 = self.dna[3:6]
		#print gene_2
		cnt_red_genes = gene_2.count('R')
		cnt_green_genes = gene_2.count('G')
		cnt_blue_genes = gene_2.count('B')
		#print "red: " + str(cnt_red_genes)
		#print "green: " + str(cnt_green_genes)
		#print "blue: " + str(cnt_blue_genes)
		red_length = cnt_red_genes * self.RED_STEM_LENGTH_FACTOR
		green_length = cnt_green_genes * self.GREEN_STEM_LENGTH_FACTOR
		blue_length = cnt_blue_genes * self.BLUE_STEM_LENGTH_FACTOR
		#print str(red_length) + " " + str(green_length) + " " + str(blue_length)
		stem_length = self.STEM_LENGTH_BASE
		stem_length += red_length
		stem_length += green_length
		stem_length += blue_length
		#print stem_length
		if(stem_length < self.STEM_LENGTH_MIN_BASE):
			stem_length = self.STEM_LENGTH_MIN_BASE
		self.stemLength = stem_length

		self.rainColorBonus.sequence(gene_2)


	def sequence_gene_3(self):
		gene_3 = self.dna[6:9]
		#print gene_3
		cnt_red_genes = gene_3.count('R')
		cnt_green_genes = gene_3.count('G')
		cnt_blue_genes = gene_3.count('B')
		red_leaf_reduction_factor = cnt_red_genes * self.RED_LEAF_REDUCTION_FACTOR
		green_leaf_width = cnt_green_genes * self.GREEN_LEAF_WIDTH_FACTOR
		blue_leaf_length = cnt_blue_genes * self.BLUE_LEAF_LENGTH_FACTOR
		#print str(red_leaf_reduction_factor) + " " + str(green_leaf_width) + " " + str(blue_leaf_length)
		leaf_length = self.LEAF_LENGTH_BASE
		leaf_length += (blue_leaf_length - red_leaf_reduction_factor)
		self.leafLength = leaf_length
		#print leaf_length
		leaf_width = self.LEAF_WIDTH_BASE
		leaf_width += (green_leaf_width - red_leaf_reduction_factor)
		self.leafWidth = leaf_width
		#print leaf_width

		self.sunColorBonus.sequence(gene_3)

	def sequence_gene_4(self):
		gene_4 = self.dna[9:12]
		gene_1 = self.dna[0:3]

		#print gene_4
		#print gene_1
		#print

		self.pollinationBonus = 0

		if gene_4[2] == gene_1[0]:
			self.pollinationBonus += 1
		if gene_4[1] == gene_1[1]:
			self.pollinationBonus += 1
		if gene_4[0] == gene_1[2]:
			self.pollinationBonus += 1

	def sequence_dna(self):
		self.sequence_gene_1()
		self.sequence_gene_2()
		self.sequence_gene_3()
		self.sequence_gene_4()

		self.redraw()
		
	def pollinate(self):
		#print "Pollinate +1"
		numPollinate = self.pollinationBonus + 1
		self.pollinateBonus.setText( "Pollinate +" + str(numPollinate), self.bloomColor )
		self.pollinateBonus.rect.center = self.rect.center
		self.messageSprites.add( self.pollinateBonus )
		self.pollinateBonus.moveTo(self.pollinateBonus.rect.centerx, self.pollinateBonus.rect.centery - 100, 
								   4, self.fps, kill=True)
		self.pollinateBonus.fadeTo(0, 4, self.fps)

	def water(self, rain):
		self.redraw()
		#if self.bloomRadius > self.NORM_BLOOM_RADIUS:
			#print "UNBLOOM"
			#self.rainBloomReset.setText( "UNBLOOM", rain.color )
			#self.rainBloomReset.rect.center = self.rect.center
			#self.messageSprites.add( self.rainBloomReset )
			#self.rainBloomReset.moveTo(self.rainBloomReset.rect.centerx, 
			#						   self.rainBloomReset.rect.centery - 100, 
			#						   4, self.fps, kill=True)
			#self.rainBloomReset.fadeTo(0, 3, self.fps)
			#self.bloomRadius = self.NORM_BLOOM_RADIUS
			#self.redraw()    
		#if self.rainColorBonus == rain.color:
		#	if self.rect.size < self.MAX_PLANT_SIZE:
		#		self.rect.width += self.PLANT_SIZE_INCREMENT
		#		self.rect.height += self.PLANT_SIZE_INCREMENT
		#		self.redraw() 
		#else:
		#	if self.rect.size > self.MIN_PLANT_SIZE:
		#		self.rect.width -= self.PLANT_SIZE_INCREMENT
		#		self.rect.height -= self.PLANT_SIZE_INCREMENT
		#		self.redraw() 

	def photosynthesis(self, sun):
		if sun.color == self.bloomColor:
			if self.bloomRadius + self.BLOOM_INCREMENT < self.MAX_BLOOM_RADIUS:
				self.bloomPlusOne.image.set_alpha(255)
				self.bloomPlusOne.rect.left = self.rect.left 
				self.bloomPlusOne.rect.centery = self.rect.centery
				self.messageSprites.add( self.bloomPlusOne )
				self.bloomPlusOne.moveTo(self.bloomPlusOne.rect.centerx, self.bloomPlusOne.rect.centery - 100, 4, self.fps, kill=True)
				self.bloomPlusOne.fadeTo(0, 3, self.fps)
				self.bloomRadius += self.BLOOM_INCREMENT
				self.life = self.bloomRadius
				self.redraw()
		elif sun.color == self.sunColorBonus:
			self.sunImmunity.image.set_alpha(255)
			self.sunImmunity.rect.left = self.rect.left 
			self.sunImmunity.rect.centery = self.rect.centery
			self.messageSprites.add( self.sunImmunity )
			self.sunImmunity.moveTo(self.sunImmunity.rect.centerx, self.sunImmunity.rect.centery - 100, 4, self.fps, kill=True)
			self.sunImmunity.fadeTo(0, 3, self.fps)
		else:
			if self.bloomRadius == self.MIN_BLOOM_RADIUS:
				width, height = self.GROW_PLANT_SIZE
				self.scaleTo( width, height, 1, self.fps, self.state.flowerDied, self )
			if self.bloomRadius - self.BLOOM_INCREMENT >= self.MIN_BLOOM_RADIUS: 
				self.bloomMinusOne.image.set_alpha(255)
				self.bloomMinusOne.rect.left = self.rect.left
				self.bloomMinusOne.rect.centery = self.rect.centery
				self.messageSprites.add( self.bloomMinusOne )
				self.bloomMinusOne.moveTo(self.bloomMinusOne.rect.centerx, self.bloomMinusOne.rect.centery - 100, 4, self.fps, kill=True)
				self.bloomMinusOne.fadeTo(0, 3, self.fps)
				self.bloomRadius -= self.BLOOM_INCREMENT
				self.life = self.bloomRadius
				self.redraw()

	def take_damage(self, damage):
		if( (self.life - damage) < 0 ):
			self.life = 0
		else:
			self.life -= damage

	def heal(self, heal_amt):
		if( (self.life + heal_amt) > 100 ):
			self.life = 100
		else:
			self.life += heal_amt

	def randomize_dna(self):
		self.dna = Double_Helix()
		for i in range(12):
			self.dna.append( random.choice( game_screen.NUCLEOBASES ) )
		self.sequence_dna()

	def setDNA(self, dna ):
		self.dna = dna
		self.sequence_dna()

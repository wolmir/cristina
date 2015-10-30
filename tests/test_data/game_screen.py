from humerus.main_commands import MainCommandScreen
from albow.controls import Label
from albow.controls import Button, ImageButton
from albow.resource import get_image, resource_path
#from albow.utils import blit_in_rect

import pygame
from nucleobase_label import Nucleobase_Label
from mutate_color import MutateColor
from state import *

SWAP_BUTTON_WIDTH = 50
spaceX = 85#100
spaceY = 20
gapY = 65 #50

class Mutate_GameScreen(MainCommandScreen):
	bg_color = (0,0,0)
	currentDNA_Labels = list()
	GENOME_MENU_X = 700#675
	GENOME_MENU_Y = 150

	def __init__(self, shell):
		MainCommandScreen.__init__(self, shell)
		self.shell = shell
		self.clock = pygame.time.Clock()

		self.grass = get_image("GrassArea.png").convert()
		self.grass.set_colorkey( (255,0,255) )

		self.sky = get_image("sky.png").convert()

		self.controlPanel = get_image("controlPanel.png").convert()

		self.forecast_bar = get_image("forecast_bar.png").convert()

		self.genome_top = get_image("rotate.png").convert()
		self.genome_top.set_colorkey((255,0,255))

		self.genome_cross = get_image("cross.png").convert()
		self.genome_cross.set_colorkey((255,0,255))

		self.genome_bottom = pygame.transform.flip( self.genome_top, False, True )
		#self.genome_bottom = get_image("genome_bottom.gif", noalpha=True)
		#self.genome_bottom = self.genome_bottom.convert()

		font = pygame.font.SysFont("", 30)
		self.game_over = font.render("GAME OVER", 1, (255,255,0))

	def init_MenuControls(self):
		#dna_lbl = Label("DNA:   " + "    ".join(map(str, self.flower.dna)))
		#dna_lbl.rect.topleft = (0, 0)
		#self.dna_lbl = dna_lbl
		#self.add( dna_lbl )

		self.bloomIconImage = get_image("bloom_icon.png").convert()
		self.bloomIconImage.set_colorkey((255,0,255))

		self.immuneIconImage = get_image("immune_icon.png").convert()
		self.immuneIconImage.set_colorkey((255,0,255))

		#self.crossImage = get_image("cross.png").convert()
		#self.crossImage.set_colorkey((255,0,255))

		#self.rotateRightDownImage = get_image("rotate.png").convert()
		#self.rotateRightDownImage.set_colorkey((255,0,255))
		#self.rotateRightUpImage = pygame.transform.flip( self.rotateRightDownImage, False, True )
		#self.rotateLeftDownImage = pygame.transform.flip( self.rotateRightDownImage, True, False )
		#self.rotateLeftUpImage = pygame.transform.flip( self.rotateRightDownImage, True, True )

		rotate_dna_left_btn = Button("---->", self.rotate_flower_left )
		rotate_dna_left_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y-50)
		self.add(rotate_dna_left_btn)

		rotate_dna_right_btn = Button("<----", self.rotate_flower_right )
		rotate_dna_right_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+180)
		self.add(rotate_dna_right_btn)

		self.randomImage = get_image("random.png").convert()
		self.randomImage.set_colorkey((255,0,255))
		random_mutation_btn = Button("", self.random_flower_mutation )
		random_mutation_btn.width = SWAP_BUTTON_WIDTH
		random_mutation_btn.rect.topleft = (self.GENOME_MENU_X+10, self.GENOME_MENU_Y-80)
		self.add(random_mutation_btn)

		self.swapImage = get_image("swap.png").convert()
		self.swapImage.set_colorkey((255,0,255))
		swap_pair_1_btn = Button("<-->", self.swap_flower_pair_1 )
		swap_pair_1_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_1_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y-15)
		self.add(swap_pair_1_btn)

		swap_pair_2_btn = Button("<-->", self.swap_flower_pair_2 )
		swap_pair_2_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_2_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+10)
		self.add(swap_pair_2_btn)

		swap_pair_3_btn = Button("<-->", self.swap_flower_pair_3 )
		swap_pair_3_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_3_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+35)
		self.add(swap_pair_3_btn)

		swap_pair_4_btn = Button("<-->", self.swap_flower_pair_4 )
		swap_pair_4_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_4_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+110)
		self.add(swap_pair_4_btn)

		swap_pair_5_btn = Button("<-->", self.swap_flower_pair_5 )
		swap_pair_5_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_5_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+135)
		self.add(swap_pair_5_btn)

		swap_pair_6_btn = Button("<-->", self.swap_flower_pair_6 )
		swap_pair_6_btn.width = SWAP_BUTTON_WIDTH
		swap_pair_6_btn.rect.topleft = (self.GENOME_MENU_X+20, self.GENOME_MENU_Y+160)
		self.add(swap_pair_6_btn)

		#health_lbl = Label("Life: " + str(self.flower.life) )
		#health_lbl.rect.topleft = (180, 80)
		#self.health_lbl = health_lbl
		#self.add(health_lbl)

		#decrease_health_btn = Button("Decrease Health", self.decrease_flower_health )
		#decrease_health_btn.rect.topleft = (0, 80)
		#self.add(decrease_health_btn)

		#increase_health_btn = Button("Increase Health", self.increase_flower_health )
		#increase_health_btn.rect.topleft = (300, 80)
		#self.add(increase_health_btn)

	def init_FlowerDNA_labels(self):
		startX = self.GENOME_MENU_X
		startY = self.GENOME_MENU_Y
		spaceX = 85#100
		spaceY = 20
		gapY = 65 #50
		
		state = self.shell.game.state

		for nucleobase_index in range(6):
			flower_nucleobase_lbl = Nucleobase_Label(state.next_flower_dna[nucleobase_index], nucleobase_index)
			if( state.next_flower_dna[nucleobase_index] == 'R' ):
				flower_nucleobase_lbl.bg_color = (255,0,0)
			elif( state.next_flower_dna[nucleobase_index] == 'G' ):
				flower_nucleobase_lbl.bg_color = (0,255,0)
			elif( state.next_flower_dna[nucleobase_index] == 'B' ):
				flower_nucleobase_lbl.bg_color = (0,0,255)

			if( nucleobase_index < 3 ):
				flower_nucleobase_lbl.rect.center = (startX, startY + (spaceY * nucleobase_index))
			elif( nucleobase_index < 6 ):
				flower_nucleobase_lbl.rect.center = (startX + spaceX, startY + (spaceY * nucleobase_index) + gapY)
			self.currentDNA_Labels.append( flower_nucleobase_lbl )
			self.add( flower_nucleobase_lbl )

		END_START = 11
		for nucleobase_index in range(11,5,-1):
			flower_nucleobase_lbl = Nucleobase_Label(state.next_flower_dna[nucleobase_index], nucleobase_index)
			if( state.next_flower_dna[nucleobase_index] == 'R' ):
				flower_nucleobase_lbl.bg_color = (255,0,0)
			elif( state.next_flower_dna[nucleobase_index] == 'G' ):
				flower_nucleobase_lbl.bg_color = (0,255,0)
			elif( state.next_flower_dna[nucleobase_index] == 'B' ):
				flower_nucleobase_lbl.bg_color = (0,0,255)

			if( nucleobase_index >= 9 ):
				flower_nucleobase_lbl.rect.center = (startX + spaceX, startY + (spaceY * (END_START - nucleobase_index)))
			if( nucleobase_index < 9 ):
				flower_nucleobase_lbl.rect.center = (startX, startY + (spaceY * (END_START - nucleobase_index))+ gapY)

			self.currentDNA_Labels.append( flower_nucleobase_lbl )
			self.add( flower_nucleobase_lbl )

		#self.pollinationBonus_lbl = Label("Bonus: " + str(self.getPollinationBonus(state)))
		#self.pollinationBonus_lbl.rect.topleft = ( self.GENOME_MENU_X, self.GENOME_MENU_Y-100)
		#self.add( self.pollinationBonus_lbl )

		numPlayerFlowers, numRivalFlowers = state.getNumFlowers()

		self.playerFlowerCount_lbl = Label("Player: " + str(numPlayerFlowers), 100)
		self.playerFlowerCount_lbl.rect.topleft = ( self.GENOME_MENU_X, self.GENOME_MENU_Y-140)
		self.add( self.playerFlowerCount_lbl )

		self.rivalFlowerCount_lbl = Label("Rival: " + str(numRivalFlowers), 100)
		self.rivalFlowerCount_lbl.rect.topleft = ( self.GENOME_MENU_X, self.GENOME_MENU_Y-120)
		self.add( self.rivalFlowerCount_lbl )

	def getPollinationBonus(self, state):
			gene_4 = state.next_flower_dna[9:12]
			gene_1 = state.next_flower_dna[0:3]

			#print gene_4
			#print gene_1
			#print

			pollinationBonus = 0

			if gene_4[2] == gene_1[0]:
				pollinationBonus += 1
			if gene_4[1] == gene_1[1]:
				pollinationBonus += 1
			if gene_4[0] == gene_1[2]:
				pollinationBonus += 1
			return pollinationBonus

	def update_flower_dna(self):
		state = self.shell.game.state
		for nucleobase_index in range(12):

			self.currentDNA_Labels[ nucleobase_index ].text = state.next_flower_dna[ self.currentDNA_Labels[ nucleobase_index ].index ]
			
			if( state.next_flower_dna[nucleobase_index] == 'R' ):
				self.currentDNA_Labels[ self.currentDNA_Labels[ nucleobase_index ].index ].bg_color = (255,0,0)
			elif( state.next_flower_dna[nucleobase_index] == 'G' ):
				self.currentDNA_Labels[ self.currentDNA_Labels[ nucleobase_index ].index ].bg_color = (0,255,0)
			elif( state.next_flower_dna[nucleobase_index] == 'B' ):
				self.currentDNA_Labels[ self.currentDNA_Labels[ nucleobase_index ].index ].bg_color = (0,0,255)

		#self.pollinationBonus_lbl.text = "Bonus: " + str(self.getPollinationBonus(state))

	def rotate_flower_left(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.rotate_left()
			self.update_flower_dna()
			state.end_turn()

	def rotate_flower_right(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.rotate_right()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_1(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_1()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_2(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_2()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_3(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_3()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_4(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_4()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_5(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_5()
			self.update_flower_dna()
			state.end_turn()

	def swap_flower_pair_6(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.swap_pair_6()
			self.update_flower_dna()
			state.end_turn()

	def random_flower_mutation(self):
		state = self.shell.game.state
		if state.state == CHANGE_DNA and state.isAbleToSpawn():
			state.state = SPAWN_PLANTS
			state.next_flower_dna.random_mutation( list(NUCLEOBASES) )
			self.update_flower_dna()
			state.end_turn()

	#def increase_flower_health(self):
	#    state = self.shell.game.state
	#    state.currentFlower.heal(10)
	#    state.currentFlower.redraw()
	#    self.health_lbl.text = "Life: " + str(self.currentFlower.life) 

	#def decrease_flower_health(self):
	#    state = self.shell.game.state
	#    state.currentFlower.take_damage(10)
	#    state.currentFlower.redraw()
	#    self.health_lbl.text = "Life: " + str(self.currentFlower.life) 

	def enter_screen(self):	
		#for x in range(len(self.subwidgets)):
		#	self.subwidgets.pop()
		self.subwidgets = []
		self.currentDNA_Labels = []

		self.init_MenuControls()
		self.init_FlowerDNA_labels()

		self.update_flower_dna()
		fps_lbl = Label("FPS: ")
		fps_lbl.rect.topleft = (0,0)
		self.add( fps_lbl )
		self.fps_lbl = fps_lbl

	def begin_frame(self):
		self.clock.tick()
		self.fps_lbl.text = str(int(self.clock.get_fps()))

		state = self.shell.game.state
		numPlayerFlowers, numRivalFlowers = state.getNumFlowers()

		self.playerFlowerCount_lbl.text = "Player: " + str(int(numPlayerFlowers))
		self.rivalFlowerCount_lbl.text = "Rival: " + str(int(numRivalFlowers))

		self.update_flower_dna()

		self.invalidate()

	def draw(self, surface):
		state = self.shell.game.state

		surface.blit(self.sky, (0,0))
		state.sun_sprites.draw(surface)
		surface.blit(self.grass, (0,0))
		#state.rain.rain.draw(surface)
		state.cloud_sprites.draw(surface)
		surface.blit(self.controlPanel, (650,0))

		surface.blit(self.bloomIconImage, (self.GENOME_MENU_X-40, self.GENOME_MENU_Y-10))
		surface.blit(self.immuneIconImage, (self.GENOME_MENU_X-35, self.GENOME_MENU_Y+110))

		swapOffset = 15

		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y-15))
		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y+10))
		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y+35))
		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y+110))
		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y+135))
		surface.blit(self.swapImage, (self.GENOME_MENU_X+swapOffset, self.GENOME_MENU_Y+160))

		surface.blit(self.randomImage, (self.GENOME_MENU_X+15, self.GENOME_MENU_Y-80))

		#surface.blit(self.crossImage, (self.GENOME_MENU_X+25, self.GENOME_MENU_Y+gapY))

		#surface.blit(self.rotateRightDownImage, (self.GENOME_MENU_X, self.GENOME_MENU_Y-40))
		#surface.blit(self.rotateLeftDownImage, (self.GENOME_MENU_X+spaceX-20, self.GENOME_MENU_Y-40))

		#surface.blit(self.rotateRightUpImage, (self.GENOME_MENU_X+15, self.GENOME_MENU_Y+gapY-11))
		#surface.blit(self.rotateLeftUpImage, (self.GENOME_MENU_X+spaceX-2, self.GENOME_MENU_Y+gapY-40))

		#surface.blit(self.rotateRightDownImage, (self.GENOME_MENU_X, self.GENOME_MENU_Y+gapY+30))
		#surface.blit(self.rotateLeftDownImage, (self.GENOME_MENU_X+spaceX-20, self.GENOME_MENU_Y+gapY+30))

		#surface.blit(self.rotateRightUpImage, (self.GENOME_MENU_X, self.GENOME_MENU_Y+160))
		#surface.blit(self.rotateLeftUpImage, (self.GENOME_MENU_X+spaceX-20, self.GENOME_MENU_Y+160))

		#surface.blit(self.rotateRightUpImage, (self.GENOME_MENU_X, self.GENOME_MENU_Y+160))
		#surface.blit(self.rotateLeftUpImage, (self.GENOME_MENU_X+spaceX-20, self.GENOME_MENU_Y+160))
		#(self.GENOME_MENU_X+20, self.GENOME_MENU_Y+190)

		surface.blit(self.forecast_bar, (0,500))		

		surface.blit(self.genome_top, (self.GENOME_MENU_X+5, self.GENOME_MENU_Y-40))
		surface.blit(self.genome_cross, (self.GENOME_MENU_X+10, self.GENOME_MENU_Y+50))
		surface.blit(self.genome_bottom, (self.GENOME_MENU_X+5, self.GENOME_MENU_Y+175))
		state.currentDay.draw( surface )
		state.flowers.draw(surface)

		#state.bug_sprites.draw(surface)

		for sprite in state.flowers:
			sprite.messageSprites.draw( surface )

		#state.grid.draw( surface )

		daysToDisplay = 0
		if len(state.days) > 14:
			daysToDisplay = 14
		else:
			daysToDisplay = len(state.days)

		for i in range(daysToDisplay):
			surface.blit( state.days[i].getIcon(), (((state.days[i].iconSize + 5) * i), self.bottom - state.days[i].iconSize))

		if state.is_completed:
			surface.blit( self.game_over, (500,300))


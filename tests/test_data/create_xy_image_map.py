'''Game main module.

Contains the entry point used by the run_game.py script.

'''

#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon

import g
import data
import maps

import sys
import pygame
import time

def main():
	data.trace("started main")
	pygame.init()
	pygame.font.init()
	
	pygame.display.set_caption("The Mimic Slime and the Forbidden Dungeon")
	g.simpleFont = pygame.font.Font(data.filepath("vera.ttf"), 8)

	data.trace("reading "+str(len(sys.argv)-1)+" arguments")

	data.trace("creating screen")
	g.screen = pygame.display.set_mode(g.screen_size)

	data.trace("loading images")
	if not data.loadImages():
		return

	for i in range((g.images["base.png"].get_size()[1])/32):
		for j in range((g.images["base.png"].get_size()[0])/32):
			tempSurface = g.simpleFont.render(str(j)+", "+str(i), False,
			(255,255,255))
			g.images["base.png"].blit(tempSurface, (j*32, i*32))
	pygame.image.save(g.images["base.png"], "base_with_xy.png")
	data.trace("complete!")

main()
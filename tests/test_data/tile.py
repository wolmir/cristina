'''Game tile module.

Contains per-tile code

'''
#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon

import g
import data

import os

tileTypes = {}

def loadTileTypes():
	global tileTypes
	tileTypes = {}
	tileDir = (os.path.join(data.data_dir, "tiletypes"))
	for filename in os.listdir(tileDir):
		if filename[-3:].lower() != "txt": continue
		data.trace("  loading "+filename)
		tileTypes[filename] = tile_style(filename)
	
	return True


class tile_style:
	def __init__(self, filename):
		self.name = filename
		self.walkable = True
		self.picture = ["base.png", 0, 0]
		self.canEat = False
		self.armor = 0
		self.replace = "replacethis.txt"
		self.symbol="_"
		rawdata = data.loadText(os.path.join("tiletypes",filename))
		for line in rawdata:
			splitLine = line.split("=", 1)
			if len(splitLine) < 2:
				data.warn("could not understand: "+line)
				continue
			splitLine[0] = splitLine[0].strip().lower()
			splitLine[1] = splitLine[1].strip()
			if splitLine[0] == "walkable":
				self.walkable = data.strToBool(splitLine[1])
				if self.walkable == None:
					self.walkable = False
					data.warn("walkable not true or false: "+line)
			elif splitLine[0] == "tile":
				tilePointer = splitLine[1].split(" ", 2)
				if len(tilePointer) < 3:
					data.warn("not enough information: "+line)
					continue
				self.picture[0] = tilePointer[0].strip()
				try:
					self.picture[1] = int(tilePointer[1])
					self.picture[2] = int(tilePointer[2])
				except ValueError:
					data.warn("xy coords not a number: "+line)
					continue
			elif splitLine[0] == "caneat":
				self.canEat = data.strToBool(splitLine[1])
				if self.canEat == None:
					self.canEat = False
					data.warn("canEat not true or false: "+line)
			elif splitLine[0] == "armor":
				self.armor = data.strToInt(splitLine[1])
				if self.armor == None:
					self.armor = 0
					data.warn("armor not a number: "+line)
			elif splitLine[0] == "replace":
				self.replace = splitLine[1]
			elif splitLine[0] == "symbol":
				if len(splitLine[1]) != g.symbolLength:
					data.warn("symbol wrong length: "+line)
					continue
				self.symbol=splitLine[1]
			else:
				data.warn("I don't understand: "+line)
				
		data.trace("    name: "+self.name)
		data.trace("    walkable: "+str(self.walkable))
		data.trace("    picture: "+repr(self.picture))
		data.trace("    canEat: "+str(self.canEat))
		data.trace("    armor: "+str(self.armor))
		data.trace("    replace: "+self.replace)


class tile:
	def __init__(self, style):
		self.style = style
		self.image = style.picture
		self.enemyPlaced = False
		

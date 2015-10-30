'''Game creature module.

Contains creature code

'''
#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon

import g
import data

import os

statTypes = {}
#attack, hp, powers
statTypes["animal"] = [3, 50, ["bite.txt"]]
statTypes["melee"] = [5, 100, ["sword.txt"]]
statTypes["range"] = [5, 80, ["arrow.txt"]]
statTypes["dragon"] = [5, 120, ["firebreath.txt"]]
statTypes["icedragon"] = [5, 120, ["icebreath.txt"]]

creatureTypes = {}

def loadCreatures():
	global creatureTypes
	creatureTypes = {}
	creatureDir = (os.path.join(data.data_dir, "creatures"))
	for filename in os.listdir(creatureDir):
		if filename[-3:].lower() != "txt": continue
		data.trace("  loading "+filename)
		creatureTypes[filename] = creature_style(filename)
	
	return True


class creature_style:
	def __init__(self, filename):
		self.name = filename
		self.picture = ["base.png", 0, 0]
		self.statType = "melee"
		self.statStrength = 1
		self.symbol="?"
		self.levelRange = [1, 1]
		rawdata = data.loadText(os.path.join("creatures",filename))
		for line in rawdata:
			splitLine = line.split("=", 1)
			if len(splitLine) < 2:
				data.warn("could not understand: "+line)
				continue
			splitLine[0] = splitLine[0].strip().lower()
			splitLine[1] = splitLine[1].strip()
			if splitLine[0] == "tile":
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
					self.picture[1] = 0
					self.picture[2] = 0
					continue
			elif splitLine[0] == "symbol":
				if len(splitLine[1]) != g.symbolLength:
					data.warn("symbol wrong length: "+line)
					continue
				self.symbol=splitLine[1]
			elif splitLine[0] == "stats":
				statPointer = splitLine[1].split(" ", 1)
				if len(statPointer) < 2:
					data.warn("not enough information: "+line)
					continue
				self.statType = statPointer[0]
				if not self.statType in statTypes:
					data.warn("stat type does not exist: "+line)
					continue
				try:
					self.statStrength = int(statPointer[1])
				except ValueError:
					data.warn("stat strength not a number: "+line)
					self.statStrength = 1
					continue
			elif splitLine[0] == "level":
				statPointer = splitLine[1].split("-", 1)
				if len(statPointer) < 2:
					data.warn("not enough information: "+line)
					continue
				try:
					self.levelRange[0] = int(statPointer[0])
					self.levelRange[1] = int(statPointer[1])
				except ValueError:
					data.warn("level range not a number: "+line)
				
			else:
				data.warn("I don't understand: "+line)
				
		data.trace("    name: "+self.name)
		data.trace("    picture: "+repr(self.picture))

class creature:
	def __init__(self, creatureType, level, xy):
		self.creatureType = creatureType
		self.xy = xy
		self.aware = False
		self.level = level
		tempStats = statTypes[creatureType.statType]
		self.powers = tempStats[2]
		self.attack = tempStats[0]*int(1+creatureType.statStrength/5.0+self.level/5.0)
		self.maxhp = tempStats[1]*int(1+creatureType.statStrength/5.0+self.level/5.0)
		self.hp = self.maxhp

	def attackCreature(self, attackStrength):
		self.hp -= attackStrength
		if self.hp <= 0:
			return False
		return True
		



	
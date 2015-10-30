'''Game powers module.

Contains code for the powers

'''
#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon

import g
import data

import os


powerTypes = {}

def loadPowers():
	global powerTypes
	powerTypes = {}
	powerDir = (os.path.join(data.data_dir, "powers"))
	for filename in os.listdir(powerDir):
		if filename[-3:].lower() != "txt": continue
		data.trace("  loading "+filename)
		powerTypes[filename] = power_style(filename)
	
	return True


class power_style:
	def __init__(self, filename):
		self.name = filename
		self.title = ""
		self.tile = ["base.png", 0, 0]
		self.powerRange = 1
		self.damage = 1
		rawdata = data.loadText(os.path.join("powers",filename))
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
				self.tile[0] = tilePointer[0].strip()
				try:
					self.tile[1] = int(tilePointer[1])
					self.tile[2] = int(tilePointer[2])
				except ValueError:
					data.warn("xy coords not a number: "+line)
					self.tile[1] = 0
					self.tile[2] = 0
					continue
			elif splitLine[0] == "name":
				self.title=splitLine[1]
			elif splitLine[0] == "range":
				try:
					self.powerRange = int(splitLine[1])
				except ValueError:
					data.warn("power range not a number: "+line)
					self.powerRange = 1
					continue
			elif splitLine[0] == "damage":
				try:
					self.damage = int(splitLine[1])
				except ValueError:
					data.warn("damage not a number: "+line)
					self.damage = 1
					continue
			else:
				data.warn("I don't understand: "+line)
				
		data.trace("    name: "+self.name)
		data.trace("    title: "+self.title)
		data.trace("    tile: "+repr(self.tile))
		data.trace("    range: "+repr(self.powerRange))
		data.trace("    damage: "+repr(self.damage))

class power:
	def __init__(self, powerType, level):
		self.powerType = powerType
		self.level = level
		self.xp = 0
	def givexp(self, points):
		if self.powerType.name == "slime.txt":
			points = points*2
		self.xp += points
		if self.xp > self.level*4:
			self.xp -= self.level*4
			self.level += 1
			print "Your Slime "+self.powerType.title+" is now more powerful"



	
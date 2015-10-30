'''Game maps module.

Contains map creation and usage logic

'''
#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon 

import g
import data
import tile
import creature
import play
import powers

import os
import random
import math
import pygame


class map_level:
	def __init__(self, size, level, style=0, startXY=-1, direction="none"):
		self.size = size
		self.level = level
		if startXY == -1:
			startXY = [random.randint(3, self.size[0]-4),
				random.randint(3, self.size[1]-4)]
		if len(self.size) < 2:
			data.error("size needs two dimensions: "+self.size)
			return
		#styles:
		#0 is random
		#1 is a natural cavern appearance.
		#2 is a series of connected rooms.
		self.style = style
		if self.style == 0:
			self.style = random.randint(1, 2)

		self.data = []
		self.creatures = []
		self.visibleTiles = []
		self.fillMap()
		if self.style == 1: #cavern
			self.digTunnel(startXY, direction)
			#self.digTunnel(startXY, direction)
			if direction == "down":
				self.setPoint(startXY, "stairsup.txt")
			elif direction == "up":
				self.setPoint(startXY, "stairs.txt")


	def placeCreature(self, xy):
		if self.isClear(xy):
			for i in range(10):
				tempCreature = creature.creatureTypes[
				random.choice(creature.creatureTypes.keys())]
				if (tempCreature.levelRange[0] > self.level or
						tempCreature.levelRange[1] < self.level):
					continue
				else:
					self.creatures.append(creature.creature(tempCreature,
							self.level, [xy[0], xy[1]]))
					break
 

		
	def fillMap(self):
		self.data = [None] * self.size[1]
		for i in range(self.size[1]):
			self.data[i] = [None] * self.size[0]
			for j in range(self.size[0]):
				self.data[i][j] = tile.tile(tile.tileTypes["stone.txt"])

	def clearPoint(self, xy):
		'''turns a tile into floor. Ignores the very edges of the map
		'''
		if xy[0] < 1 or xy[0] >= len(self.data[0])-1:
			return
		if xy[1] < 1 or xy[1] >= len(self.data)-1:
			return
		if self.data[xy[1]][xy[0]].style.name == "stone.txt":
			self.data[xy[1]][xy[0]] = tile.tile(tile.tileTypes["floor.txt"])
			
	def setPoint(self, xy, tileName):
		'''changes a tile.
		'''
		if xy[0] < 1 or xy[0] >= len(self.data[0])-1:
			return
		if xy[1] < 1 or xy[1] >= len(self.data)-1:
			return
		tempPlace = self.data[xy[1]][xy[0]].enemyPlaced
		self.data[xy[1]][xy[0]] = tile.tile(tile.tileTypes[tileName])
		self.data[xy[1]][xy[0]].enemyPlaced = tempPlace

	def digTunnel(self, xy, stairDirection="none", recurse=2):
		numberOfSteps = 100
		steeringChange = 0.35
		steeringBound = 0.5
		#data.trace("started new tunnel: "+str(recurse))
		pointer = [xy[0], xy[1]]
		direction = random.uniform(0, 2*math.pi)
		steering = random.uniform(-1.1, 1.1)
		placedStair = False
		placedStairUp = False
		placedHole = False
		for i in range(numberOfSteps):
			if (self.data[pointer[1]][pointer[0]].enemyPlaced == False and
								(random.random() < 0.02)):
				self.placeCreature(pointer)
				self.data[pointer[1]][pointer[0]].enemyPlaced = True
				
			if recurse > 0 and i % 26 == 0:
				self.digTunnel([pointer[0], pointer[1]], "none", recurse-1)
			if (not placedStair and self.level < 17 and
					(random.random() < 0.05 or i == numberOfSteps - 1)):
				self.setPoint(pointer, "stairs.txt")
				placedStair = True
			if (not placedStairUp and
					(random.random() < 0.05 or i == numberOfSteps - 1)):
				self.setPoint(pointer, "stairsup.txt")
				placedStairUp = True
			if (not placedHole and self.level < 17 and
					(random.random() < 0.05 or i == numberOfSteps - 1)):
				self.setPoint(pointer, "hole.txt")
				placedHole = True
			direction += steering
			steering += random.uniform(-steeringChange, steeringChange)
			steering = g.bound(steering, -steeringBound, steeringBound)
			xyDiff = g.radianToXY(direction)
			pointer[0] = pointer[0] + xyDiff[0]
			pointer[0] = g.bound(pointer[0], 1, self.size[0]-2)
			pointer[1] = pointer[1] + xyDiff[1]
			pointer[1] = g.bound(pointer[1], 1, self.size[1]-2)
			self.clearPoint(pointer)


	def dump(self):
		print self.size
		for i in range(len(self.data)):
			newLine = ""
			for j in range(len(self.data[i])):
				newLine += self.data[i][j].style.symbol
			print newLine
			
	def draw(self, xy):
		startx = max(0, xy[0]-g.screen_size[0]/(g.tileSize*2))
		starty = max(0, xy[1]-g.screen_size[1]/(g.tileSize*2))
		endx = min(self.size[0], startx+g.screen_size[0]/(g.tileSize))
		endy = min(self.size[1], starty+g.screen_size[1]/(g.tileSize))
		for i in range(starty, endy): #base tile layer
			for j in range(startx, endx):
				tempRect = pygame.Rect(self.data[i][j].style.picture[1]*g.tileSize,
				self.data[i][j].style.picture[2]*g.tileSize,
				g.tileSize, g.tileSize)
				tempR2 = ((j-startx)*g.tileSize, (i-starty)*g.tileSize)
				g.screen.blit(g.images[self.data[i][j].style.picture[0]],
				tempR2,
				tempRect)

		for creatureEntry in self.creatures: #creatures
			if self.visibleTiles.count(creatureEntry.xy) != 0:
				tempRect = pygame.Rect(creatureEntry.creatureType.picture[1]*g.tileSize,
						creatureEntry.creatureType.picture[2]*g.tileSize, g.tileSize, g.tileSize)
				g.screen.blit(g.images[creatureEntry.creatureType.picture[0]],
						((creatureEntry.xy[0]-startx)*g.tileSize,
						(creatureEntry.xy[1]-starty)*g.tileSize),
						tempRect)
				g.screen.fill((0, 235, 0), ((creatureEntry.xy[0]-startx)*g.tileSize,
						(creatureEntry.xy[1]-starty)*g.tileSize,
						((g.tileSize-1)*creatureEntry.hp)/creatureEntry.maxhp, 2))
		for i in range(starty, endy): #visibility overlay
			for j in range(startx, endx):
				if self.visibleTiles.count([j, i]) == 0:
					#g.screen.fill((0,0,0, 100), ((j-startx)*g.tileSize,
					#(i-starty)*g.tileSize, g.tileSize, g.tileSize))
					tempRect = pygame.Rect(32*g.tileSize, 0,
					g.tileSize, g.tileSize)
					tempR2 = ((j-startx)*g.tileSize, (i-starty)*g.tileSize)
					g.screen.blit(g.images["base.png"],
					tempR2,
					tempRect)
		tempRect = pygame.Rect(play.currPlayer.picture[1]*g.tileSize,
				play.currPlayer.picture[2]*g.tileSize, g.tileSize, g.tileSize)
		g.screen.blit(g.images[play.currPlayer.picture[0]],
				((xy[0]-startx)*g.tileSize, (xy[1]-starty)*g.tileSize),
				tempRect)
		g.screen.fill((0, 235, 0), ((xy[0]-startx)*g.tileSize,
				(xy[1]-starty)*g.tileSize,
				((g.tileSize-1)*play.currPlayer.hp)/play.currPlayer.maxhp, 2))
		self.drawUI()

	def drawUI(self):
		pointer = [0, g.screen_size[1]-g.tileSize, g.tileSize,
			g.tileSize]
		index = 0
		for power in play.currPlayer.powers:
			index += 1
			color = (0, 0, 35)
			if index-1 == play.currPlayer.currPower:
				color = (0, 0, 135)
			g.screen.fill(color, pointer)
			pygame.draw.rect(g.screen, (255,255,255), pointer, 1)
			tempRect = pygame.Rect(power.powerType.tile[1]*g.tileSize,
				power.powerType.tile[2]*g.tileSize, g.tileSize, g.tileSize)
			g.screen.blit(g.images[power.powerType.tile[0]],
				pointer, tempRect)
			tempSurface = g.smallFont.render(str(index), False,
			(255,255,255))
			g.screen.blit(tempSurface, pointer)
			pointer[0]+=g.tileSize

	def isClear(self, xy, xyDiff=(0,0)):
		if (xy[0]+xyDiff[0] < 0 or xy[0]+xyDiff[0] >= len(self.data[0])):
			return False
		if (xy[1]+xyDiff[1] < 0 or xy[1]+xyDiff[1] >= len(self.data)):
			return False
		return self.data[xy[1]+xyDiff[1]][xy[0]+xyDiff[0]].style.walkable
	
	def hasCreature(self, xy, xyDiff=(0,0)):
		if (xy[0]+xyDiff[0] < 0 or xy[0]+xyDiff[0] >= len(self.data[0])):
			return False
		if (xy[1]+xyDiff[1] < 0 or xy[1]+xyDiff[1] >= len(self.data)):
			return False
		return self.data[xy[1]+xyDiff[1]][xy[0]+xyDiff[0]].enemyPlaced

	def findCreature(self, xy, xyDiff=(0,0)):
		if not self.hasCreature(xy, xyDiff):
			return None
		pointer = (xy[0]+xyDiff[0], xy[1]+xyDiff[1])
		for i in range(len(self.creatures)):
			if self.creatures[i].xy[0] == pointer[0] and self.creatures[i].xy[1] == pointer[1]:
				return i
		return None

	def hasPlayer(self, xy, xyDiff=(0,0)):
		if (xy[0]+xyDiff[0] < 0 or xy[0]+xyDiff[0] >= len(self.data[0])):
			return False
		if (xy[1]+xyDiff[1] < 0 or xy[1]+xyDiff[1] >= len(self.data)):
			return False
		if play.currPlayer.xy == [xy[0]+xyDiff[0], xy[1]+xyDiff[1]]:
			return True
		return False

	def process(self, xy):
		self.visibleTiles = []
		startx = max(0, xy[0]-8)
		starty = max(0, xy[1]-8)
		endx = min(self.size[0], xy[0]+8)
		endy = min(self.size[1], xy[1]+8)
		for i in range(starty, endy):
			for j in range(startx, endx):
				if self.LOS(xy, [j, i]):
					self.visibleTiles.append([j, i])

	def overFeature(self, xy, xyDiff=(0,0)):
		return self.data[xy[1]+xyDiff[1]][xy[0]+xyDiff[0]].style.symbol
	
	def findCloser(self, creatureXY, xy):
		baseDistance = g.distance(creatureXY, xy)
		possible = None
		for diff in ((1, 1), (0, 1), (-1, 1), (1, -1), (0, -1), (-1, -1), (1, 0), (-1, 0)):
			if self.isClear(creatureXY, diff):
				if not self.hasCreature(creatureXY, diff):
					dist = g.distance([creatureXY[0]+diff[0], creatureXY[1]+diff[1]], xy)
					if dist < baseDistance:
						return diff
					elif dist == baseDistance:
						possible = diff
		return possible
		
	def run(self, xy):
		for creatureEntry in self.creatures:
			if g.distance(creatureEntry.xy, xy) <= 8:
				if ((not creatureEntry.aware) and
					self.visibleTiles.count(creatureEntry.xy) != 0):
						creatureEntry.aware = True
				if creatureEntry.aware == True:
					target = self.findCloser(creatureEntry.xy, xy)
					if target == None:
						continue
					if self.hasPlayer(creatureEntry.xy, target):
						play.currPlayer.attack(creatureEntry.attack)
						continue
					elif not self.hasCreature(creatureEntry.xy, target):
						self.data[creatureEntry.xy[1]][creatureEntry.xy[0]].enemyPlaced = False
						creatureEntry.xy[0] += target[0]
						creatureEntry.xy[1] += target[1]
						self.data[creatureEntry.xy[1]][creatureEntry.xy[0]].enemyPlaced = True
		
			
	def LOS(self, xy1, xy2):
		'''returns True if there's line of sight between the two points.
		Not completely accurate yet.'''
		if xy1[0] == xy2[0] and xy1[1] == xy2[1]:
			return True
		if not self.isClear(xy1): return False
		if not self.isClear(xy2): return False
		if xy1[0] > xy2[0]: #trade points if needed
			tempXY = [xy2[0], xy2[1]]
			xy2 = [xy1[0], xy1[1]]
			xy1 = [tempXY[0], tempXY[1]]
		#slope
		if xy1[0] == xy2[0]: #straight up/down
			intercept = "NaN"
			slope = "straight"
		else:
			slope = (xy2[1] - xy1[1]) / float(xy2[0] - xy1[0])
			intercept = xy1[1]-slope*xy1[0]
		for x in range(xy1[0], xy2[0]):
			y = int(slope*x+intercept)
			if not self.isClear([x, y]): return False
		
		for y in range(min(xy1[1], xy2[1]), max(xy1[1], xy2[1])):
			if slope == "straight":
				x = xy1[0]
			else:
				x = int((y-intercept)/slope)
			if not self.isClear([x, y]): return False
		return True
		
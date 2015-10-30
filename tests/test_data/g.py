'''Game global module.

Contains all the code and global variables I can't be bothered to stick in a
	class by itself.

'''

#Copyright (C) 2011 EMH Software
#This file is part of The Mimic Slime and the Forbidden Dungeon

import math

global debug
#0=only errors. 1=warnings. 2=trace
debug = 1

global simpleFont
global smallFont

global tileSize
tileSize = 32

global screen_size
screen_size = (640, 480)

global fullscreen
fullscreen = False

global symbolLength
symbolLength = 1

global screen

global images
images = {}

def bound(inInt, minInt, maxInt):
	return min(max(inInt, minInt), maxInt)

def XYtoRadian(xyStart, xyTarget):
	return math.atan2((xyTarget[1]-xyStart[1]), (xyTarget[0]-xyStart[0]))

def radianToXY(inRadian):
	'''converts a radian direction to a grid coordinate. Returns the
	xy differential.'''

	
	#0-pi/8->right, pi/8-3pi/8->up-right, 3pi/8-5pi/8->up
	#5pi/8-7pi/8->up-left, 7pi/8-9pi/8->left, 9pi/8-11pi/8->down-left
	#11pi/8-13pi/8->down, 13pi/8-15pi/8->down-right, 15pi/8-16pi/8->right
	piSlice = math.pi/8
	inRadian = inRadian % (2*math.pi) #get into the standard range
	if inRadian < piSlice: #right
		return [1, 0]
	if inRadian < piSlice*3: #up-right
		return [1, -1]
	if inRadian < piSlice*5: #up
		return [0, -1]
	if inRadian < piSlice*7: #up-left
		return [-1, -1]
	if inRadian < piSlice*9: #left
		return [-1, 0]
	if inRadian < piSlice*11: #down-left
		return [-1, 1]
	if inRadian < piSlice*13: #down
		return [0, 1]
	if inRadian < piSlice*15: #down-right
		return [1, 1]
	if inRadian < piSlice*16: #right (again)
		return [1, 0]

def distance(xy1, xy2):
	'''returns distance between two points, in the number of 8-way moves needed
	to arive'''
	return max(abs(xy2[0]-xy1[0]), abs(xy2[1]-xy1[1]))
	
#-------------------------------------------------------------------------------
#
#   Mutagenesis - Bezier curves
#
#-------------------------------------------------------------------------------

from pygame import draw

#-------------------------------------------------------------------------------

"""
bezier.py - Calculates a bezier curve from control points. 
 
2007 Victor Blomqvist
Released to the Public Domain
"""
 
#from vec2d import *
# 
#gray = (100,100,100)
#lightgray = (200,200,200)
#red = (255,0,0)
#green = (0,255,0)
#blue = (0,0,255)
#X,Y,Z = 0,1,2
 
def calculate_bezier(p, steps = 30):
	"""
	Calculate a bezier curve from 4 control points and return a 
	list of the resulting points.
	
	The function uses the forward differencing algorithm described here: 
	http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
	"""
	
	#print "calculate_bezier:", p ###
	
	t = 1.0 / steps
	temp = t*t
	
	f = p[0]
	fd = 3 * (p[1] - p[0]) * t
	fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
	fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
	
	fddd = 2 * fddd_per_2
	fdd = 2 * fdd_per_2
	fddd_per_6 = fddd_per_2 / 3.0
	
	points = []
	for i in xrange(steps):
		points.append(f)
		f = f + fd + fdd_per_2 + fddd_per_6
		fd += fdd + fddd_per_2
		fdd += fddd
		fdd_per_2 += fddd_per_2
	points.append(f)
	return points

#-------------------------------------------------------------------------------

def calculate_multi_bezier(points, steps):
	if not points:
		raise ValueError("Empty point list")
	result = []
	lastp = points[-1]
	for i in xrange(0, len(points), 3):
		p = points[i:i+4]
		if len(p) > 1:
			while len(p) < 4:
				p.append(lastp)
			result.extend(calculate_bezier(p, steps))
	#raw_input("?") ###
	return result

def fill_bezier(surf, color, points, steps):
	poly = calculate_multi_bezier(points, steps)
	draw.polygon(surf, color, poly)

#-------------------------------------------------------------------------------
#
#   Mutagenesis - Rendering
#
#-------------------------------------------------------------------------------

from __future__ import division
from math import pi, sin, cos
from pygame import Rect, Surface, Color, draw, transform, SRCALPHA
from pygame import gfxdraw
#from bezier import fill_bezier
from bezier import calculate_multi_bezier

from vector_algebra import vector

deg = pi / 180

#def vector(x, y):
#	return (x, y)

fill_colors = {
	1: Color("red"),
	2: Color("orange"),
	3: Color("yellow"),
	4: Color("light green"),
	5: Color("light blue"),
	6: Color("white"),
	7: Color("dark green"),
	8: Color("dark blue"),
	9: Color("violet"),
}

#-------------------------------------------------------------------------------

class Turtle(object):

	mirror = 1
	enable_drawing = True
	param_value = 1
	fill_color = fill_colors[1]
	diameter = 10

	def __init__(self, surf, pos, heading):
		self.surface = surf
		self.position = pos
		self.heading = heading
		self.init()
	
	def init(self):
		self.path = []
		self.branch_multiple = 0
	
	def clone(self, **kwds):
		cls = self.__class__
		turtle = cls.__new__(cls)
		turtle.__dict__.update(self.__dict__)
		turtle.__dict__.update(kwds)
		turtle.init()
		return turtle
	
	def forward(self, distance, color, width):
		#print "Turtle.forward:", distance, color ###
		a = self.heading * deg
		p0 = self.position
		x0, y0 = p0
		dx = distance * cos(a)
		dy = distance * sin(a)
		x1 = x0 + dx
		y1 = y0 + dy
		p1 = vector(x1, y1)
		#print "...", p0, p1 ###
		if self.enable_drawing:
			draw.line(self.surface, color, p0, p1, width)
		self.position = p1
		self.path.append(p1)
	
	def turn(self, angle):
		self.heading += self.mirror * angle
	
	def turn_for_branch(self, b, branch_angle):
		if b & 1:
			a = - ((b + 1) // 2)
		else:
			a = b // 2
		self.turn(a * branch_angle)
	
#	def flip_mirror(self):
#		self.mirror *= -1
	
	def mirror_heading(self, h):
		self.heading = h - (self.heading - h)

#-------------------------------------------------------------------------------

branch_angle = 20
wood_length = 10
wood_width = 3
wood_color = (0x80, 0x40, 0x00)
fill_color = (0x40, 0xc0, 0x00)
turn_angle = 10
bezier_steps = 5

def turn_left(turtle):
	turtle.turn(turn_angle)

def turn_right(turtle):
	turtle.turn(-turn_angle)

def render_wood(turtle):
	turtle.forward(wood_length, wood_color, wood_width)

def set_fill_color(turtle):
	turtle.fill_color = fill_colors[turtle.param_value]

def set_diameter(turtle):
	turtle.diameter = 2 * turtle.param_value

def set_branch_multiple(turtle):
	turtle.branch_multiple = turtle.param_value

def draw_circle(turtle):
	#draw.circle(turtle.surface, turtle.fill_color, turtle.position,
	#	turtle.diameter // 2)
	x, y = turtle.position
	r = turtle.diameter // 2
	gfxdraw.filled_circle(turtle.surface, int(x), int(y), r, turtle.fill_color)
	
rendering_procs = {
	"l": turn_left,
	"r": turn_right,
	"w": render_wood,
	"c": set_fill_color,
	"d": set_diameter,
	"o": draw_circle,
	"b": set_branch_multiple,
}

#-------------------------------------------------------------------------------

def render_symbol(turtle, sym):
	if "0" <= sym <= "9":
		turtle.param_value = int(sym)
	else:
		proc = rendering_procs.get(sym)
		if proc:
			proc(turtle)

def render_boundary(lturtle, rturtle, string, i, di):
	#print "render_boundary:", string, i, di ###
	while i >= 0:
		sym = string[i:i+1]
		i += di
		if sym == "{" or sym == "}" or sym == "":
			break
		render_symbol(lturtle, sym)
		render_symbol(rturtle, sym)
	return i

def render_filled_poly(turtle, string, i):
	#print "render_filled_poly:", string, i ###
	lturtle = turtle.clone(mirror = 1, enable_drawing = False)
	rturtle = turtle.clone(mirror = -1, enable_drawing = False)
	j = render_boundary(lturtle, rturtle, string, i, 1)
	h = turtle.heading
	lturtle.mirror_heading(h)
	rturtle.mirror_heading(h)
	render_boundary(lturtle, rturtle, string, j - 2, -1)
	###points = [turtle.position] + lturtle.path + list(reversed(rturtle.path))
	###draw.polygon(turtle.surface, fill_color, points)
	###gfxdraw.bezier(turtle.surface, points, 10, fill_color) ###
	###fill_bezier(turtle.surface, fill_color, points, bezier_steps)
	pfirst = [turtle.position]
	plast = [0.5 * (lturtle.path[-1] + rturtle.path[-1])]
	side1 = pfirst + lturtle.path + plast
	side2 = pfirst + rturtle.path + plast
	points1 = calculate_multi_bezier(side1, bezier_steps)
	points2 = calculate_multi_bezier(side2, bezier_steps)
	points = points1 + list(reversed(points2))
	draw.polygon(turtle.surface, lturtle.fill_color, points)
	return j

def render_multiple_branches(turtle, string, i, m):
	#print "render_multiple_branches:", i, string[i:] ###
	a = 360 / m
	for k in xrange(m):
		branch_turtle = turtle.clone()
		branch_turtle.turn(k * a)
		j = render_substring(branch_turtle, string, i)
		#print "render_multiple_branches: remaining:", string[j:] ###
	return j

def render_substring(turtle, string, i):
	#print "render_substring:", i, string[i:] ###
	n = len(string)
	b = 0
	while i < n:
		sym = string[i]
		i += 1
		#print "sym =", sym ###
		if sym == "[":
			m = turtle.branch_multiple
			if m:
				i = render_multiple_branches(turtle, string, i, m)
				turtle.branch_multiple = 0
			else:
				b += 1
				branch_turtle = turtle.clone()
				branch_turtle.turn_for_branch(b, branch_angle)
				i = render_substring(branch_turtle, string, i)
		elif sym == "]":
			break
		else:
			b = 0
			if sym == "{":
				i = render_filled_poly(turtle, string, i)
			else:
				render_symbol(turtle, sym)
	return i

def render_string(turtle, string):
	render_substring(turtle, string, 0)

def render_plant(plant, size):
	#print "render_plant:", plant, size ###
	buffer = plant.buffer
	if not buffer:
		size = (600, 600) ###
		#print "render_plant: Rendering", plant, "at", size ###
		buffer = Surface(size, SRCALPHA, 32)
		pos = vector(size[0] // 2, size[1])
		turtle = Turtle(buffer, pos, -90)
		render_string(turtle, plant.structure)
		plant.buffer = buffer
	return buffer

def get_plant_thumbnail(plant, size):
	#print "get_plant_thumbnail:", plant, size ###
	thumb = plant._thumbnail
	if not thumb:
		#print "get_plant_thumbnail: generating thumbnail" ###
		buffer = render_plant(plant, (600, 600))
		thumb = transform.smoothscale(buffer, size)
		plant._thumbnail = thumb
	return thumb

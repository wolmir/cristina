from __future__ import division

from pygame import *
from random import *
from math import *
import glob
import settings

cache = {}
fonts = {}

def preload():
	for iname in glob.glob("img/*.png"):
		getimg(iname[4:])

def drawtext(text, filled=True, size=64):
	if size not in fonts:
		fonts[size] = font.Font("font/Trade_Winds/TradeWinds-Regular.ttf", size)
	ix, iy = fonts[size].size(text)
	d = 1
	surf = Surface((ix+2*d, iy+2*d)).convert_alpha()
	surf.fill((0,0,0,0))
	i0 = fonts[size].render(text, True, (0, 0, 0))
	for off in ((d, 0), (0, d), (d, 2*d), (2*d, d)):
		surf.blit(i0, off)
	if filled:
		i1 = fonts[size].render(text, True, (255, 255, 255))
		surf.blit(i1, (d, d))
	return surf

def speckle(img):
	if settings.lowres:
		return
	for x in range(img.get_width()):
		for y in range(img.get_height()):
			r, g, b, a = img.get_at((x, y))
			r = min(max(int(r * uniform(0.9, 1.1)), 0), 255)
			g = min(max(int(g * uniform(0.9, 1.1)), 0), 255)
			b = min(max(int(b * uniform(0.9, 1.1)), 0), 255)
			img.set_at((x, y), (r, g, b, a))

def getimg(imgname):
	if imgname in cache:
		return cache[imgname]
	if imgname.endswith(".png"):
		img = image.load("img/" + imgname).convert_alpha()
		speckle(img)
	elif imgname == "purple":
		img = Surface((40, 40)).convert_alpha()
		img.fill((255, 0, 255))
	elif imgname == "brown":
		img = Surface((30, 30)).convert_alpha()
		img.fill((255, 128, 0))
	elif imgname.startswith("bird"):
		img = Surface((8, 4)).convert_alpha()
		img.fill((255, 255, 255))
	elif imgname == "cannonball":
		if settings.lowres:
			img = Surface((12, 12)).convert()
			img.fill((0, 0, 0))
			img.fill((60, 60, 60), (1, 1, 10, 10))
		else:
			img = Surface((14, 14)).convert_alpha()
			img.fill((0, 0, 0, 0))
			draw.circle(img, (0, 0, 0), (7, 7), 7)
			draw.circle(img, (60, 60, 60), (7, 7), 5)
	elif imgname == "cloud":
		img = Surface((40, 20)).convert_alpha()
		img.fill((255, 255, 255, 100))
	elif imgname == "mine":
		if settings.lowres:
			img = Surface((20, 28)).convert()
			img.fill((255, 100, 100))
		else:
			img = Surface((32, 32)).convert_alpha()
			img.fill((0, 0, 0, 0))
			draw.circle(img, (255, 100, 100, 50), (16, 12), 12)
			draw.circle(img, (255, 100, 100, 120), (16, 12), 8)
			draw.circle(img, (255, 100, 100, 255), (16, 12), 4)
	elif imgname == "splash":
		img = Surface((32, 32)).convert_alpha()
		img.fill((0, 0, 0, 0))
		for _ in range(10):
			r = 2
			x, y = randrange(r, 32-r), randrange(r, 32-r)
			draw.circle(img, (255, 255, 255, 100), (x, y), r)
	elif imgname == "wake":
		img = Surface((4, 4)).convert_alpha()
		img.fill((255, 255, 255, 100))
	elif imgname == "smoke":
		img = Surface((32, 32)).convert_alpha()
		img.fill((0, 0, 0, 0))
		for _ in range(10):
			r = 2
			x, y = randrange(r, 32-r), randrange(r, 32-r)
			draw.circle(img, (0, 0, 0, 100), (x, y), r)
	elif imgname == "heal":
		img = Surface((32, 32)).convert_alpha()
		img.fill((0, 0, 0, 0))
		for _ in range(10):
			r = 2
			x, y = randrange(r, 32-r), randrange(r, 32-r)
			draw.circle(img, (200, 200, 200, 100), (x, y), r)
	elif imgname == "island":
		img = Surface((120, 120)).convert_alpha()
		img.fill((0, 255, 0))
	elif imgname.startswith("rgb"):
		cs = map(int, imgname[3:].split(","))
		img = Surface((40, 40)).convert_alpha()
		img.fill(cs)
	elif imgname.startswith("hp:"):
		hp, hpmax = [int(x) for x in imgname[3:].split("/")]
		img = Surface((60, 60)).convert_alpha()
		img.fill((0,0,0,0))
		if hp > 0:
			thetas = [2*pi*x/(3*hpmax) for x in range(3*hp+1)]
			ps = [(30, 30)] + [(30 + 30*sin(theta), 30-30*cos(theta)) for theta in thetas]
			draw.polygon(img, (180,180,180), ps, 0)
			ps = [(30, 30)] + [(30 + 23*sin(theta), 30 - 23*cos(theta)) for theta in thetas]
			draw.polygon(img, (150,150,150), ps, 0)
			speckle(img)
	elif imgname.startswith("bosshp:"):
		hp, hp0 = [int(x) for x in imgname[7:].split("/")]
		w = 400
		img = Surface((w, 16)).convert_alpha()
		img.fill((255,255,255,255))
		img.fill((192,192,192,255), (2,2,w-4,12))
		if hp < hp0:
			img.fill((128,0,0,255), (2,2,(w-4)-(w-4)*hp//hp0,12))
	elif imgname.startswith("text:"):
		img = drawtext(imgname[5:])
	elif imgname.startswith("text-"):
		size, t = imgname[5:].split(":")
		img = drawtext(t, size=int(size))
	elif imgname.startswith("text0:"):
		img = drawtext(imgname[6:], False)
	elif imgname.startswith("rock"):
		w, h = [int(settings.ik * float(v)) for v in imgname[4:].split(",")]
		img = Surface((w, h)).convert_alpha()
		img.fill((0, 0, 0, 0))
		r = 6
		for y in range(r, h-r):
			for _ in range(4):
				x = randrange(r, w-r)
				c = randrange(70, 120)
				color = c + randrange(0, 10), c + randrange(0, 10), c + randrange(0, 10)
				draw.circle(img, color, (x, y), r)
	elif imgname.startswith("shroud"):
		img = Surface(settings.size).convert_alpha()
		img.fill(shroudcolor)
	elif imgname == "shadow":
		img = Surface((20, 20)).convert_alpha()
		img.fill((0, 0, 0, 0))
		draw.circle(img, (0, 0, 0, 160), (10, 10), 10)
	elif imgname.startswith("shadow"):
		r = [int(x) for x in imgname[6:].split("x")]
		img = Surface((w, h)).convert_alpha()
		img.fill((0, 0, 0, 0))
	elif imgname == "grayfill":
		img = Surface(settings.size).convert_alpha()
		img.fill((0, 0, 0, 200))
	elif imgname == "backdrop":
		img = Surface(settings.size).convert_alpha()
		img.fill((200, 200, 255))
		img.fill((140, 140, 255), (0, settings.Yh, settings.sX, settings.sY))
		line = Surface((settings.sX, 1)).convert()
		line.fill((255, 255, 255))
		for Y in range(settings.sY):
			dY = abs(Y - settings.Yh)
			line.set_alpha(min(max(255 - 2 * dY, 0), 255))
			img.blit(line, (0, Y))
	cache[imgname] = img
	return img

shroudcolor = 20, 20, 60, 90
def setshroud(color):
	global shroudcolor
	if color == shroudcolor:
		return
	if "shroud" in cache:
		del cache["shroud"]
	shroudcolor = tuple(x + cmp(y, x) for x, y in zip(shroudcolor, color))



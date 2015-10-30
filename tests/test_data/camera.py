from __future__ import division
from pygame import *
from math import *
import settings, img, state

pscale = 30

def drawbackdrop():
	display.get_surface().blit(img.getimg("backdrop"), (0, 0))

def drawshadow(x, y, r):
	i = img.getimg("shadow")
	yd = y - state.yc  # distance from camera to object
	if not settings.yrange[0] < yd < settings.yrange[1]:
		return
	k = settings.k0 * settings.dynormal / yd  # scale in screen pixels of 1 game unit at distance of object
	Y0 = int(settings.Yh + k * state.zc)  # Y-coordinate at z = 0
	iw0, ih0 = i.get_size()
	iw = 3.0 * r * k
	ih = state.zc / 5.0 * r * k
	if abs(k * x) > iw/2 + settings.sX/2:
		return
	if abs(Y0 - settings.sY / 2) > settings.sY/2 + ih/2:
		return
	srz = transform.smoothscale(i, (int(iw), int(ih)))

	X0 = settings.sX / 2 + k * x
	X = int(X0 - iw / 2)
	Y = int(Y0 - ih / 2)

	display.get_surface().blit(srz, (X, Y))

def drawlayer(layer):
	try:
		imgname, x, y, z, theta, ascale, obj = layer
	except:
		print layer
		raise
	if imgname == "shroud":
		return drawshroud()
	if ascale is None:
		ascale = 1
	yd = y - state.yc  # distance from camera to object
	if not settings.yrange[0] < yd < settings.yrange[1]:
		return

	if settings.lowres:
		theta = 0

	k = settings.k0 * settings.dynormal / yd  # scale in screen pixels of 1 game unit at distance of object
	Y0 = int(settings.Yh + k * state.zc)  # Y-coordinate at z = 0
	i = img.getimg(imgname)
	if theta == 0:
		iw0, ih0 = i.get_size()
		iw = iw0 * k * ascale / settings.ik
		ih = ih0 * k * ascale / settings.ik
		if abs(k * x) > iw/2 + settings.sX/2:
			return
		if abs(settings.Yh + k * (state.zc - z) - settings.sY / 2) > settings.sY/2 + ih/2:
			return
		srz = transform.smoothscale(i, (int(iw), int(ih)))
	else:
		srz = transform.rotozoom(i, degrees(theta), k * ascale / settings.ik)

	iw, ih = srz.get_size()
	Xc = settings.sX / 2 + k * x
	Yc = settings.Yh + k * (state.zc - z)
	X = int(Xc - iw / 2)
	Y = int(Yc - ih / 2)

	if Y >= Y0:
		return
	elif Y + ih >= Y0:
		area = 0, 0, iw, Y0 - Y  # don't draw the area below the water
	else:
		area = None
	display.get_surface().blit(srz, (X, Y), area)

def drawshroud():
	display.get_surface().blit(img.getimg("shroud"), (0, 0))

def drawwave(py):
	return
	y = settings.yv + settings.yr - 50 * (py - state.y0)
	display.get_surface().fill((128,128,255,50), (0, y, settings.sx, settings.sy))
	

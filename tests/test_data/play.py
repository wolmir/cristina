from pygame import *
from math import *
from random import *
import scene, camera, state, img, settings

class Scene(object):
	def __init__(self):
		state.init()
		state.start()
		self.t = 0
	def think(self, dt, kpressed, kdowns):
		self.t += dt
		if K_ESCAPE in kdowns or K_p in kdowns:
			if settings.DEBUG:
				scene.pop()
			else:
				scene.scenes.append(PauseScene(self))
		dx = int(kpressed[K_RIGHT] or kpressed[K_d] or kpressed[K_e]) - int(kpressed[K_LEFT] or kpressed[K_a])
		jumping = any(k in kdowns for k in (K_UP, K_w, K_COMMA, K_SPACE, K_RETURN, K_DOWN, K_s, K_o))
		shooting = state.mode in ["quest", "boss"]
		#shooting = kpressed[K_SPACE]
		state.player.control(dx, jumping, shooting)
		if settings.DEBUG and K_F2 in kdowns:
			state.player.hurt()
		if settings.DEBUG and K_F3 in kdowns:
			state.player.hp = state.hpmax
		if settings.DEBUG and K_F4 in kdowns:
			state.addboss()
		if settings.DEBUG and K_F5 in kdowns:
			state.beatboss()
		state.think(dt)
	def draw(self):
		camera.drawbackdrop()
		camera.drawwave(40)
		ls, ss = state.getlayers()
		for s in ss:
			camera.drawshadow(*s)
		for l in ls:
			camera.drawlayer(l)
		
		screen = display.get_surface()
		i = img.getimg("text-44:Stage %s" % state.stage)
		screen.blit(i, i.get_rect(bottomleft=(10, settings.sY+5)))
		i = img.getimg("hp:%s/%s" % (state.player.hp, state.hpmax))
		screen.blit(i, i.get_rect(bottomright=(settings.sX-8, settings.sY-8)))
		if state.mode == "boss" and state.bosses:
			i = img.getimg("text-44:BOSS")
			screen.blit(i, i.get_rect(midtop=(settings.sX//2, 2)))
			hp = sum(b.hp for b in state.bosses)
			hp0 = sum(b.hp0 for b in state.bosses)
			i = img.getimg("bosshp:%s/%s" % (hp, hp0))
			screen.blit(i, i.get_rect(midtop=(settings.sX//2, 60)))

class PauseScene(object):
	def __init__(self, scene0):
		self.scene0 = scene0
	def think(self, dt, kpressed, kdowns):
		if K_ESCAPE in kdowns or K_p in kdowns:
			scene.pop()
		if K_q in kdowns:
			scene.pop()
			scene.pop()
	def draw(self):
		self.scene0.draw()
		screen = display.get_surface()
		screen.blit(img.getimg("grayfill"), (0, 0))
		X0, Y0 = settings.sX // 2, settings.sY // 2
		i = img.getimg("text:Esc: resume")
		screen.blit(i, i.get_rect(midbottom = (X0, Y0)))
		i = img.getimg("text:Q: quit")
		screen.blit(i, i.get_rect(midtop = (X0, Y0)))


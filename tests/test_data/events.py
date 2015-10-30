#7444
#Events

import pygame
from pygame.locals import *
import sys
from logger import Log

def PyGame_Event_Quit(event, engine):
	engine.properties["running"] = False

def PyGame_Event_Stub(event, engine):
	pass

def PyGame_Event_Stub_Verbose(event, engine):
	Log.Message("Stub event: " + str(pygame.event.event_name(event.type)))

def PyGame_Event_KeyDown(event, engine):
	engine.properties["keydown"] = pygame.key.name(event.key)

def PyGame_Event_KeyUp(event, engine):
	engine.properties["keydown"] = None



PyGame_Events = {
	pygame.QUIT : PyGame_Event_Quit,
	pygame.ACTIVEEVENT : PyGame_Event_Stub_Verbose,
	pygame.KEYDOWN : PyGame_Event_Stub,
	pygame.KEYUP : PyGame_Event_Stub,
	pygame.MOUSEMOTION : PyGame_Event_Stub,
	pygame.MOUSEBUTTONUP : PyGame_Event_Stub,
	pygame.MOUSEBUTTONDOWN : PyGame_Event_Stub,
	pygame.JOYAXISMOTION : PyGame_Event_Stub,
	pygame.JOYBALLMOTION : PyGame_Event_Stub,
	pygame.JOYHATMOTION : PyGame_Event_Stub,
	pygame.JOYBUTTONUP : PyGame_Event_Stub,
	pygame.JOYBUTTONDOWN : PyGame_Event_Stub,
	pygame.VIDEORESIZE : PyGame_Event_Stub_Verbose,
	pygame.VIDEOEXPOSE : PyGame_Event_Stub_Verbose,
	pygame.USEREVENT : PyGame_Event_Stub
}
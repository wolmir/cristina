#
# libengine.py
# If you want some more structure other than the benefit the exe gives you, here is some pygame
#     related stuff
# libengine.py MUST have a run() method that runs the game
# Other than that its up to you
#
#  this version will build on some other base code
#   * engine.py - handles timing, input, and display
#   * world.py - some engines call this a state, its a displayable runable part of a game,
#                    such as a menu, or the level running code. Worlds contain Agents, the
#                    equivalent of sprites
#   * controller.py - handles some basic input for toggling fullscreen, or quitting the game
#
#   Important to note, game runs on a fixed timestep (currently set to 60hz)
#   Update functions don't need to know the time passed since last frame, just assume
#   it's been 1/60, or if you change the framerate, 1/framerate
#



import sys,os
import time
import engine
import controller
import world
if sys.platform=="win32":
    os.environ['SDL_VIDEODRIVER']='windib'

try:
    import android
except:
    android = None
    
engine = engine.Engine()
controller = controller.Controller(engine)

def run():
    engine.running = True
    engine.start()
    engine.world = world.make_world(engine)
    
    
    lt = time.time()
    ticks = 0
    fr = 0
    engine.screen_refresh = 1
    engine.next_screen = engine.screen_refresh

    while engine.running:
        engine.dt = engine.clock.tick(getattr(engine,"framerate",30))
        engine.dt = min(engine.dt*.001*60,100.0)
        engine.update()
        engine.next_screen -= engine.dt
        if engine.next_screen < 0:
            engine.clear_screen()
            engine.world.draw()
            engine.draw_screen()
            engine.next_screen = engine.screen_refresh
        controller.input()
    print "quit"
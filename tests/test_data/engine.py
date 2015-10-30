#
# engine.py - handles generally running the game
# can set a game resolution (iwidth, iheight) as well as a screen resolution
# the screen scales to fit
# also has a builting framerate counter
#


import pygame
import random

def fit(surf,size):
    surf = pygame.transform.smoothscale(surf,size)
    return surf

class Engine:
    def __init__(self):
        self.fullscreen = False
        #The screen width, what resolution the screen is scaled to
        self.swidth = 640
        self.sheight = 480
        #The interactive width, what resolution the game is actually rendered at
        self.iwidth = 640
        self.iheight = 480
        self.window = None   #The window is the actual window
        self.surface = None   #The surface is what will be displayed, most of the time draw to this
        self.blank = None
        self.running = False   #If this is set to false, the game will quit
        self.paused = False   #Not implemented, should be controlled by the world
        self.framerate = 60    #What framerate the game runs at
        self.dt = 0
        self.show_fps = True
        self.clock = None
        self.world = None   #Change what world is set to to change between scenes or modes
        self.next_tick = 0.0
        self.spread = .01
        self.spread2 = 1.0
        self.offset = [0,0]
        self.reset = .02
    def start(self):
        """Separate from __init__ in case we want to make the object before making the screen"""
        pygame.init()
        pygame.mixer.init()
        self.make_screen()
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("fonts/vera.ttf",12)
    def stop(self):
        self.running = False
    def pause(self):
        self.paused = True
    def unpause(self):
        self.paused = False
    def update(self):
        """One tick, according to dt"""
        self.next_tick += self.dt
        if self.world:
            while self.next_tick>0:
                self.next_tick -= 1
                self.world.update()
    def make_screen(self):
        flags = pygame.RESIZABLE|pygame.FULLSCREEN*self.fullscreen
        pygame.display.set_icon(pygame.image.load("art/icons/ico.png"))
        self.window = pygame.display.set_mode([self.swidth,self.sheight],flags)
        self.surface = pygame.Surface([self.iwidth,self.iheight]).convert()
        self.blank = self.surface.convert()
        self.blank.fill([0,0,0])
    def get_mouse_pos(self):
        x,y = pygame.mouse.get_pos()
        x=int(x*(self.iwidth/float(self.swidth)))
        y=int(y*(self.iheight/float(self.sheight)))
        return x,y
    def clear_screen(self):
        self.surface.blit(self.blank,[0,0])
    def draw_screen(self):
        showfps = self.show_fps
        self.window.fill([10,10,10])
        def draw_segment(dest,surf,pos,size,alpha=255):
            rp = [pos[0]*self.swidth,pos[1]*self.sheight]
            rs = [size[0]*self.swidth,size[1]*self.sheight]
            surf = fit(surf,rs)
            if alpha!=255:
                surf.set_alpha(alpha)
            dest.blit(surf,rp)
        draw_segment(self.window,self.surface,[0,0],[1,1])
        if random.randint(0,200)==-1:
            self.offset[0]=random.random()*self.spread2-self.spread2/2.
            self.offset[1]=random.random()*self.spread2-self.spread2/2.
        else:
            if self.offset[0]>0:
                self.offset[0]-=self.reset
            elif self.offset[0]<0:
                self.offset[0]+=self.reset
            if abs(self.offset[0])<self.reset:
                self.offset[0]=random.random()*self.spread-self.spread/2.
            if self.offset[1]>0:
                self.offset[1]-=self.reset
            elif self.offset[1]<0:
                self.offset[1]+=self.reset
            if abs(self.offset[1])<self.reset:
                self.offset[1]=random.random()*self.spread-self.spread/2.
        draw_segment(self.window,self.surface,self.offset,[1,1],40)
        white = self.surface.convert()
        white.fill([0,0,0])
        draw_segment(self.window,white,[0,0],[1,1],random.randint(0,5))
        if showfps:
            self.window.blit(self.font.render(str(self.clock.get_fps()),1,[255,0,0]),[0,self.window.get_height()-12])
        pygame.display.flip()
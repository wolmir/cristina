#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
import random
import time
from virus import *
from agents import *

class World(object):
    def __init__(self,engine):
        self.engine = engine
        self.objects = []
        self.sprites = []
        self.start()
    def add(self,o):
        """Add an object to the scene"""
        self.objects.append(o)
    def start(self):
        """Code that runs when a world starts, base world
        doesn't need to do anything"""
    def update(self):
        """self.sprites starts empty, any object added to the list during
        update() is going to be rendered"""
        self.sprites = []
        for o in self.objects:
            o.update(self)
            if o.visible:
                self.sprites.append(o)
    def draw(self):
        """Iterate sprites and draw them"""
        [s.draw(self.engine) for s in self.sprites]
    def input(self,controller):
        """As controller gets functions to check the state of things, input
        can be put here"""
        
        
def off(pos,offamt):
    return [pos[0]+offamt[0],pos[1]+offamt[1]]
class CityDrawer(Agent):
    def draw(self,engine):
        offx,offy = self.pos
        def of(p):
            return off(p,[offx,offy])
        self.world.over = None
        for c in self.world.cities:
            for near in c.get_travelmap():
                pygame.draw.line(engine.surface,[50,150,50],of(c.pos),of(near[1].pos))
        for c in self.world.cities:
            color = [0,255,0]
            if c.get_infected():
                color = [255,0,0]
            pygame.draw.line(engine.surface,[0,0,0],of(c.pos),of([c.pos[0],c.pos[1]+4]))
            n = engine.font.render("%s"%len([pp for pp in c.people if not pp.dead and pp.job]),1,[0,0,0])
            engine.surface.blit(n,of([c.pos[0]-n.get_width()//2,c.pos[1]+4]))
            pygame.draw.circle(engine.surface,color,of(c.pos),3)
            x,y = engine.get_mouse_pos()
            p = of(c.pos)
            if x>=p[0]-8 and x<=p[0]+8 and y>=p[1]-8 and y<=p[1]+8:
                self.world.over = c
        c = None
        if self.world.over:
            c = self.world.over
        elif self.world.panel.city:
            c = self.world.panel.city
        if c:
            cname = engine.font.render(c.name,1,[0,0,0])
            s = cname.copy()
            s.fill([0,255,0])
            s.blit(cname,[0,0])
            px,py = of([c.pos[0]-s.get_width()//2+10,c.pos[1]-s.get_height()//2-10])
            if px<0:
                px = 0
            if py<0:
                py = 0
            engine.surface.blit(s,[px,py])
            
class Text(Agent):
    def set_text(self,text):
        self.surface = None
        self.text = text
        return self
    def render(self,engine):
        if not self.surface:
            self.surface = engine.font.render(self.text,1,[0,255,0])
    def draw(self,engine):
        if not self.surface:
            self.render(engine)
        engine.surface.blit(self.surface,self.pos)

class CityPanel(Agent):
    def init(self):
        self.turnon = None
        self.city = None
        self.objects = []
    def update(self,world):
        self.objects = []
        px = 10
        py = 10
        self.over = None
        mx,my = world.engine.get_mouse_pos()
        mx-=self.pos[0]
        if mx>=0 and mx<=200 and my>=0 and my<=400:
            self.over = self.update
        if self.city:
            self.objects.append(Text(pos=[px,py]).set_text(self.city.name))
            py+=15
            for p in self.city.people:
                if p.symptoms():
                    self.objects.append(
                        Text(pos=[px,py]).set_text("%s - %s"%(
                                p.name,
                                ",".join([x.name for x in p.symptoms()])
                            )))
                    py += 10
            py = 210
            def btn(text,action,icon=None):
                if mx>=px and mx<=px+200 and my>=py and my<=py+20:
                    self.over = getattr(self,action)
                    self.objects.append(Agent("art/select.png",pos=[px,py]))
                if icon:
                    self.objects.append(Agent(icon,pos=[px,py]))
                self.objects.append(Text(pos=[px+20,py]).set_text(text))
            if self.city.isolated:
                btn("Connect [-100]","connect","art/car.png")
                py+=20
            else:
                inf = 5
                if self.city.advertising:
                    inf = 3
                btn("Isolate [$500/%s inf]"%inf,"isolate","art/car.png")
                py+=20
            btn("Hire researcher [$50] (%s)"%len([x for x in self.city.people if x.job=="researcher"]),"researcher","art/researcher.png")
            py+=20
            btn("Hire doctor [$200] (%s)"%len([x for x in self.city.people if x.job=="doctor"]),"doctor","art/doctor.png")
            py+=20
            if self.city.advertising:
                btn("(advertising bought)","update")
            else:
                btn("buy advertising [$600]","influence")
        if self.turnon:
            d = 0
            if self.pos[0]>d:
                self.pos[0]=-200
            if self.pos[0]<d:
                self.pos[0]+=20
                #~ if self.turnon<240:
                    #~ if self.world.map.pos[0]<200:
                        #~ self.world.map.pos[0]+=20
    def draw(self,engine):
        self.surface.fill([0,0,0])
        pygame.draw.rect(self.surface,[0,255,0],[[0,0],[200,400]],2)
        super(CityPanel,self).draw(engine)
        for o in self.objects:
            p = o.pos[:]
            o.pos[0]+=self.pos[0]
            o.pos[1]+=self.pos[1]
            o.draw(engine)
            o.pos = p
    def action(self,world,money=None,influence=None):
        con = 1
        if influence:
            con = 1*con
            if influence>world.player.influence:
                con = 0*con
        if money and con:
            if world.player.budget>=money:
                world.player.budget-=money
                con = 1*con
            else:
                con = 0*con
        if not con:
            world.engine.offset = [random.random()*0.2-0.1,random.random()*0.2-0.1]
        return con
    def isolate(self,world):
        inf = 5
        if self.city.advertising:
            inf = 3
        if self.action(world,500,inf):
            self.city.isolated = True
    def connect(self,world):
        if self.action(world,-100,0):
            self.city.isolated = False
    def doctor(self,world):
        if self.action(world,200,0):
            d = Doctor()
            d.player = world.player
            inhabit(self.city,d)
    def researcher(self,world):
        if self.action(world,50,0):
            r = Researcher()
            r.player = world.player
            inhabit(self.city,r)
    def influence(self,world):
        if self.action(world,600,0):
            world.player.influence += 1
            self.city.advertising += 1

class Messages(Agent):
    def init(self):
        self.objects = []
        self.bg = pygame.Surface([640,40])
        self.bg.fill([0,0,0])
        self.bg.set_alpha(150)
        self.over = None
    def update(self,world):
        self.over = None
        for o in self.objects[:]:
            o.pos[0]-=2
            x,y = world.engine.get_mouse_pos()
            if x>=o.pos[0] and x<=o.rect().right and y>=o.pos[1] and y<=o.rect().bottom:
                self.over = o
            if o.pos[0]<-600:
                self.objects.remove(o)
    def draw(self,engine):
        engine.surface.blit(self.bg,[0,440])
        [o.draw(engine) for o in self.objects]
        if self.over and self.over.data[1].has_key("city"):
            pygame.draw.line(engine.surface,[255,255,255],self.over.pos,self.over.data[1]["city"].pos)
    def right(self):
        if not self.objects:
            return 660
        last = self.objects[-1]
        return last.rect().right+10
        
class PlayerPanel(Agent):
    def init(self):
        self.objects = []
        self.bg = pygame.Surface([140,240])
        self.bg.fill([0,0,0])
        self.bg.set_alpha(150)
        self.player = None
    def update(self,world):
        if self.player:
            self.objects = []
            x=self.pos[0]+2
            y=self.pos[1]+2
            self.objects.append(Agent(art="art/dollar.png",pos=[x,y]))
            self.dollar_text = Text(pos=[x+20,y])
            self.objects.append(self.dollar_text)
            y+=20
            self.influence_text = Text(pos=[x+20,y])
            self.objects.append(self.influence_text)
            y+=20
            self.score_text = Text(pos=[x+20,y])
            self.objects.append(self.score_text)
            y+=20
            self.objects.append(Text(pos=[x,y]).set_text("Virus study level:"))
            y+=20
            self.objects.append(Text(pos=[x+20,y]).set_text("%s"%(len(self.player.viruses))))
            y+=20
        if self.player:
            self.dollar_text.set_text("%(budget)s/%(max_budget)s +%(income)s"%self.player.__dict__)
            self.influence_text.set_text("Influence: %(influence)s"%self.player.__dict__)
            self.score_text.set_text("Score: %(score).2f%%"%self.player.__dict__)
    def draw(self,engine):
        engine.surface.blit(self.bg,self.pos)
        [o.draw(engine) for o in self.objects]
        
class MapWorld(World):
    def play_music(self):
        pygame.mixer.music.load("music/gurdonark_-_Glow.ogg")
        pygame.mixer.music.play(-1)
    def start(self,num_viruses=1,seed=int(time.time()*100)):
        #~ seed = 131603110005
        #~ seed = "i like cats"
        if seed:
            random.seed(seed)
        self.offset = [0,0]
        self.mapart = Agent(art="art/americalowres.png",pos=[0,0])
        self.add(self.mapart)
        self.map = CityDrawer(pos=[0,0])
        self.map.world = self
        self.add(self.map)
        self.panel = CityPanel(pos=[-200,0])
        self.panel.surface = pygame.Surface([200,400])
        self.add(self.panel)
        self.panel.world = self
        self.num_viruses = num_viruses
        self.load_cities()
        self.play_music()
        self.over = None
        self.turn_time = 60*3
        self.next_turn = self.turn_time
        self.messages = []
        self.message_time = 60*2
        self.next_message = 0
        self.messagepanel = Messages()
        self.add(self.messagepanel)
        self.playerpanel = PlayerPanel(pos=[510,220])
        self.add(self.playerpanel)
        self.player = Player()
        self.playerpanel.player = self.player
    def load_cities(self):
        self.cities = []
        f = open("dat/cities.txt")
        for l in f.read().replace("\r\n","\n").split("\n"):
            if l.endswith("*"):
                stuff = [x.strip() for x in l.split("  ") if x.strip()]
                code,lat,long,city = stuff
                city = city[:-1]
                city,state = city.split(",")
                if "/" in city:
                    city = city.split("/",1)[0]
                lat = float(lat)
                long = float(long)
                width=64
                height=20
                px = (-long+123)/float(width)*640+25
                py = (-lat+48)/float(height)*480
                self.cities.append(Location(name=city+", "+state,lat=lat,long=long,pos=[px,py]))
        f = open("dat/population.txt")
        pops = {}
        for l in f.read().replace("\r\n","\n").split("\n"):
            stuff = l.split("\t")
            cn = stuff[1]
            pop = float(stuff[3].replace(",",""))
            area = float(stuff[4].replace(",",""))
            dens = float(stuff[5].replace(",",""))
            pops[cn.lower().strip()] = {"population":pop,"area":area,"density":dens}
        self.total_pop = 0
        for c in self.cities:
            c.__dict__.update(pops[c.name.lower().split(",")[0]])
            c.travel_table(self.cities)
            numpeeps = int(min((c.population/10000000.0)*100,15))
            avg_size = c.population/float(numpeeps)
            pop = c.population
            for x in range(numpeeps):
                p = gen_random_population()
                p.size = avg_size+(random.randint(-avg_size//3,avg_size//3))
                pop -= p.size
                if pop<0:
                    p.size+=pop
                    pop=0
                p.size = int(p.size)
                if p.size<0:
                    p.size = 100
                inhabit(c,p)
                self.total_pop+=p.size
            if pop>0:
                random.choice(c.people).size+=int(pop)
                self.total_pop+=int(pop)
        for i in range(self.num_viruses):
            random.shuffle(self.cities)
            zero = self.cities[0]
            p = random.choice(zero.people)
            infect(badvirus,p)
        for i in range(10):
            random.shuffle(self.cities)
            p = random.choice(self.cities[0].people)
            infect(nicevirus,p)
    def input(self,controller):
        if controller.mbdown:
            if self.messagepanel.over:
                self.panel.turnon = self.messagepanel.over.data[1]["city"].pos[0]
                self.panel.pos[0] = -200
                self.panel.city = self.messagepanel.over.data[1]["city"]
            elif self.panel.over:
                self.panel.over(self)
            elif self.over:
                self.panel.turnon = self.over.pos[0]
                self.panel.pos[0] = -200
                self.panel.city = self.over
            else:
                self.panel.pos[0] = -200
                self.map.pos = [0,0]
                self.panel.turnon = None
                self.panel.city = None
    def update(self):
        super(MapWorld,self).update()
        self.next_turn -= 1
        if self.next_turn <=0:
            self.next_turn = self.turn_time
            self.turn()
        if self.messages:
            self.next_message -= 1
            if self.next_message<=0:
                t = Text(pos=[self.messagepanel.right(),460])
                t.data = self.messages.pop(0)
                t.set_text(t.data[0])
                self.messagepanel.objects.append(t)
                self.next_message = self.message_time
        self.mapart.pos = self.map.pos
    def turn(self):
        d = {"news":[],"world":self}
        [c.turn(d) for c in self.cities]
        self.player.turn()
        pop = 0
        virusleft = 0
        for c in self.cities:
            for p in c.people:
                if not p.dead:
                    pop += p.size
                    for il in p.illnesses:
                        if il.type=="deadly":
                            virusleft += 1
        self.player.score = pop/float(self.total_pop)*100
        for n in d["news"]:
            if n["type"] == "deaths":
                msg = ("%(amount)s reported dead in %(cityname)s"%n,n)
            self.messages.append(msg)
        if not virusleft:
            self.engine.world = Losing(self.engine)
            self.engine.world.oldworld = self
            
class Losing(World):
    def update(self):
        if not hasattr(self,"fade"):
            self.fade = 0
            self.fadesurf = pygame.Surface([640,480])
            self.end = 0
        if self.fade<255:
            self.fade += 3
        else:
            self.end += 1
            sc = self.oldworld.player.score
            grade = "F"
            if sc>=60:
                grade = "D"
            if sc>=70:
                grade = "C"
            if sc>=80:
                grade = "B"
            if sc>=90:
                grade = "A"
            self.objects = [Text(pos=[200,180]).set_text("The virus has been wiped out.")]
            self.objects += [Text(pos=[200,220]).set_text("Percentage remaining: %.2f%% - %s"%(sc,grade))]
            self.objects += [Text(pos=[200,280]).set_text("Click to retry")]
        super(Losing,self).update()
    def draw(self):
        if hasattr(self,"fadesurf"):
            self.oldworld.draw()
            self.fadesurf.set_alpha(int(self.fade))
            self.engine.surface.blit(self.fadesurf,[0,0])
            super(Losing,self).draw()
    def input(self,controller):
        if hasattr(self,"end") and self.end>100:
            if controller.mbdown:
                self.engine.world = MapWorld(self.engine)
                self.engine.world.start()
        
def make_world(engine):
    """This makes the starting world"""
    w = MapWorld(engine)
    return w

import math
import random

class Model(object):
    def __init__(self,**kwargs):
        keys = dir(self)
        self.defaults()
        self.attr = []
        for k in dir(self):
            if k not in keys:
                self.attr.append(k)
        self.__dict__.update(kwargs)

class Player(Model):
    def defaults(self):
        self.budget = 1000   #Current budget
        self.income = 100   #How much we will get
        self.max_budget = 1000   #Our budget can't exceed this
        self.influence = 1    #How much influence we have
        self.tonics = 0
        self.cures = 0
        self.viruses = 0
        self.score = 100
        self.score_bonus = 0
        self.viruses = {}
    def turn(self):
        if self.score_bonus == 0 and self.score<70:
            self.influence += 4
            self.score_bonus += 1
            self.income += 100
        self.budget+=self.income
        if self.budget>self.max_budget:
            self.budget = self.max_budget
        
class Location(Model):
    def defaults(self):
        self.name = "Seattle"
        self.pos = [0,0]
        self.people = []
        self.population = 1000
        self.area = 1000
        self.density = 1000
        self.isolated = False
        self.advertising = 0
        self.travelmap = []
    def turn(self,context):
        anydead = self.get_infected()
        context["location"] = self
        for p in self.people:
            p.turn(context)
        if anydead != self.get_infected() and "news"  in context:
            context["news"].append({"type":"deaths","amount":self.get_infected_count(),"cityname":self.name,"city":self})
    def add(self,p):
        self.people.append(p)
    def remove(self,p):
        if p in self.people:
            self.people.remove(p)
    def travel_table(self,city_list):
        """Calculate distance to each city in the list"""
        self.travelmap = []
        def dist(a,b):
            return math.sqrt((a.pos[0]-b.pos[0])**2+(a.pos[1]-b.pos[1])**2)
        for c in city_list:
            if c == self:
                continue
            d = dist(c,self)
            if d>100:
                continue
            self.travelmap.append((d,c))
        self.travelmap.sort(key=lambda c:c[0])
    def get_travelmap(self):
        if self.isolated:
            return []
        return [x for x in self.travelmap if not x[1].isolated]
    def get_infected(self):
        """How infected are we?"""
        return len([x for x in self.people if x.dead])
    def get_infected_count(self):
        return sum(x.size for x in self.people if x.dead)

class Population(Model):
    def defaults(self):
        self.name = "fred"
        self.size = 1000 #how many people I represent
        self.lifestyle = 0  #healthy lifestyle? poor? smokers? etc
        self.race = "white"  #what race they are
        self.sex = "male"
        self.age = 18   #average age
        self.mobility = 2  #how many turns between travelling
        self.trust = 0  #How likely they are to trust the media
        self.job = None
        
        self.location = None
        self.last_travel = 0
        self.travel_history = []  #first entry is their home
        self.homesick = 0
        self.max_travel_distance = 3
        self.illnesses = []
        self.immunities = set()
        self.dead = False
    def travel_factor(self):
        """Calculate whether we are fit to travel or not"""
        if self.dead:
            return 0
        tf = 10
        for s in self.symptoms():
            tf -= s.visibility*s.severity
        return tf
    def symptoms(self):
        symptoms = set()
        if self.dead:
            return symptoms
        for i in self.illnesses:
            for s in i.symptoms():
                symptoms.add(s)
        return symptoms
    def turn(self,context):
        if self.dead:
            return
        context["population"] = self
        for s in self.symptoms():
            if s.name == "death":
                n = context.get("dead",0)
                n+=1
                context["dead"] = n
                self.dead = True
        self.random_walk(context["location"])
        for i in self.illnesses:
            i.turn(context)
    def random_walk(self,location):
        tf = self.travel_factor()
        if tf<5:
            return
        if self.homesick:
            if self.travel_history:
                self.moveto(self.travel_history[-1],False)
                del self.travel_history[-1]
            if not self.travel_history:
                self.homesick = False
                self.last_travel=0
            return
        self.last_travel += 1
        if self.last_travel>=self.mobility:
            self.last_travel = 0
            options = location.get_travelmap()
            if not options:
                return
            l = random.choice(options)
            self.moveto(l[1])
            if len(self.travel_history)>=self.max_travel_distance:
                self.homesick = True
    def moveto(self,l,history=True):
        if history:
            self.travel_history.append(self.location)
        self.location.remove(self)
        inhabit(l,self)        
    def remove_disease(self,d):
        if d in self.illnesses:
            self.illnesses.remove(d)
            
class Doctor(Population):
    def defaults(self):
        Population.defaults(self)
        self.job = "doctor"
        self.name = "Doctor"
        self.lifestyle = 10
    def random_walk(self,location):
        pass
    def turn(self,context):
        self.dohealing()
        super(Doctor,self).turn(context)
    def dohealing(self):
        if not self.location:
            return
        people = self.location.people[:]
        def score(p):
            sc = 0
            for i in p.illnesses:
                if i.name in self.player.viruses:
                    if self.player.viruses[i.name]>sc:
                        sc = self.player.viruses[i.name]
        people.sort(key=lambda p:score(p))
        if not people:
            return
        p = people[-1]
        if score(p)==0:
            return
        il = p.illnesses[:]
        def score(i):
            if i.name in self.player.viruses:
                return self.player.viruses[i.name]*i.age
            return 0
        if not il:
            return
        il.sort(key=lambda i:score(i))
        il = il[-1]
        if score(il)==0:
            return
        il.age -= self.player.viruses[il.name]*2
        if il.age<=0:
            p.remove_disease(il)
        
class Researcher(Population):
    def defaults(self):
        Population.defaults(self)
        self.job = "researcher"
        self.name = "Researcher"
        self.lifestyle = 10
    def random_walk(self,location):
        pass
    def turn(self,context):
        self.doresearch()
        super(Researcher,self).turn(context)
    def doresearch(self):
        if not self.location:
            return
        names = set()
        for p in self.location.people:
            if p.job in ["researcher","doctor"]:
                continue
            for il in p.illnesses:
                names.add(il.name)
        def score(name):
            sc = 0
            if sc not in self.player.viruses:
                sc = 10
            else:
                sc = 3-self.player.viruses[name]
            return sc
        names = list(names)
        if not names:
            return
        names.sort(key=lambda x:score(x))
        name = names[0]
        sc = self.player.viruses.get(name,0)
        sc += 1
        if sc>3:
            sc = 3
        self.player.viruses[name] = sc

names = []
f = open("dat/people.txt")
mode = None
for l in f.read().replace("\r\n","\n").split("\n"):
    if l.startswith("name/"):
        spl = l.split("/")
        mode = spl[0]
        race,sex = spl[1:]
    elif mode=="name":
        if l.strip():
            n = l.strip()
            names.append({"race":race,"sex":sex,"name":n})
def gen_random_population():
    random.shuffle(names)
    n = names[0]#.pop(0)
    x = Population(name=n["name"])
    sex,race = n["sex"],n["race"]
    if sex=="any":
        sex = random.choice(["male","female"])
    if race=="any":
        sex = random.choice(["african american","white","latino","asian"])
    x.sex = sex
    x.race = race
    x.age = random.randint(6,52)
    x.mobility = random.randint(2,10)
    x.max_travel_distance = 10-x.mobility//2
    return x
        
class Symptom(Model):
    def defaults(self):
        self.name = "cough"
        self.visibility = 1  #How likely to detect/how likely they are in the hospital
        self.severity = 1  #How much discomfort caused, highest levels can kill
        self.spread = 2   #Modifies spread
        self.spread_types = ["air"]   #Spread modifier only if type matches
    def __repr__(self):
        return self.name
        
class Stage(Model):
    def defaults(self):
        self.length = 2   #Number of turns for this stage
        self.spread = 1  #Power of contagion to spread to another host
        self.weakness = 1  #Weakness to drugs
        self.symptoms = []   #What symptoms appear
    def mspread(self,types):
        """Return spread modified by symptoms"""
        sp = self.spread
        if not sp:
            return 0
        for s in self.symptoms:
            for st in s.spread_types:
                if st in types:
                    sp+=s.spread
                    break
        return sp
        
class Disease(Model):
    names = []
    def defaults(self):
        self.stages = []
        self.spread_methods = ["touch"]       #How disease is spread
        
        self.age = 0                                     #Current life
        self.mutations = 0                              #How many mutations we have gone through
        
        self.mutate_chance = 4              #Chance out of 100 to mutate at all
        
        self.add_stage_chance = 0               #In mutation how likely to add a stage
        self.remove_stage_chance = 0            #In mutation how likely to remove a stage
        
        self.alter_stage_chance = 1                 #how likely to change a stage
        self.add_symptom_chance = 1               #Add a symptom to a changing stage
        self.remove_symptom_chance = 1          #Remove a symptom from a changing stage
        self.change_symptom_chance = 1          #Change a symptom
        
        self.add_spread_method_chance = 1       #How likely to add a new spread method
        self.alter_spread_method_chance = 2     #How likely to change a spread method to something else
        
        self.name = "H1N16"                         #Name given to disease once discovered, used as seed for random?
        self.type = "deadly"
    def get_stage(self):
        """Gets the stage we are currently on"""
        c = 0
        for s in self.stages:
            c += s.length
            if c>self.age:
                return s
        #All stages complete, we are no longer infected!
        return None
    def symptoms(self):
        s = self.get_stage()
        if not s:
            return []
        return s.symptoms
    def turn(self,context):
        if self.name not in self.names:
            self.names.append(self.name)
        context["disease"] = self
        self.spread(context["location"])
        self.age += 1
        if not self.get_stage():
            context["population"].remove_disease(self)
    def spread(self,location):
        s = self.get_stage()
        if not s:
            return
        people = [p for p in location.people if self.name not in p.immunities]
        best = None
        bscore = 0
        m = s.mspread(self.spread_methods)
        if not m:
            return
        for p in people:
            score = m-p.lifestyle
            if score>bscore:
                best = p
                bscore = score
        if best:
            infect(self,best)
    def copy(self):
        """Copy disease so it can be used on a new population"""
        a = {}
        for k in self.attr:
            if k in ["age","mutations"]:
                continue
            a[k] = self.__dict__[k]
        d = Disease(**a)
        d.mutate()
        return d
    def mutate(self):
        if random.randint(0,100)<self.mutate_chance:
            self.name = "H%s"%random.randint(0,500000)
            while self.name in self.names:
                self.name = "H%s"%random.randint(0,500000)
            self.names.append(self.name)
            mutate = ["alts"]*self.alter_stage_chance+["addspr"]*self.add_spread_method_chance+["alterspr"]*self.alter_spread_method_chance+["nil"]*10
            mutate = random.choice(mutate)
            if mutate=="alts":
                sym = ["add"*self.add_symptom_chance]+["remove"*self.remove_symptom_chance]+["change"*self.change_symptom_chance]
                sym = random.choice(sym)
                s = random.choice(self.stages[:-1])
                if sym=="add":
                    symptom = random.choice([cough,diarrhea,stomach_pain,headache])
                    s.symptoms.append(symptom)
                elif sym=="remove":
                    if s.symptoms:
                        l = list(s.symptoms)
                        random.shuffle(l)
                        s.symptoms.remove(l[0])
                elif sym=="change":
                    if s.symptoms:
                        i = random.randint(0,len(s.symptoms)-1)
                        s.symptoms[i] = random.choice([cough,diarrhea,stomach_pain,headache])
            elif mutate=="addspr":
                self.spread_methods.append(random.choice(["air","water","touch","sex","sigh","longair"]))
            elif mutate=="alterspr":
                random.shuffle(self.spread_methods)
                self.spread_methods[0] = random.choice(["air","water","touch","sex","sigh","longair"])
            return 1
        return 0
        

def inhabit(location,population):
    location.people.append(population)
    population.location = location
def infect(disease,population):
    """After building a disease, inflict it on a population."""
    if len(population.illnesses)<2:
        population.illnesses.append(disease.copy())
        population.immunities.add(disease.name)
    
cough = Symptom(name="cough",visibiliy=1,severity=3,spread=2,spread_types=['air'])
diarrhea = Symptom(name="diarrhea",visibility=1,severity=4,spread=1,spread_types=['touch'])
stomach_pain = Symptom(name="stomach pain",visibility=5,severity=1,spread=0)
headache = Symptom(name="headache",visibility=2,severity=4,spread=0)
death = Symptom(name="death",visibility=10,severity=10,spread=2,spread_types=['touch','air'])

badvirus = Disease(
                stages=[
                    Stage(length=2,spread=0,weakness=2,symptoms=[cough]),
                    Stage(length=4,spread=1,weakness=2,symptoms=[cough]),
                    Stage(length=2,spread=1,weakness=1,symptoms=[cough,diarrhea,stomach_pain]),
                    Stage(length=1,spread=2,weakness=1,symptoms=[death])
                    ],
                spread_methods=["air"],
                name="H1N8M7G9",
                type="deadly"
                )
nicevirus = Disease(
                stages=[
                    Stage(length=1,spread=0,weakness=2,symptoms=[cough]),
                    Stage(length=2,spread=1,weakness=1,symptoms=[cough]),
                    Stage(length=1,spread=2,weakness=1,symptoms=[cough])
                    ],
                alter_stage_chance=0,
                spread_methods=["air"],
                name="H2N8M7G8",
                type="benign"
                )

#~ mc = 0
#~ nv = badvirus
#~ for x in range(500):
    #~ nv = nv.copy()
    #~ mc += nv.mutate()
#~ print mc
if __name__=="__main__":
    x = Disease(
                    stages=[
                        Stage(length=1,spread=0,weakness=2,symptoms=[cough]),
                        Stage(length=2,spread=1,weakness=1,symptoms=[cough,diarrhea,stomach_pain]),
                        Stage(length=1,spread=2,weakness=1,symptoms=[death])
                        ],
                    spread_methods=["air"],
                    name="H1N8M7G9"
                    )
    bob = Population(name="Bob")
    infect(x,bob)
    anna = Population(name="Anna")
    infect(x,anna)
    jane = Population(name="Jane")
    seattle = Location()
    inhabit(seattle,anna)
    inhabit(seattle,bob)
    inhabit(seattle,jane)
    for i in range(10):
        inhabit(seattle,Population(name="dummy%s"%i))
    t = 0
    dead = 0
    while seattle.people:
        print t
        t += 1
        for p in seattle.people:
            print p.name,p.symptoms()
        print "# infected:",len([x for x in seattle.people if x.illnesses])
        d = {}
        seattle.turn(d)
        dead += d.get("dead",0)
        print "# dead:",dead

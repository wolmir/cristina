#-------------------------------------------------------------------------------
#
#   Mutagenesis - Game
#
#-------------------------------------------------------------------------------

import itertools
from random import choice
from pygame import Surface, SRCALPHA
from humerus.albow.root import schedule_call
from humerus.albow.resource import get_sound
from humerus.albow.dialogs import ask
from humerus.hgame import HGame
from lsystem import LSystem
from mutation import mutate_dna, append_remaining, cross_rhs

class Chromosome(object):

	def __init__(self, lhs, rhs):
		self.lhs = lhs
		self.rhs = rhs
	
	def __str__(self):
		return "%s -> %s" % (self.lhs, self.rhs)
	
	def clone(self):
		return Chromosome(self.lhs, self.rhs)
	
	def dump(self):
		print self.lhs, "->", self.rhs

#class ChromosomePair(list):
#
#	def __init__(self, a, b):
#		list.__init__(self, (a, b))
#	
#	def clone(self):
#		cs = [c.clone() for c in self]
#		return ChromosomePair(*cs)
#	
#	def dump(self):
#		for c in self:
#			c.dump()

#-------------------------------------------------------------------------------

plant_seed = "A"

initial_chromosomes = [
	Chromosome("A", "wA")
]

test_chromosomes = [
	Chromosome("A", "wwwwB"),
	Chromosome("B", "[A][A]"),
	Chromosome("B", "[L][L]A"),
	Chromosome("B", "[C][C]"),
	Chromosome("C", "wwwwD"),
	Chromosome("D", "[C][C]"),
	Chromosome("D", "[L][L]C"),
	Chromosome("D", "E"),
	Chromosome("E", "[G][C]"),
	Chromosome("E", "[C][G]"),
	Chromosome("G", "wO"),
	Chromosome("G", "wwF"),
	Chromosome("L", "{7cllwrwrw}"),
	Chromosome("O", "1c5do"),
	Chromosome("F", "5b[P]S"),
	Chromosome("P", "{6clllwrw}"),
	Chromosome("S", "3c6do"),
]

#-------------------------------------------------------------------------------

class NoPicklePrivates(object):

	def __getstate__(self):
		state = self.__dict__.copy()
		for name in state.keys():
			if name.startswith("_"):
				del state[name]
		return state
	
	def __setstate__(self, d):
		self.__dict__.update(d)

#-------------------------------------------------------------------------------

class DNA(NoPicklePrivates):

	_lsystem = None
	
	def __init__(self, chromosomes):
		#self.chromosome_pairs = chromosomes or []
		self.chromosomes = chromosomes or []
	
	def clone(self):
		#new_chromosomes = [pair.clone() for pair in self.chromosome_pairs]
		new_chromosomes = [c.clone() for c in self.chromosomes]
		return DNA(new_chromosomes)
	
	def get_lsystem(self):
		lsys = self._lsystem
		if not lsys:
			lsys = LSystem()
			for c in self.chromosomes:
					lsys.add_production(c.lhs, c.rhs)
			self._lsystem = lsys
			#print "DNA: LSystem:" ###
			#lsys.dump() ###
		return lsys
	
	lsystem = property(get_lsystem)
	
	def dump(self):
#		for pair in self.chromosome_pairs:
#			pair.dump()
		for c in self.chromosomes:
			c.dump()
		print
	
#initial_dna = DNA(initial_chromosomes)
initial_dna = DNA(test_chromosomes)

#-------------------------------------------------------------------------------

class Plant(NoPicklePrivates):

	max_structure_length = 2000

	_buffer = None
	_thumbnail = None
	pedigree = ""

	def __init__(self, number, dna):
		self.number = number
		self.dna = dna
		self.structure = plant_seed
	
	def __str__(self):
		return "Plant#%s" % self.number
	
	def __getstate__(self):
		d = NoPicklePrivates.__getstate__(self)
		thumb = self._thumbnail
		if thumb:
			d['thumbnail_size'] = thumb.get_size()
			d['thumbnail_data'] = thumb.get_buffer().raw
		return d
	
	def __setstate__(self, d):
		size = d.pop('thumbnail_size', None)
		data = d.pop('thumbnail_data', None)
		if size and data:
			surf = Surface(size, SRCALPHA)
			surf.get_buffer().write(data, 0)
			self._thumbnail = surf
		NoPicklePrivates.__setstate__(self, d)
	
	def growth_step(self):
		lsys = self.dna.lsystem
		self.structure = lsys.substitute_string(self.structure)
		self._buffer = None
		self._thumbnail = None
	
	def get_buffer(self):
		return self._buffer
	
	def set_buffer(self, buffer):
		self._buffer = buffer
	
	buffer = property(get_buffer, set_buffer)

	def growth_tick(self):
		if len(self.structure) < self.max_structure_length:
			self.growth_step()
	
	def restart_growth(self):
		self.structure = plant_seed
	
	def get_description(self):
		result = "Specimen %s" % self.number
		ped = self.pedigree
		if ped:
			result = "%s (%s)" % (result, ped)
		return result

#-------------------------------------------------------------------------------

class GameState(object):

	def __init__(self):
		self.specimens = []
		self.specimens.append(Plant(1, initial_dna))
		self.current_specimen = self.specimens[0]
		self.last_specimen = None
		self.next_plant_number = 2

#-------------------------------------------------------------------------------

class Game(HGame):

	app_magic = "MuGn"
	save_file_suffix = ".mutgam"

	growth_step_time = 100 # ms
	
	radiation_sound = get_sound("radiation.ogg")
	mutation_time = 1000 # ms
	
	breeding_sound = get_sound("bees.ogg")
	breeding_time = 1500 # ms
	
	trash_sound = get_sound("slash.ogg")
	
	def new_plant(self, dna):
		n = self.state.next_plant_number
		self.state.next_plant_number = n + 1
		plant = Plant(n, dna)
		return plant

	def init_timing(self):
		schedule_call(self.growth_step_time, self.growth_tick, repeat = True)

	def get_current_specimen(self):
		return self.state.current_specimen
	
	def set_current_specimen(self, plant):
		state = self.state
		if state.current_specimen is not plant:
			state.last_specimen = state.current_specimen
			state.current_specimen = plant
	
	current_specimen = property(get_current_specimen, set_current_specimen)
	
	def get_last_specimen(self):
		return self.state.last_specimen
		
	last_specimen = property(get_last_specimen)
	
	def get_specimen_no(self, i):
		return self.state.specimens[i]
	
	num_specimens = property(lambda self: len(self.state.specimens))
	
	def select_specimen_no(self, i):
		state = self.state
		self.current_specimen = state.specimens[i]
	
	def specimen_no_is_selected(self, i):
		state = self.state
		return state.current_specimen is state.specimens[i]

	def new_state(self):
		return GameState()
	
	def begin_frame(self):
		pass
		#print "Game.begin_frame"

	def add_specimen(self, plant):
		self.state.specimens.append(plant)
		self.current_specimen = plant
	
	def mutate_current_specimen(self):
		self.radiation_sound.play()
		schedule_call(self.mutation_time, self.do_mutation)
	
	def do_mutation(self):
		plant = self.current_specimen
		if plant:
			new_plant = self.mutate_plant(plant)
			new_plant.pedigree = "mutation of %s" % plant.number
			self.add_specimen(new_plant)
	
	def growth_tick(self):
		plant = self.current_specimen
		if plant:
			plant.growth_tick()
	
	def restart_growth(self):
		plant = self.current_specimen
		if plant:
			plant.restart_growth()
	
	def breed(self):
		self.breeding_sound.play()
		schedule_call(self.breeding_time, self.do_breeding)
	
	def do_breeding(self):
		plant1 = self.last_specimen
		plant2 = self.current_specimen
		if plant1 and plant2:
			new_dna = self.cross_dna(plant1.dna, plant2.dna)
			new_plant = self.new_plant(new_dna)
			new_plant.pedigree = "%s + %s" % (plant1.number, plant2.number)
			self.add_specimen(new_plant)

	def discard_current_specimen(self):
		plant = self.current_specimen
		if plant:
			if ask("Discard %s?" % plant.get_description()) == "OK":
				self.trash_sound.play()
				self.state.specimens.remove(plant)
				self.current_specimen = None

	def mutate_plant(self, plant):
		new_dna = plant.dna.clone()
		mutate_dna(new_dna)
		print "\nMutated DNA:"
		new_dna.dump()
		new_plant = self.new_plant(new_dna)
		return new_plant
	
	def cross_dna(self, dna1, dna2):
		print "\nParent 1 DNA:" ###
		dna1.dump() ###
		print "Parent 2 DNA:" ###
		dna2.dump() ###
		cl1 = dna1.chromosomes
		cl2 = dna2.chromosomes
		new_chromosomes = [cross_chromosomes(c1, c2) for (c1, c2) in zip(cl1, cl2)]
		append_remaining(new_chromosomes, cl1, cl2)
		result = DNA(new_chromosomes)
		print "Resulting DNA:" ###
		result.dump() ###
		return result

#-------------------------------------------------------------------------------

	
def cross_chromosomes(c1, c2):
	lhs = choice([c1.lhs, c2.lhs])
	rhs = cross_rhs(c1.rhs, c2.rhs)
	return Chromosome(lhs, rhs)

#-------------------------------------------------------------------------------

game = Game()

##################################################################
#
#   Humerus - Game object with level editing
#
#   A subclass of HGame providing support for a level editor.
#
#   Abstract methods:
#
#      create_level(self)
#         Should create and return a new, empty level object.
#
#   Overridable methods:
#
#      pickle_level(self, pickler, level)
#         Should pickle the given level using the given picker.
#         The default implementation pickles the level object
#         directly.
#
#      unpickle_level(self, unpickler)
#         Should unpickle a level from the given unpickler
#         and return an object representing it. The default
#         implementation unpickles the level object directly.
#
##################################################################

import os
from tempfile import mkstemp
from cPickle import Pickler, Unpickler
from gui.albow.dialogs import ask
from hgame import check_file_magic, check_file_version
from hlgame import HLGame

#------------------------------------------------------------------------

class HEGame(HLGame):
	#  editing_level_dir    string     Dir for saving level being edited
	#  level_needs_saving   boolean    Changes to level need saving

	#  Level file constants

	level_file_version = 1         #  Version number of data we write
	level_min_version = 1          #  Minimum data version we understand
	level_app_version = (1, 0, 0)  #  Earliest app version that understands what we write
	level_version_ranges = {}      #  For earlier data versions, version -> (min_app_version, max_app_version)
	level_file_magic = "LEVL"      #  Magic for recognising type of data
	
	#  Default values of instance variables

	editing_level_dir = None
	level_needs_saving = False

	def set_playing_level_dir(self, dir):
		"""Sets the directory from which levels are being or to be
		played. If different from the current editing level dir,
		clears the editing level dir so that a pathname will be asked
		for the next time a level is saved."""
		#print "HEGame.set_playing_level_dir:", repr(dir) ###
		HLGame.set_playing_level_dir(self, dir)
		if self.editing_level_dir != self.playing_level_dir:
			self.editing_level_dir = None
	
	def get_level_save_dir(self):
		"""Returns the default directory in which to save the level
		being edited. Uses the editing level dir if one is set, otherwise
		the playing level dir. Will return the default custom level dir
		instead of the standard level dir unless a level has previously been
		saved there explicitly."""
		dir = self.editing_level_dir
		#print "HEGame.get_level_save_dir: editing_level_dir =", dir ###
		if not dir:
			dir = self.playing_level_dir
			#print "...playing_level_dir =", dir ###
			#print "...std level dir =", self.get_std_level_dir() ###
			if not dir or dir == self.get_std_level_dir():
				#print "...substituting mods dir" ###
				dir = self.get_default_custom_level_dir()
		return dir

#	def get_custom_level_path(self):
#		"""Returns the full pathname of the level currently being edited,
#		or None if no level is being edited."""
#		dir = self.level_set_dir
#		setname = self.level_set_name
#		filename = self.level_name
#		if not (dir and filename):
#			return None
#		if setname:
#			dir = os.path.join(dir, setname)
#		return os.path.join(dir, filename)
	
#	def get_custom_level_dir(self):
#		"""Returns the full pathname of the directory containing the level
#		being edited, or the default custom levels directory."""
#		dir = self.get_custom_level_set_dir()
#		setname = self.level_set_name
#		if setname:
#			dir = os.path.join(dir, setname)
#		return dir
	
	def mark_current_level_completed(self):
		"""If the level is not being tested, add it to the list of completed levels
		for the current game."""
		if not self.testing:
			HLGame.mark_current_level_completed(self)

	def load_level(self, path):
		HLGame.load_level(self, path)
		self.level_needs_saving = False

	def read_level(self, path):
		f = open(path, "rb")
		try:
			check_file_magic(f, self.app_magic, "level")
			check_file_magic(f, self.level_file_magic, "level")
			p = Unpickler(f)
			file_version = p.load()
			app_version = p.load()
			check_file_version(file_version, app_version,
				self.level_min_version, self.level_file_version,
				self.level_version_ranges)
			level = self.unpickle_level(p)
		finally:
			f.close()
		return level

	def unpickle_level(self, unpickler):
		return unpickler.load()

	def write_level(self, path):
		fd, tmp_path = mkstemp(dir = os.path.dirname(path))
		f = os.fdopen(fd, "wb")
		try:
			f.write(self.app_magic)
			f.write(self.level_file_magic)
			p = Pickler(f, 2)
			p.dump(self.level_file_version)
			p.dump(self.level_app_version)
			self.pickle_level(p, self.level)
		finally:
			f.close()
		try:
			os.unlink(path)
		except EnvironmentError:
			pass
		os.rename(tmp_path, path)
		#self.set_custom_level_path(path)
		dir, name = os.path.split(path)
		self.playing_level_dir = dir
		self.editing_level_dir = dir
		self.level_name = name

	def pickle_level(self, pickler, level):
		pickler.dump(level)

	def new_level(self):
		self.level = self.create_level()
		self.playing_level = None
		self.level_name = None
		self.level_needs_saving = False
		#self.level.reset()

	def level_changed(self):
		"""Should be called by the level editor whenever the user modifies
		the level in any way."""
		self.level_needs_saving = True


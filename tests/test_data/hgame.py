############################################################################
#
#   Humerus - Game object
#
#   The central object of a game without levels. Provides
#   facilities for saving and restoring the state of a game.
#   Designed to be used in conjunction with an HShell.
#
#   Information to be stored in the saved game file should
#   be kept as pickleable attributes of the game's 'state'
#   object.
#
#   Abstract methods:
#
#      new_state(self)
#         Should create and return a state object for a new game.
#
#      game_is_completed(self):
#         Should return a true value if the game is completed.
#         The value returned will be passed to the game_completed()
#         method of the HShell, and can be used e.g. to distinguish
#         between winning and losing conditions.
#
############################################################################

import os
from tempfile import mkstemp
from cPickle import Pickler, Unpickler
from gui.albow.dialogs import ask, alert

#---------------------------------------------------------------------------

class HGame(object):
	#  save_dir             string     Last save file dir
	#  save_name            string     Last save file name
	#  unsaved_progress     boolean    Game progress needs saving
	#  state                object     Any additional game state to be saved
		
	app_version = (1, 0, 0)  #  Version number of the game application
	app_magic = "????"

	#  Saved game file constants

	save_file_version = 1         #  Version number of data we write
	save_min_version = 1          #  Minimum data version we understand
	save_app_version = (1, 0, 0)  #  Earliest app version that understands what we write
	save_version_ranges = {}      #  For earlier data versions, version -> (min_app_version, max_app_version)
	save_file_magic = "SAVE"      #  Magic for recognising type of data
	
	#  Filenames and  suffixes
	
	save_file_default_name = "SavedGame"
	save_file_suffix = ".gam"     #  Saved game files
	
	# The following path is relative to the directory containing
	# the Game directory or the .app bundle.
	
	default_save_dir_name = "Saves"

	#  Default values of instance variables

	state = None
	save_dir = None
	save_name = None
	unsaved_progress = False
	
	def game_in_progress(self):
		"""Return true if a saveable game state exists."""
		return self.play_in_progress()

	def play_in_progress(self):
		"""Return true if it is appropriate to show the playing screen."""
		return self.state and not self.game_is_completed()
	
	def game_is_completed(self):
		"""Return true if the game is completed. Return value may be used
		to distinguish different completion states, e.g. win/lose."""
		return False
	
	def game_needs_saving(self):
		return self.game_in_progress() and self.unsaved_progress

	def new_game(self):
		self.state = self.new_state()
		self.unsaved_progress = False
		self.save_name = None
	
	def new_state(self):
		raise NotImplementedError("HGame subclass did not implement new_state()")
	
	def load_game(self, path):
		"""Restores a saved game from the specified path."""
		f = open(path, "rb")
		check_file_magic(f, self.app_magic, "saved game")
		check_file_magic(f, self.save_file_magic, "saved game")
		p = Unpickler(f)
		file_version = p.load()
		app_version = p.load()
		check_file_version(file_version, app_version,
			self.save_min_version, self.save_file_version,
			self.save_version_ranges)
		data = p.load()
		f.close()
		self.restore_save_data(data)
		self.set_save_path(path)
		self.unsaved_progress = False
	
	def restore_save_data(self, data):
		self.__dict__.update(data)

	def save_game(self, path):
		"""Saves current game progress in the specified file."""
		fd, tmp_path = mkstemp(dir = os.path.dirname(path))
		f = os.fdopen(fd, "wb")
		f.write(self.app_magic)
		f.write(self.save_file_magic)
		p = Pickler(f, 2)
		p.dump(self.save_file_version)
		p.dump(self.save_app_version)
		data = {}
		self.collect_save_data(data)
		p.dump(data)
		f.close()
		try:
			os.unlink(path)
		except EnvironmentError:
			pass
		os.rename(tmp_path, path)
		self.set_save_path(path)
		self.unsaved_progress = False
	
	def collect_save_data(self, data):
		data['state'] = self.state

	def get_save_dir(self):
		"""Returns the full pathname of the directory last used to save a
		game, or the default save directory."""
		return self.save_dir or self.get_default_dir(self.default_save_dir_name)
	
	def get_save_path(self):
		"""Returns the default path that should be used for saving the game."""
		return os.path.join(self.get_save_dir(),
			self.save_name or self.save_file_default_name)
	
	def set_save_path(self, path):
		"""Record the last path used to save a game."""
		self.save_dir, self.save_name = os.path.split(path)
	
	def get_default_dir(self, name):
		"""Find the full path of a directory relative to the application."""
		from gui.albow.resource import resource_dir
		d = os.path.dirname
		base = d(d(resource_dir))
		return os.path.join(base, name)
	
	def timer_event(self, event):
		self.begin_frame()
		return True
	
	def begin_frame(self):
		pass

#---------------------------------------------------------------------------

def check_file_magic(f, expected, what):
	magic = f.read(len(expected))
	if magic <> expected:
		raise EnvironmentError("Does not seem to be a %s file." % what)

def check_file_version(file_version, app_version,
		min_version, cur_version, version_ranges):
	if not min_version <= file_version <= cur_version:
		if file_version > cur_version:
			mess = "Can only be opened by version %s.%s.%s or later." % app_version
		else:
			v1, v2 = version_ranges[file_version]
			vs1 = "%s.%s.%s" % v1
			vs2 = "%s.%s.%s" % v2
			mess = "Can only be opened by versions %s to %s." % (vs1, vs2)
		raise EnvironmentError(mess)

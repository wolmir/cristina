############################################################################
#
#   Humerus - Game object with levels
#
#   The central object of a game made up of a series of levels.
#   Provides facilities for remembering which levels have been
#   completed and saving this information in a saved-game file.
#   Designed to be used in conjunction with an HLShell.
#
#   Levels are kept in a directory, one level per file. The
#   order of playing is determined by lexicographically sorting
#   the filenames. It is recommended to prefix each filename by
#   a level number with leading zeroes.
#
#   By default, levels are taken from a directory called
#   "levels.xxx" in the Resources directory, where "xxx" is
#   your chosen level set suffix. Support is provided for
#   letting the user choose another set of levels to play.
#
#   The level object loaded from a level file is not actually
#   played, but is used as a template from which to clone levels
#   for playing. By default, the clone is made using copy.deepcopy(),
#   but this can be changed by overriding the clone_level() method.
#
#   If any information besides the list of completed levels needs
#   to be stored in the saved game file, it should be kept as
#   pickleable attributes of the game's 'state' object.
#
#   Abstract methods:
#
#      read_level(path)
#         Should read a level template from the specified file and
#         return an object representing it.
#
#      new_state()
#         Should create and return a state object for a new game.
#         May be left unimplemented if no additional game state needs
#         to be saved.
#
#   A level can be represented by any object having the following
#   methods:
#
#      level_is_completed()
#         Should return a positive if the player has completed the level
#         successfully, a negative value if it is completed unsuccesfully,
#         and zero if it is not yet completed.
#
#      begin_frame()
#         Called in reponse to each timer event whenever the game is
#         not paused.
#
############################################################################

import os, gc
from copy import deepcopy
from tempfile import mkstemp
from cPickle import Pickler, Unpickler
from gui.albow.resource import resource_path
from gui.albow.dialogs import ask
from gui.albow.file_dialogs import look_for_file_or_directory
from hgame import HGame, check_file_version

#------------------------------------------------------------------------

class HLGame(HGame):
	#  levels_completed     [string]   List of level names
	#  level                custom     Level template currently loaded
	#  playing_level        custom     Level instance currently being played
	#  playing_level_dir    string     Dir containing levels being played
	#  level_name           string     Name of level being played or edited
  #  testing              boolean    Test Level command in effect
		
	#  Filenames and  suffixes
	
	level_file_suffix = ".lev"  #  Level files
	level_set_suffix = ".lvs"   #  Level set directories
	
	#  Standard level directory, relative to Resources (without suffix)
	
	std_level_dir_name = "levels"

	# The following path is relative to the directory containing
	# the Game directory or the .app bundle.
	
	default_custom_level_dir_name = "Mods"
		
	#  Optional feature flags
	
	disable_gc_during_play = False

	#  Default values of instance variables

	level = None
	playing_level = None
	playing_level_dir = None
	level_name = None
	testing = False

	def __init__(self):
		self.levels_completed = []

	def game_in_progress(self):
		"""Returns true if a level is loaded and a set of levels is being played
		(i.e. not just an isolated stand-alone level)."""
		return self.level_loaded() and self.playing_level_set()
	
	def play_in_progress(self):
		return self.level_in_progress()
	
	def level_loaded(self):
		"""Returns true if a level is currently loaded (but not necessarily
		being played)."""
		return self.level is not None
	
	def level_started(self):
		"""Returns true if a level has been started."""
		return self.playing_level is not None

	def level_in_progress(self):
		"""Returns true if a level is being played and it is not yet
		completed."""
		return self.level_started() and not self.level_is_completed()
	
	def level_is_completed(self):
		"""Return true if the currently loaded level has been completed.
		A positive value indicates successful completion, a negative
		value indicates failure."""
		level = self.playing_level
		return level and level.level_is_completed()
	
	def playing_level_set(self):
		"""Returns true if a level set is being played (whether a level is
		loaded or not)."""
		dir = self.playing_level_dir
		return dir and dir.endswith(self.level_set_suffix)
	
	def unload_level(self):
		"""Stop playing and remove any level currently loaded."""
		self.stop_level()
		self.playing_level = None
		self.level = None
		self.level_name = None
	
	def start_level(self):
		"""Start or restart the currently loaded level."""
		self.playing_level = self.clone_level(self.level)
		prepare = getattr(self.playing_level, 'prepare', None)
		if prepare:
			prepare()
		if self.disable_gc_during_play:
			gc.disable()
	
	def clone_level(self, level_template):
		"""Given a level template, return a level to be played."""
		return deepcopy(level_template)
	
	def stop_level(self):
		"""Shut down any level currently being played."""
		if self.disable_gc_during_play:
			gc.enable()
		self.playing_level = None

	def new_game(self):
		"""Prepare for a new game by discarding the current level, clearing the
		list of completed levels and saved game file name."""
		self.stop_level()
		self.level = None
		del self.levels_completed[:]
		HGame.new_game(self)
	
	def new_state(self):
		return None
	
	def load_game(self, path):
		"""Restores current level set and saved game progress from the specified
		file. If the level set can't be found, the user will be asked to look
		for it."""
		HGame.load_game(self, path)
	
	def restore_save_data(self, data):
		level_set_path = data.pop('level_set_path')
		if not level_set_path:
			level_set_path = self.get_std_level_dir()
		if not os.path.exists(level_set_path):
			level_set_path = self.look_for_level_set(level_set_path)
			if not level_set_path:
				raise Cancel
		self.stop_level()
		self.level = None
		self.set_playing_level_dir(level_set_path)
		HGame.restore_save_data(self, data)

	def look_for_level_set(self, orig_path):
		name = os.path.basename(orig_path)
		prompt = "Can't find '%s'. Would you like to look for it?" % name
		if ask(prompt, ["Yes", "No"]) == "Yes":
			return look_for_file_or_directory(name)
	
	def save_game(self, path):
		"""Saves current game progress in the specified file. If a non-standard
		level set is being played, the pathname of the level set is also
		recorded in the saved game file."""
		HGame.save_game(self, path)
	
	def collect_save_data(self, data):
		level_set_path = self.playing_level_dir
		if level_set_path == self.get_std_level_dir():
			level_set_path = ""
		data['level_set_path'] = level_set_path
		data['levels_completed'] = self.levels_completed
		HGame.collect_save_data(self, data)

	def get_std_level_dir(self):
		"""Returns the full pathname of the directory containing the standard
		levels."""
		path = resource_path(self.std_level_dir_name) + self.level_set_suffix
		return os.path.abspath(path)
	
	def get_playing_level_dir(self):
		"""Returns the full pathname of the last directory from which a
		level was played, or the default level directory."""
		path = self.playing_level_dir
		if not path:
			path = self.get_std_level_dir()
		return path
	
	def mark_current_level_completed(self):
		"""Add the current level to the list of completed levels for the
		current game."""
		if not self.testing and self.playing_level_set() and \
				not self.is_final_level():
			name = self.level_name
			if name not in self.levels_completed:
				self.levels_completed.append(name)
				self.unsaved_progress = True
	
	def is_final_level(self):
		"""If the current level is one that should not be progressed beyond
		even when it is completed, return true."""
		return False
	
	def load_next_uncompleted_level(self):
		path = self.next_uncompleted_level_path()
		if path:
			self.load_level(path)
		else:
			self.stop_level()
			self.level = None

	def next_uncompleted_level_path(self):
		"""Returns the full pathname of the next level file in the current
		level set that is not in the list of completed levels. If no such
		level is found, returns None."""
		ext = self.level_file_suffix
		dir = self.get_playing_level_dir()
		if os.path.isdir(dir):
			names = [name for name in os.listdir(dir) if name.endswith(ext)]
			names.sort()
			for name in names:
				if name not in self.levels_completed:
					return os.path.join(dir, name)
		return None
	
	def load_level(self, path):
		level = self.read_level(path)
		self.stop_level()
		self.level = level
		self.level_needs_saving = False
		dir, name = os.path.split(path)
		self.set_playing_level_dir(dir)
		self.level_name = name
	
	def set_playing_level_dir(self, dir):
		"""Sets the directory from which levels are being or are to be played."""
		self.playing_level_dir = dir

	def begin_frame(self):
		"""Calls the begin_frame() method of the current level, if any."""
		level = self.playing_level
		if level:
			level.begin_frame()
	
	def get_custom_level_set_dir(self):
		"""If a custom level set is being played or edited, returns the full
		pathname of the directory containing that level set. Otherwise,
		returns the default custom levels directory."""
		dir = self.playing_level_dir
		if dir and dir.endswith(self.level_set_suffix) \
				and dir != self.get_std_level_dir():
			return os.path.dirname(dir)
		else:
			return self.get_default_custom_level_dir()
	
	def get_default_custom_level_dir(self):
		return self.get_default_dir(self.default_custom_level_dir_name)

	def level_number_and_title(self):
		"""Get level number and title from the current level filename.
		Expects the filename to be formatted as '<number>-<title>'. Underscores
		in the title are replaced by spaces. Returns a tuple (number, name).
		If there is no number, 0 is returned for the number."""
		number = 0
		title = ""
		name = self.level_name
		if name:
			name = os.path.splitext(name)[0].replace("_", " ")
			parts = name.split("-", 1)
			if len(parts) == 2:
				title = parts[1]
				try:
					number = int(parts[0])
				except ValueError:
					pass
			else:
				title = name
		return number, title

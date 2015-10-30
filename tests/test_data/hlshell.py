################################################################
#
#   Humerus - HLShell
#
#   An HShell subclass designed to be used with an HLGame.
#
################################################################

import os
import pygame.display
from gui.albow.root import Cancel
from gui.albow.dialogs import alert
from gui.albow.file_dialogs import request_old_filename
from hshell import HShell

#---------------------------------------------------------------------------

class HLShell(HShell):

	has_levels = True

	def load_file(self, path):
		"""Load a level set, level or saved game dpending on the filename suffix.
		Reports errors to the user."""
		if path.endswith(self.game.level_set_suffix):
			self.load_level_set(path)
		elif path.endswith(self.game.level_file_suffix):
			self.load_level_file(path)
		else:
			HShell.load_file(self, path)
	
	def new_game_cmd(self):
		"""Implementation of the 'New Game' command."""
		self.ask_save()
		game = self.game
		game.new_game()
		self.load_next_uncompleted_level()
		if game.level_loaded():
			self.restart_level()
		else:
			self.no_levels_found()
			self.show_main_menu_screen()
	
	def no_levels_found(self):
		"""Called when a level set is found to contain no levels."""
		alert("No levels found.")
	
	def restore_game(self, path):
		"""Restore a saved game from the specified path and start playing
		the next uncompleted level. Reports errors to the user."""
		self.load_game_file(path)
		self.load_next_uncompleted_level()
		self.restart_level()
		
	def resume_game_cmd(self):
		"""Implementation of the 'Resume Game' command."""
		self.resume_game()
	
	def restart_level_enabled(self):
		"""Enable checker for the 'Restart Level' command."""
		return self.game.level_in_progress()
	
	def restart_level_cmd(self):
		"""Implementation of the 'Restart Level' command."""
		self.restart_level()
	
	def restart_level(self):
		if self.game.level_loaded():
			if self.game.level_in_progress():
				self.game.stop_level()
			self.game.start_level()
			self.show_play_screen()
	
	def load_next_uncompleted_level(self):
		"""Load the next uncompleted level, if any. Reports errors to the user.
		If there are no more levels, sets game.level to None."""
		path = self.game.next_uncompleted_level_path()
		if path:
			self.load_level_file(path)
		else:
			self.game.unload_level()

	def load_level_file(self, path):
		"""Load the specified level file. Reports errors to the user. Raises
		Cancel if an error occurs."""
		try:
			self.game.load_level(path)
		except EnvironmentError, e:
			alert("Unable to load '%s': %s" % (os.path.basename(path), e))
			raise Cancel

	def open_level_set_cmd(self):
		"""Implementation of the 'Play Custom Levels' command."""
		self.ask_save()
		path = request_old_filename(suffixes = [self.game.level_set_suffix],
			directory = self.game.get_custom_level_set_dir())
		if not path:
			raise Cancel
		self.load_level_set(path)
		self.restart_level()
	
	def load_level_set(self, path):
		"""Make the specified directory the current custom level set and load
		the first level. Reports errors to the user. Raises Cancel if an error
		occurs."""
		game = self.game
		game.set_playing_level_dir(path)
		game.new_game()
		self.load_next_uncompleted_level()
		if not self.game.level_loaded():
			self.no_levels()

	def check_for_completion(self):
		result = self.game.level_is_completed()
		if result:
			self.level_completed(result)
	
	def level_completed(self, result):
		if result > 0:
			self.level_won(result)
		elif result < 0:
			self.level_lost(result)
	
	def level_won(self, result):
		game = self.game
		game.mark_current_level_completed()
		if not game.is_final_level():
			self.load_next_uncompleted_level()
			if self.game.level_loaded():
				self.restart_level()
				return
		self.game_completed(result)
	
	def level_lost(self, result):
		self.game.stop_level()
		self.show_main_menu_screen()

################################################################
#
#   Humerus - HEShell
#
#   A Shell subclasss designed to be used with an HEGame.
#
################################################################

import os
from gui.albow.root import Cancel
from gui.albow.dialogs import alert, ask
from gui.albow.file_dialogs import request_old_filename, request_new_filename
from hlshell import HLShell

class HEShell(HLShell):

	has_level_editor = True
	
	edit_menu_screen = None
	editor_screen = None

	def handle_command_line_options(self):
		options = self.options
		if self.load_filename_argument():
			if options.edit_option:
				self.edit_level()
			else:
				self.restart_level()
		elif options.edit_option:
			self.new_level_cmd()
			self.edit_level()
		elif options.new_game_option:
			self.new_game_cmd()
		else:
			self.show_main_menu_screen()

	def show_edit_menu_screen(self):
		self.show_screen(self.edit_menu_screen)
	
	def show_editor_screen(self):
		if self.game.level_loaded():
			self.show_screen(self.editor_screen)
		else:
			self.show_edit_menu_screen()

	def test_level_enabled(self):
		"""Enable checker for the 'Test Level' command."""
		return self.game.level_loaded()
	
	def test_level_cmd(self):
		"""Implementation of the 'Test Level' command."""
		game = self.game
		if game.level_loaded():
			game.testing = True
			game.start_level()
			self.show_play_screen()
	
#	def play_next_level(self):
#		"""Load the next uncompleted level, if any, and start playing it. Reports
#		errors to the user."""
#		if self.ask_save_level():
#			HLShell.play_next_level(self)
#		else:
#			self.show_editor_screen()

	def enter_level_editor_cmd(self):
		"""Implementation of the 'Level Editor' command."""
		self.show_edit_menu_screen()

	def create_level_set_cmd(self):
		"""Implementation of the 'Create Level Set' command."""
		path = request_new_filename(prompt = "Create level set named:",
			suffix = self.game.level_set_suffix,
			directory = self.game.get_custom_level_set_dir(),
			filename = "CustomLevels")
		if path:
			name = os.path.basename(path)
			try:
				os.mkdir(path)
			except EnvironmentError, e:
				alert("Unable to create '%s': %s:" % (name, e))
				return
			self.game.set_playing_level_dir(path)
			alert("Level set '%s' created." % name)
	
	def new_level_cmd(self):
		"""Implementation of the 'New Level' command."""
		self.ask_save()
		self.game.new_level()
		self.show_editor_screen()

	def open_level_cmd(self):
		"""Implementation of the 'Open Level' command."""
		game = self.game
		path = request_old_filename(suffixes = [game.level_file_suffix],
			directory = game.get_level_save_dir())
		if path:
			if self.load_level_file(path):
				self.show_editor_screen()
				return True
		return False
	
	def save_level_enabled(self):
		return self.game.level_loaded()
	
	def save_level_cmd(self):
		"""Implementation of the 'Save Level' command."""
		return self.write_level(ask_path = False)

	def save_level_as_enabled(self):
		return self.game.level_loaded()
	
	def save_level_as_cmd(self):
		"""Implementation of the 'Save Level As...' command."""
		return self.write_level(ask_path = True)

	def write_level(self, ask_path):
		"""Writes the current level to a file. If ask_path is true, or the level
		has not been saved before, asks the user for a pathname, otherwise writes
		it to the previously-used pathname. Reports errors to the user. Returns
		true unless cancelled or an error occurs."""
		game = self.game
		dir = game.editing_level_dir
		name = game.level_name or ""
		if dir and name and not ask_path:
			path = os.path.join(dir, name)
		else:
			if not dir:
				dir = game.get_level_save_dir()
			path = request_new_filename(prompt = "Save level as:",
				suffix = game.level_file_suffix, directory = dir, filename = name)
		if path:
			try:
				game.write_level(path)
				game.level_needs_saving = False
				return True
			except EnvironmentError, e:
				alert("Unable to save '%s': %s" % (
						os.path.basename(path), mess))
		return False

	def edit_level_enabled(self):
		"""Enable checker for the 'Edit Level' command."""
		return self.game.level_loaded()
	
	def edit_level_cmd(self):
		"""Implementation of the 'Edit Level' command."""
		self.edit_level()
	
	def edit_level(self):
		if self.game.level_loaded():
			self.game.stop_level()
			self.show_editor_screen()
	
	def exit_level_editor_cmd(self):
		"""Implementation of the 'Exit Level Editor' command."""
		self.show_main_menu_screen()
	
	def ask_save(self):
		"""If there is unsaved game progress or changes to a level, ask the
		user whether to save it, and if the answer is yes, do so. Reports
		errors to the user. Raises Cancel if cancelled or an error occurred."""
		HLShell.ask_save_progress(self)
		self.ask_save_level()

	def ask_save_level(self):
		"""If there are unsaved changes to a level, ask the
		user whether to save it, and if the answer is yes, do so. Reports
		errors to the user. Raises Cancel if cancelled or an error occurred."""
		if self.game.level_needs_saving:
			resp = ask("Save changes to level?", ["Yes", "No", "Cancel"])
			if resp == "Cancel":
				raise Cancel
			if resp == "Yes":
				self.save_level_cmd()

	def level_completed(self, result):
		if self.game.testing or self.game.level_needs_saving:
			self.game.testing = False
			self.edit_level()
		else:
			HLShell.level_completed(self, result)

	def escape_key(self):
		screen = self.current_screen
		if screen is self.editor_screen:
			self.show_edit_menu_screen()
		elif screen is self.edit_menu_screen:
			self.edit_level()
		elif screen is self.play_screen and self.game.testing:
			self.game.testing = False
			self.edit_level()
		else:
			HLShell.escape_key(self)

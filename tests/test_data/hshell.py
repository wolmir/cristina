################################################################
#
#   Humerus - HShell
#
#   A Shell subclasss designed to be used with an HGame.
#
################################################################

import os
import pygame.display
from pygame.locals import K_ESCAPE
from gui.albow.root import Cancel
from gui.albow.shell import Shell
from gui.albow.dialogs import alert, ask
from gui.albow.file_dialogs import request_old_filename, request_new_filename

#---------------------------------------------------------------------------

class HShell(Shell):
	#  game      Game
	#  options   Options

	game_title = "Untitled Game"
	has_levels = False
	has_level_editor = False
	
	#  Screens - may be None if that screen type not used in game
	
	about_screen = None
	main_menu_screen = None
	intro_screen = None
	play_screen = None
	
	def __init__(self, game, options):
		self.game = game
		self.options = options
		display = pygame.display.get_surface()
		Shell.__init__(self, display)
		self.set_timer(options.frame_time())

	def run(self):
		try:
			self.handle_command_line_options()
			Shell.run(self)
		except Cancel:
			pass
	
	def handle_command_line_options(self):
		try:
			if self.load_filename_argument():
				self.resume_game()
			elif self.options.new_game_option:
				self.new_game_cmd()
			else:
				self.default_startup()
		except Cancel:
			self.default_startup()
	
	def default_startup(self):
		self.show_main_menu_screen()

	def load_filename_argument(self):
		"""If a filename was supplied on the command line, load it and
		return True. Otherwise, return False. Reports errors to the user."""
		filename = self.options.filename_argument
		if filename:
			path = os.path.abspath(filename)
			self.load_file(path)
			return True
		else:
			return False
	
	def show_screen(self, screen):
		if screen:
			Shell.show_screen(self, screen)
	
	def show_about_screen(self):
		self.show_screen(self.about_screen)

	def show_main_menu_screen(self):
		self.show_screen(self.main_menu_screen)
	
	def show_intro_screen(self):
		self.show_screen(self.intro_screen)

	def show_play_screen(self, testing = False):
		if self.game.play_in_progress():
			self.show_screen(self.play_screen)
		else:
			self.show_menu_screen()
	
	def load_file(self, path):
		"""Load a saved game. Reports errors to the user."""
		if path.endswith(self.game.save_file_suffix):
			self.restore_game(path)
		else:
			alert("Unrecognized file: %s" % path)

	def about_enabled(self):
		return self.about_screen is not None

	def about_cmd(self):
		"""Implementation of the 'About' command."""
		self.show_about_screen()
	
	def new_game_cmd(self):
		"""Implementation of the 'New Game' command."""
		self.ask_save()
		self.game.new_game()
		self.resume_new_game()
	
	def load_game_cmd(self):
		"""Implementation of the 'Load Game' command."""
		game = self.game
		self.ask_save()
		dir = game.get_save_dir()
		path = request_old_filename(suffixes = [game.save_file_suffix],
			directory = dir)
		if not path:
			raise Cancel
		self.restore_game(path)

	def restore_game(self, path):
		"""Restore a saved game from the specified path. Reports errors to the user."""
		self.load_game_file(path)
		self.resume_game()
	
	def load_game_file(self, path):
		"""Load a saved game from the specified path. Reports errors to
		the user. Raises Cancel if cancelled or an error occurs."""
		try:
			self.game.load_game(path)
		except EnvironmentError, e:
			alert("Unable to load '%s': %s" % (
				os.path.basename(path), e))
			raise Cancel
	
	def save_game_enabled(self):
		"""Enable checker for the 'Save Game' command."""
		return self.game.game_needs_saving()

	def save_game_cmd(self):
		"""Implementation of the 'Save Game' command."""
		self.save_game(prompt = False)
		alert("Game saved.")
	
	def save_game_as_enabled(self):
		"""Enable checker for the 'Save Game' command."""
		return self.game.game_in_progress()

	def save_game_as_cmd(self):
		"""Implementation of the 'Save Game As' command."""
		self.save_game(prompt = True)

	def save_game(self, prompt):
		"""Save the game. If prompt is true or no save pathname is set, ask
		for a pathname. Reports errors to the user. Raises Cancel if cancelled
		or an error occurs."""
		game = self.game
		old_path = game.get_save_path()
		if prompt or not game.save_name:
			new_path = request_new_filename(prompt = "Save game as:",
				suffix = game.save_file_suffix, pathname = old_path)
		else:
			new_path = old_path
		if not new_path:
			raise Cancel
		try:
			game.save_game(new_path)
		except EnvironmentError, e:
			alert("Unable to save '%s': %s" % (
				os.path.basename(new_path), e))
			raise Cancel

	def resume_game_enabled(self):
		"""Enable checker for the 'Resume Game' command."""
		return self.game.play_in_progress()

	def resume_game_cmd(self):
		"""Implementation of the 'Resume Game' command."""
		self.resume_game()
	
	def resume_new_game(self):
		if self.game.play_in_progress():
			if self.intro_screen:
				self.show_intro_screen()
			else:
				self.show_play_screen()

	def resume_game(self):
		if self.game.play_in_progress():
			self.show_play_screen()
	
	def quit_cmd(self):
		self.quit()

	def ask_save(self):
		"""If there is anything to be saved, ask the user whether to save it, and
		if the answer is yes, do so. Reports errors to the user. Raises Cancel if
		cancelled or an error occurred."""
		self.ask_save_progress()
		
	def ask_save_progress(self):
		"""If there is unsaved game progress, ask the user whether to save it, and
		if the answer is yes, do so. Reports errors to the user. Raises Cancel if
		cancelled or an error occurred."""
		if self.game.game_needs_saving():
			resp = ask("Save game progress?", ["Yes", "No", "Cancel"])
			if resp == "Cancel":
				raise Cancel
			if resp == "Yes":
				self.save_game(prompt = True)

	def ask_quit(self):
		"""Make sure user really wants quit the game. Raises Cancel if cancelled
		or an error occurred."""
		if not ask("Quit the game?") == "OK":
			raise Cancel

	def confirm_quit(self):
		"""Make sure user really wants quit the game. If there is unsaved
		information, give an opportunity to do so. Returns true if quitting should
		proceed. Raises Cancel if cancelled or an error occurred."""
		self.ask_quit()
		self.ask_save()
		return True

	def defer_drawing(self):
		if self.frame_time:
			screen = self.current_screen
			if screen and self.screen_runs_game(screen):
				return True
		return False

	def timer_event(self, event):
		result = True
		screen = self.current_screen
		if screen:
			if self.screen_runs_game(screen):
				result = self.game.timer_event(event)
				self.check_for_completion()
		return result
	
	def begin_frame(self):
		"""Deprecated, use timer_event() instead."""
		game = self.game
		screen = self.current_screen
		if screen:
			screen.begin_frame()
			if self.screen_runs_game(screen):
				game.begin_frame()
				self.check_for_completion()
	
	def check_for_completion(self):
		result = self.game.game_is_completed()
		if result:
		 	self.game_completed(result)
	
	def game_completed(self, result):
		"""Called when the game is completed, and passed the result returned
		by the game's game_is_completed() method."""
		self.show_main_menu_screen()

	def screen_runs_game(self, screen):
		"""Returns true if the game should run while the given screen
		is the current screen."""
		return screen is self.play_screen or getattr(screen, 'runs_game', False)

	def key_down(self, e):
		if e.key == K_ESCAPE:
			self.escape_key()
	
	def escape_key(self):
		if self.current_screen is self.main_menu_screen:
			self.resume_game()
		else:
			self.show_main_menu_screen()

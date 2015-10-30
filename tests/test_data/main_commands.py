################################################################
#
#   Humerus - Main commands screen
#
################################################################

from pygame.locals import *
from gui.albow.resource import get_font, get_image
from gui.albow.controls import Label
from command_screen import MenuTitle, MenuButton, CommandScreen

#--------------------------------------------------------------------------

class MainMenuTitle(MenuTitle):
	pass

class MainMenuButton(MenuButton):
	pass

#--------------------------------------------------------------------------

class MainCommandScreen(CommandScreen):
	
	title_class = MainMenuTitle
	button_class = MainMenuButton

	menu_items = [
		("Help",             'about',              [K_F1, K_h]),
		("New Game",         'new_game',           [K_n]),
		("Load Game...",     'load_game',          [K_o]),
		("Save Game",        'save_game',          [K_s]),
		("Save Game As...",  'save_game_as',       []),
		("Continue",         'resume_game',        []),
		("Restart Level",    'restart_level',      [K_r]),
		("Custom Levels...", 'open_level_set',     [K_k]),
		("Level Editor",     'enter_level_editor', [K_e]),
		("Quit",             'quit',               [K_q]),
	]

	def get_title(self):
		return self.shell.game_title
	
	title = property(get_title)

	def include_command(self, action):
		if action in ('restart_level', 'open_level_set'):
			return self.shell.has_levels
		elif action == 'enter_level_editor':
			return self.shell.has_level_editor
		else:
			return True

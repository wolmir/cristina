################################################################
#
#   Humerus - Typical level editor menu screen
#
################################################################

from pygame.locals import *
from gui.albow.resource import get_font, get_image
from gui.albow.controls import Label
from command_screen import MenuTitle, MenuButton, CommandScreen

#--------------------------------------------------------------------------

class EditMenuTitle(MenuTitle):
	pass

class EditMenuButton(MenuButton):
	pass

#--------------------------------------------------------------------------

class EditCommandScreen(CommandScreen):

	title = "Level Editor"
	title_class = EditMenuTitle
	button_class = EditMenuButton

	menu_items = [
		("Create Level Set...", 'create_level_set',  []),
		("New Level",           'new_level',         [K_n]),
		("Open Level...",       'open_level',        [K_o]),
		("Resume Editing",      'edit_level',        []),
		("Test Level",          'test_level',        [K_t]),
		("Save Level",          'save_level',        [K_s]),
		("Save Level As...",    'save_level_as',     []),
		("Exit Editor",         'exit_level_editor', [K_q]),
	]

#--------------------------------------------------------------------------
#
#class EditMenuScreen(EditCommandScreen):
#
#	title = "Level Editor"
#	title_class = EditMenuTitle
#	button_class = EditMenuButton
#	with_menu = True

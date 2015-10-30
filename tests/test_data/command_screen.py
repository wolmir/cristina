################################################################
#
#   Humerus - Command Screen
#
################################################################

from pygame.locals import *
from gui.albow.screen import Screen
from gui.albow.controls import Label, Button
from gui.albow.layout import Column

#  Install MenuButton theme
import theme

#-----------------------------------------------------------------------------

class MenuTitle(Label):
	pass

#-----------------------------------------------------------------------------

class MenuButton(Button):
	pass

#	def __init__(self, client, title, action_name, **kwds):
#		Button.__init__(self, title)
#		self.client = client
#		self.action_name = action_name
#	
#	def enable(self):
#		return action_enabled(self.client, self.action_name)
#	
#	def action(self):
#		do_action(self.client, self.action_name)

#-----------------------------------------------------------------------------

def action_enabled(client, action_name):
	func = getattr(client, action_name + '_enabled', None)
	if func:
		return func()
	else:
		return True

def do_action(client, action_name):
	func = getattr(client, action_name + '_cmd', None)
	if func:
		func()

#-----------------------------------------------------------------------------

class CommandScreen(Screen):
	#  Abstract class attributes:
	#
	#  menu_items     [(title, action_name, [keycode])]
	
	title = None
	title_class = MenuTitle
	button_class = MenuButton
	
	def __init__(self, shell, with_menu = False):
		Screen.__init__(self, shell)
		self.init_command_map()
		if with_menu:
			title = self.create_title()
			buttons = self.create_buttons()
			self.add_title_and_buttons(title, buttons)
	
	def init_command_map(self):
		map = {}
		for title, action, keys in self.menu_items:
			if self.include_command(action):
				for key in keys:
						map[key] = action
		self.command_map = map
	
	def create_title(self):
		title = self.title
		if title:
			return self.title_class(self.title)
	
	def create_buttons(self):
		buttons = []
		for title, action, keys in self.menu_items:
			if self.include_command(action):
				buttons.append(self.create_button(title, action))
		return buttons
	
	def include_command(self, action):
		return True
	
	def create_button(self, title, action_name):
		def enable():
			return action_enabled(self.shell, action_name)
		def action():
			do_action(self.shell, action_name)
		return self.button_class(title, action = action, enable = enable)

	def add_title_and_buttons(self, title, buttons):
		menu = Column(buttons, align = 'l')
		self.add_title_and_menu(title, menu)
	
	def add_title_and_menu(self, title, menu):
		items = [menu]
		if title:
			items.insert(0, title)
		box = Column(items, align = 'l', spacing = 20)
		c = self.center
		box.center = self.center
		self.add(box)

	def key_down(self, e):
		command = None
		if e.cmd or e.key == K_ESCAPE or K_F1 <= e.key <= K_F12:
			command = self.command_map.get(e.key)
		if command:
			self.do_command(command)
		else:
			Screen.key_down(self, e)
	
	def do_command(self, command):
		if action_enabled(self, command):
			do_action(self.shell, command)

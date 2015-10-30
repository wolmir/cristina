################################################################
#
#   Humerus - Command Line Options
#
#   Parsing command line options and setting video mode.
#
################################################################

import os, sys
from optparse import OptionParser
import pygame
pygame.init()
from gui.albow.resource import resource_path

class Options(object):

	display_flags = 0         # Flags passed to pygame.display.set_mode()

	#  Attributes settable by command line options
	
	fullscreen_option = False
	windowed_option = False
	fullscreen_by_default = False
	screen_size_option = (800, 600)
	frame_rate_option = 0
	new_game_option = False
	edit_option = False
	filename_argument = None
	
	#  Command line option configuration
	
	allow_fullscreen_option = False  # Can force fullscreen with cmd line option
	allow_windowed_option = False    # Can force windowed with cmd line option
	allow_screen_size_option = False # Can set screen_size with cmd line option
	allow_frame_rate_option = False  # Can set frame rate using cmd line option
	allow_new_game_option = True     # Can start new game using cmd line option
	allow_edit_option = True         # Can enter editor using cmd line option
	
	allowed_screen_sizes = []        # Empty to allow any screen size
	
	#  Usage text, in case of command line errors
	
	usage = "%prog [options] [saved_game]"

	#  Command line option descriptors
	#
	#  Format: ("short,long", attr_name, help_text [, type])
	#
	#  Option value is stored in an attribute of the shell named
	#  attr_name + '_option'.
	#
	#  You can replace the std_command_line_options in your subclass to
	#  change the option or help text, but don't change the attr_name.
	
	std_command_line_options = [
		("-f,--fullscreen", 'fullscreen',  "Run in full-screen mode"           ),
		("-w,--windowed",   'windowed',    "Run in windowed mode"              ),
		("-s,--size",       'screen_size', "Window size: <width>x<height>", str),
		("-F,--framerate",  'frame_rate',  "Frames per second",             int),
		("-n,--newgame",    'new_game',    "Start new game"                    ),
	]
	
	edit_command_line_options = [
		("-e,--edit",       'edit',        "Start in level editor"),
	]
	
	extra_command_line_options = []  # Any extra options you want
	
	debug_command_line_options = []  # Only available when env var DEBUG is true

	macosx_bundle = False  # Set to true when run from Finder on MacOSX
	
	def __init__(self, with_editor = False):
		self.get_command_line_options(with_editor)
		self.set_video_mode()
#		self.set_timer()
	
	def set_video_mode(self):
		flags = self.display_flags
		if self.fullscreen_option or (
				not self.windowed_option and self.fullscreen_by_default):
			flags |= FULLSCREEN
		pygame.display.set_mode(self.screen_size_option, flags)

#	def set_timer(self):
#		rate = self.frame_rate_option
#		if rate:
#			t = int(round(1000.0 / rate))
#			pygame.time.set_timer(pygame.USEREVENT, t)

	def frame_time(self):
		rate = self.frame_rate_option
		if rate:
			return 1000.0 / rate
		else:
			return 0

	def fatal(self, mess):
		sys.stderr.write("%s: %s\n" % (sys.argv[0], mess))
		sys.exit(1)
	
	def extract_macosx_finder_launch_args(self):
		#  When launched from the Finder under MacOSX, we get called with
		#  a command line argument of the form -psn_N_NNNNN. In this case we
		#  delete the argument from argv and return true.
		args = sys.argv
		if len(args) > 1 and args[1].startswith("-psn_"):
			del args[1]
			return True
		else:
			return False

	def set_screen_size_option(self, value):
		try:
			screen_size = map(int, value.split("x"))
			if len(screen_size) <> 2:
				raise ValueError
		except ValueError:
			fatal("Invalid --size argument")
		allowed = self.allowed_screen_sizes
		if not allowed or screen_size in allowed:
			self.screen_size_option = screen_size

	def get_command_line_options(self, with_editor):
		self.macosx_bundle = self.extract_macosx_finder_launch_args()
		parser = OptionParser(usage = self.usage)
		def add_option(flags, dest, help, type = None):
			if type:
				action = 'store'
			else:
				action = 'store_true'
			parser.add_option(action = action, dest = dest, help = help,
				type = type, *flags.split(","))
		options = self.std_command_line_options
		if with_editor:
			options = options + self.edit_command_line_options
		for desc in options:
			attr = 'allow_' + desc[1] + '_option'
			if getattr(self, attr):
				add_option(*desc)
		for desc in self.extra_command_line_options:
			add_option(*desc)
		if os.environ.get("DEBUG"):
			for desc in self.debug_command_line_options:
				add_option(*desc)
		opts, args = parser.parse_args()
		if args:
			self.filename_argument = args[0]
		for name, value in opts.__dict__.items():
			if name == 'screen_size':
				set_screen_size_option(self, value)
			else:
				attr = name + '_option'
				setattr(self, attr, value)

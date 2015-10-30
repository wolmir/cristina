#------------------------------------------------------------------------------
#
#   Humerus - Level editor change dot
#
#------------------------------------------------------------------------------

from pygame import Rect
from gui.albow.widget import Widget
from gui.albow.theme import ThemeProperty

class ChangeDot(Widget):

	frame_width = ThemeProperty('frame_width')
	fill_color = ThemeProperty('fill_color')

	def __init__(self, game, **kwds):
		Widget.__init__(self, Rect(0, 0, 16, 16), **kwds)
		self.game = game
	
	def draw(self, surf):
		fg = self.fg_color
		bg = self.fill_color
		b = 2 * self.frame_width
		r = self.get_margin_rect()
		surf.fill(fg, r)
		r.inflate_ip(-b, -b)
		surf.fill(bg, r)
		if self.game.level_needs_saving:
			r.inflate_ip(-2, -2)
			surf.fill(fg, r)

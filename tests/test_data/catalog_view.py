#-------------------------------------------------------------------------------
#
#   Mutagenesis - Plant catalogue view
#
#-------------------------------------------------------------------------------

from pygame import Rect
from humerus.albow.palette_view import PaletteView
from humerus.albow.utils import frame_rect, blit_in_rect
from rendering import get_plant_thumbnail
from game import game

class CatalogView(PaletteView):

	#border_width = 1
	#border_color = (0xff, 0xff, 0xff)
	highlight_style = 'frame'
	#frame_color = (0x80, 0x80, 0x80)
	frame_color = (0x40, 0x40, 0x40)
	text_color = (0xff, 0xff, 0xff)
	text_bg_color = frame_color
	thumbnail_bg_color = (0, 0, 0)
	thumbnail_border_width = 2

	thumb_size = (64, 64)
	cell_margin = 2

	def __init__(self, **kwds):
		tw, th = self.thumb_size
		cm = 2 * self.cell_margin
		PaletteView.__init__(self, cell_size = (tw + cm, th + cm),
			nrows = 1, ncols = 4, scrolling = True, **kwds)
	
	def num_items(self):
		return game.num_specimens
	
	def draw_item(self, surf, i, rect):
		plant = game.get_specimen_no(i)
		thumb = get_plant_thumbnail(plant, self.thumb_size)
		r = thumb.get_rect()
		r.center = rect.center
		surf.fill(self.thumbnail_bg_color, r)
		surf.blit(thumb, r)
		frame_rect(surf, self.frame_color, r, self.thumbnail_border_width)
		r = rect.inflate(-2, -2)
		buf = self.font.render(str(plant.number), True, self.text_color,
			self.text_bg_color)
		r = buf.get_rect()
		blit_in_rect(surf, buf, rect, 'bl', 3)
	
	def click_item(self, i, e):
		game.select_specimen_no(i)
	
	def item_is_selected(self, i):
		return game.specimen_no_is_selected(i)

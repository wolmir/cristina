#-------------------------------------------------------------------------------
#
#   Mutagenesis - Plant view
#
#-------------------------------------------------------------------------------

from pygame import Rect
from humerus.albow.widget import Widget
from humerus.albow.utils import frame_rect, blit_in_rect
from game import game
from rendering import render_plant

#-------------------------------------------------------------------------------

class PlantView(Widget):

	bg_color = (0, 0, 0)
	border_width = 2
	border_color = (0x40, 0x40, 0x40)
	text_color = (0xff, 0xff, 0xff)
	
	ref = None

	def __init__(self, **kwds):
		#Widget.__init__(self, Rect(0, 0, size[0], size[1]), **kwds)
		Widget.__init__(self, **kwds)
	
	def draw(self, surf):
		#print "PlantView.draw" ###
		plant = self.ref.get()
		if plant:
			buffer = render_plant(plant, self.size)
			frame = surf.get_rect()
			r = buffer.get_rect()
			r.midbottom = frame.midbottom
			surf.blit(buffer, r)
			title = plant.get_description()
			buf = self.font.render(title, True, self.text_color)
			r = buf.get_rect()
			blit_in_rect(surf, buf, frame, 'bl', 3)

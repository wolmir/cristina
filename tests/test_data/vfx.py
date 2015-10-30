from cocos.particle_systems import *
from cocos.particle import *
from cocos.actions import *
from cocos.text import *
from cocos.layer import Layer
import cocos


class MessageLayer( Layer ):
    def show_message( self, msg, callback=None ):

        w,h = director.get_window_size()

        self.msg = Label( msg,
            font_size=24,
            font_name='Nokia Cellphone',
            anchor_y='center',
            anchor_x='center' )
        self.msg.position=(w, h/2)

        self.add( self.msg )

        actions = Accelerate(MoveBy( (-w/2,0), duration=0.5)) + \
                    Delay(2) +  \
                    Accelerate(MoveBy( (-w/2, 0), duration=0.5)) + \
                    Hide()

        if callback:
            actions += CallFunc( callback )

        self.msg.do( actions )


def createLabel(msg, fontsize = 18, color = (255, 0, 0, 255)):
    errormsg = cocos.text.Label(msg,
                        font_name='Nokia Cellphone',
                         font_size=fontsize,
                         anchor_x='center', anchor_y='center')
    errormsg.element.color = color
    return errormsg

class SuccessExplosion(Explosion):
    def __init__(self, start_color=Color(0, 1, 0, 1), end_color=Color(1,1,1,0)):
        super(SuccessExplosion, self).__init__()
        self.total_particles = 10
        self.life = 1.0
        self.life_var = 0.5
        self.start_color = start_color
        self.start_color_var = Color(0, 0, 0, 0)
        self.end_color = end_color
        self.end_color_var = Color(0, 0, 0, 0)
        self.do(Delay(2) + CallFunc(self.kill))
import cocos
from vfx import *
from cocos.particle import *
from cocos.actions import *

class PowerUpIndicator(cocos.sprite.Sprite):
    def __init__(self, image, callback):
        super(PowerUpIndicator, self).__init__(image)
        self.file_name = image
        self._count = 2
        self.callback = callback
        self.label = createLabel(str(self.count), 24)
        self.label.position = (-self.width/2, 10)
        self.label.element.color = (0, 0, 0, 118)
        self.label.element.anchor_x = 'right'
        self.add(self.label)

    def activate(self):
        if self.count > 0:
            self.do(cocos.actions.RotateBy(10, 0.1) + cocos.actions.RotateBy(-20, 0.1) + cocos.actions.RotateBy(10,0.1))
            self.count -= 1
            self.callback(self.file_name)

    def _set_count(self, c):
        self._count = c
        self.label.element.text = str(self._count)

    def _get_count(self):
        return self._count

    count = property(_get_count, _set_count, doc='indicates the number of powerups available')

    def _set_scale( self, s ):
        super(PowerUpIndicator, self)._set_scale(s)

        if hasattr(self, 'label'):
            self.label.position = (-self.width/2, -self.height/2)

def ByteBlaster( bitpattern ):
    """
    Eliminates on coming byte and launches a new pattern.
    """
    for i in xrange(len(bitpattern.bits)):
        (r, g, b, a) = bitpattern.Color4B24F(bitpattern.colors[i])
        se = SuccessExplosion(Color(r, g, b, a))
        se.position = bitpattern.bits[i].x, bitpattern.y + 32
        bitpattern.parent.add(se, 2)
    parent = bitpattern.parent
    parent.sound_effects['explode'].play()

    bitpattern.kill()
    #toggles the isAnimating flag used to disable touch.
    parent.do(cocos.actions.Delay(0.5) + cocos.actions.CallFunc(parent.handleSuccess))


def BitAndOrder( bitpattern ):
    """
    Re-orders bits in the right order.
    """
    bitpattern.bits = sorted(bitpattern.bits, key = lambda k: k.bitNum)
    w,h = director.get_window_size()
    bitSize = w/len(bitpattern.bits)
    for i in xrange(len(bitpattern.bits)):
        bitpattern.bits[i].position = w-(i+1)*bitSize, 0
    parent = bitpattern.parent
    parent.isAnimating = False



#stuff used by the AutoByte powerup for tracking indices.
indices = []

def AutoByteHelper( bitpattern ):
    global indices
    bitpattern.toggleBit(indices.pop())
    if len(indices) == 0:
        bitpattern.parent.isAnimating = False

def AutoByte( bitpattern, num ):
    global indices
    """
    toggles the required bits. Should be launched only when the bits are in order.
    """
    val = 1;
    indices = []
    for i in range(0, len(bitpattern.bits)):
        if val & num == 0:
            indices.append(i)
        val = val << 1
    random.shuffle(indices)
    bitpattern.do((cocos.actions.Delay(0.2) + cocos.actions.CallFuncS(AutoByteHelper)) * len(indices))
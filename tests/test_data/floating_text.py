import pygame

from mutate_sprite import MutateSprite

class FloatingText( MutateSprite ):
    def __init__( self, color, pos ):
        MutateSprite.__init__( self, color, pos )
        self.text = "?"
        #self.origSize = (30, 30)
        self.color = color
        self.font = pygame.font.SysFont("", 20)
        self.image = self.font.render(self.text, False, color)
        #self.imageMaster = pygame.Surface( self.origSize )
        #self.imageMaster.fill( color )
        #self.imageMaster.set_alpha(255)
        #self.image = self.imageMaster
        
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.image.set_alpha(255)
        #self.line = Interpolator( pos )
        #self.alpha = Interpolator( self.image.get_alpha() )
        #self.scale = Interpolator( self.origSize )

    def setText( self, text, color ):
        self.text = text
        self.color = color
        self.image = self.font.render(self.text, False, self.color)       
        oldCenter = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
        self.image.set_alpha(255)
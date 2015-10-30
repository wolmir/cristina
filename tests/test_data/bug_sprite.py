import pygame

from mutate_sprite import MutateSprite

class BugSprite(MutateSprite):
    def __init__( self, color, pos ):
        MutateSprite.__init__( self, color, pos )
        self.color = color
        self.rect = pygame.Rect(pos,(1,1))
        self.redraw()

    def setColor(self, color):
        self.color = color
        self.redraw()

    def redraw(self):
        SURFACE_WIDTH = 10
        SURFACE_HEIGHT = 10
        oldAlpha = self.image.get_alpha()
        self.image = pygame.surface.Surface( (SURFACE_WIDTH, SURFACE_HEIGHT) )
        pygame.draw.circle(self.image, self.color, (SURFACE_WIDTH/2,SURFACE_HEIGHT/2), SURFACE_WIDTH/2 )
        self.image.set_colorkey((0,0,0))

        pos = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.image.set_alpha(oldAlpha)
import pygame

class LifeBar(pygame.sprite.Sprite):
    MAX_LIFE = 100
    life = 100
    color = (255,0,0)
    borderColor = (255,255,255)
    position = (320, 240)

    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.redraw()


    def redraw(self):
        SURFACE_WIDTH = 50
        SURFACE_HEIGHT = 10
        self.image = pygame.Surface((SURFACE_WIDTH, SURFACE_HEIGHT))
        self.image.fill( self.screen.bg_color )

        pygame.draw.rect(self.image, 
                         self.color, 
                            ( 0, 0, 
                             SURFACE_WIDTH * (self.life / float(self.MAX_LIFE)),
                            SURFACE_HEIGHT ))

        pygame.draw.rect(self.image, 
                         self.borderColor, 
                            ( 0, 0, 
                            SURFACE_WIDTH, 
                            SURFACE_HEIGHT ), 
                         2)

        self.rect = self.image.get_rect()
        self.rect.center = self.position

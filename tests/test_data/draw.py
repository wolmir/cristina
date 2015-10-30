import pygame
import data

class Draw(object):
    def __init__(self, w=100, h=100):        
        self.sfont = self.sfont = pygame.font.SysFont(data.filepath('terminal.fon', 'fonts'), 12)
        self.sfont = self.font = pygame.font.SysFont(data.filepath('terminal.fon', 'fonts'), 17)
        self.textbox = pygame.Surface((w, h))        
        self.w, self.h = w,h
        self.line_height = 16
        

    def draw_info(self, screen, r, player):
        self.textbox.fill((0,0,0))
        msg = 'LIFES: {} - HP: {}% - K1: {} - K2: {} - K3: {}'.format(player.lifes, 
                                        player.hp, player.key1, player.key2, player.key3 )
        text = self.sfont.render(msg, 0, (250, 250, 250), (0,0,0))
        self.textbox.blit(text, (10, 2))
        screen.blit(self.textbox, (r.x, r.y, self.w, self.h))

    def draw_level(self, screen, level, camera):
        r = pygame.Rect(0,0, level.tw, level.th)
        for y in range(level.height):
            for x in range(level.width):
                r.x = x*level.tw
                r.y =  y*level.th
                if camera.colliderect(r):
                    t = level.gt(x, y, 1)
                    if t == 0:
                        continue
                    else:
                        screen.blit(t, 
                                    ((x*level.tw)- camera.left,
                                     (y*level.th)- camera.top))

    def draw_entities(self, screen, entites, camera):
        for e in entites:
            if isinstance(e, pygame.sprite.Sprite) and camera.colliderect(e.rect):
                screen.blit(e.image, (e.rect.left - camera.left,
                                        e.rect.top - camera.top))

    def draw_text(self, screen, lines, y):
        for l in lines:
            text = self.font.render(l, 0, (250, 250, 250), (0,0,0))
            textpos = text.get_rect(centerx=screen.get_width()/2, centery=y+self.line_height)
            y=y+self.line_height
            screen.blit(text, textpos)
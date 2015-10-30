import pygame
import pygame.locals as pl
import rstore
import score

from const import *

# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

# transparent surface to blit to
hsurf = pygame.Surface(HUD_SIZE, pl.SRCALPHA, 32)

def pos_on_hud(pos):
    return (pos[0] > HUD_POS[0] and pos[0] < HUD_POS[0] + HUD_SIZE[0] 
            and pos[1] > HUD_POS[1] and pos[1] < HUD_POS[1] + HUD_SIZE[1])

# color of all text on HUD
_HUDCOL = BLACK
# x offset for text
_X_OFF = 20

# events that we can send back to the play scene
EVENT_PREVIOUS = 'previous'
EVENT_NEXT = 'next'
EVENT_MAIN = 'main'
EVENT_RESET = 'reset'

def _get_pos_for_centering(tocenter, surf):
    """Get (x, y) position for centering tocenter on surf."""

    surf_size = surf.get_size()
    tocenter_size = tocenter.get_size()
    x = (surf_size[0] - tocenter_size[0]) / 2
    y = (surf_size[1] - tocenter_size[1]) / 2

    if x < 0 or y < 0:
        # the surface to center is bigger than the surface we want to
        # center on!
        return (0, 0)
    return (x, y)

class Hud(object):
    BUT_PREVIOUS = 'previous'
    BUT_NEXT = 'next'
    BUT_MAIN = 'main'
    BUT_RESET = 'reset'
    def __init__(self, pscene, board):
        self._pscene = pscene
        self._game = pscene.game
        self._board = board
        self.smallfont = rstore.fonts['hudsmall']
        self.largefont = rstore.fonts['hudlarge']
        self.set_data(1)

        self.currenttxt = self.smallfont.render('Current', True, RED1)
        self.besttxt = self.smallfont.render('Best', True, RED1)

        # images for previous level, next level, menu and reset
        self.surfaces = {}
        self.rects = {}
        self.hover = {}

        # note positions are w.r.t top left of hud surface
        button_ypos = 400 - TUT_POS[0]
        arrow_size = rstore.images['next'].get_size()
        arrow_width, arrow_height = arrow_size
        right_xpos = HUD_SIZE[0] - arrow_width
        button_data = {self.BUT_NEXT: [rstore.images['next'], rstore.images['nextsel'], 
                                       (right_xpos, button_ypos)],
                       self.BUT_PREVIOUS: [rstore.images['prev'], rstore.images['prevsel'], 
                                    (0, button_ypos)]}

        pad = 20 #padding between < button and reset on each side
        vpad = 6 # vertical padding between center buttons
        mid_but_width = HUD_SIZE[0] - 2 * arrow_width - 2 * pad
        mid_but_height = (arrow_height - vpad) / 2 
        # create surfaces for main menu and reset
        reset_not = pygame.Surface((mid_but_width, mid_but_height))
        reset_sel = pygame.Surface((mid_but_width, mid_but_height))
        main_not = pygame.Surface((mid_but_width, mid_but_height))
        main_sel = pygame.Surface((mid_but_width, mid_but_height))


        border = 4
        fill_surf = pygame.Surface((mid_but_width - 2 * border, mid_but_height - 2 * border))
        reset_not.fill(RED1)
        reset_sel.fill(ORANGEY)
        fill_surf.fill(RED1)
        reset_sel.blit(fill_surf, (border, border))

        main_not.fill(BLUE1)
        main_sel.fill(ORANGEY)
        fill_surf.fill(BLUE1)
        main_sel.blit(fill_surf, (border, border))

        # put text on surfaces
        reset_txt = rstore.fonts['button'].render('RESET', True, WHITE)
        main_txt = rstore.fonts['button'].render('MENU', True, WHITE)

        reset_blit_pos = _get_pos_for_centering(reset_txt, reset_not)
        main_blit_pos = _get_pos_for_centering(main_txt, main_not)
        reset_not.blit(reset_txt, reset_blit_pos)
        reset_sel.blit(reset_txt, reset_blit_pos)
        main_not.blit(main_txt, main_blit_pos)
        main_sel.blit(main_txt, main_blit_pos)

        button_data[self.BUT_MAIN] = [main_not, main_sel, (arrow_width + pad, button_ypos + mid_but_height + vpad)]
        button_data[self.BUT_RESET] = [reset_not, reset_sel, (arrow_width + pad, button_ypos)]

        for but, val in button_data.items():
            not_selected_surf = val[0]
            selected_surf = val[1]
            pos = val[2]
            self.surfaces[but] = [not_selected_surf, selected_surf]
            new_rect = not_selected_surf.get_rect()
            new_rect.x += pos[0]
            new_rect.y += pos[1]
            self.rects[but] = new_rect
            self.hover[but] = False

    def handle_cursor_position(self, pos):
        for but, r in self.rects.items():
            if r.collidepoint(pos):
                self.hover[but] = True
            else:
                self.hover[but] = False

    def handle_mouse_up(self, pos):
        # did we click one of the options?
        for but, r in self.rects.items():
            if r.collidepoint(pos):
                # we clicked on a button
                self._game.juke.play_sfx('menuclick')
                # do something!
                if (but == self.BUT_NEXT):
                    # go to next level if possible
                    return EVENT_NEXT
                elif (but == self.BUT_PREVIOUS):
                    # go to previous level if possible
                    return EVENT_PREVIOUS
                elif (but == self.BUT_MAIN):
                    return EVENT_MAIN
                elif (but == self.BUT_RESET):
                    return EVENT_RESET
        # no event sent back to playscene
        return None

    def set_data(self, lnum):
        self.set_text(lnum)

    def set_text(self, lnum):
        self.set_level(lnum)
        self.set_moves(0)
        self.set_saved(0)
        self.set_lost(0)
        self.set_high_score(score.scores[lnum])

    def draw(self):
        #hsurf.fill(_FILL_COL)
        hsurf.blit(rstore.images['hud'], (0, 0))
        hsurf.blit(self.levtxt, (_X_OFF, 0))
        hsurf.blit(self.currenttxt, (_X_OFF, 60))
        hsurf.blit(self.savetxt, (_X_OFF, 90))
        #hsurf.blit(self.losttxt, (_X_OFF, 100))
        hsurf.blit(self.movtxt, (_X_OFF, 120))
        pygame.draw.line(hsurf, BLACK, (0, 160), (HUD_SIZE[0], 160), 4)
        hsurf.blit(self.besttxt, (_X_OFF, 180))
        hsurf.blit(self.best_saved_txt, (_X_OFF, 210))
        hsurf.blit(self.best_moves_txt, (_X_OFF, 240))

        # draw buttons
        for but in self.surfaces:
            if self.hover[but]:
                hsurf.blit(self.surfaces[but][1], self.rects[but])
            else:
                hsurf.blit(self.surfaces[but][0], self.rects[but])
        # reset hover for next frame
        for but in self.hover:
            self.hover[but] = False

    def set_high_score(self, sc):
        s0 = score.get_score_string(sc[0])
        s1 = score.get_score_string(sc[1])
        if (sc[0] != score.NO_SCORE):
            s0 += '/8'
            
        self.best_saved_txt = self.smallfont.render('Bits saved: {0}'.format(s0),
                                              True, _HUDCOL)
        self.best_moves_txt = self.smallfont.render('Moves: {0}'.format(s1),
                                              True, _HUDCOL)

    def set_level(self, level):
        self.levtxt = self.largefont.render('Level {0}'.format(level),
                                            True, _HUDCOL)

    def set_moves(self, moves):
        self.movtxt = self.smallfont.render('Moves: {0}'.format(moves),
                                            True, _HUDCOL)

    def set_lost(self, lost):
        self.losttxt = self.smallfont.render('Bits lost: {0}/8'.format(lost),
                                             True, _HUDCOL)

    def set_saved(self, saved):
        self.savetxt = self.smallfont.render('Bits saved: {0}/8'.format(saved),
                                             True, _HUDCOL)

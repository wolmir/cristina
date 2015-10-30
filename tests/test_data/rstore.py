"""Resource store and loader (sort of modelled on Skellington)."""

import os
import pygame

_my_path = os.path.abspath(os.path.dirname(__file__))
# base path is back one directory
base_path = os.path.normpath(os.path.join(_my_path, '..'))
# paths to image, font and sound directories
_image_path = os.path.join(base_path, 'image')
_font_path = os.path.join(base_path, 'font')
_sound_path = os.path.join(base_path, 'sound')

images = {'bg': 'paper.png',
          'arrowleft': 'arrowleft.png',
          'arrowdown': 'arrowdown.png',
          'arrowright': 'arrowright.png',
          'arrowup': 'arrowup.png',
          'hud' : 'hud.png',
          'next': 'next.png',
          'nextsel': 'nextsel.png',
          'prev': 'prev.png',
          'prevsel': 'prevsel.png'
}

# value is name, size in pts
fonts = {'main': ('ShareTechMono-Regular.ttf', 30),
         'button': ('ShareTechMono-Regular.ttf', 16),
         'hudlarge': ('PGott.ttf', 40),
         'highscore': ('PGott.ttf', 30),
         'hudsmall': ('PGott.ttf', 20),
         'tutorial': ('PGott.ttf', 20),
         'menu': ('PGott.ttf', 40),
         'finish': ('PGott.ttf', 40),
         'title': ('SerialPublicationDEMO.ttf', 80)
}

sfx = {'click': 'click.ogg',
       'menuclick': 'menuclick.ogg',
       'shoot': 'shoot.ogg',
       'goal': 'goal.ogg',
       'error': 'error.ogg',
       'turn': 'turn.ogg',
       'complete': 'complete2.ogg',
       'highscore': 'highscore.ogg',
       'stranded': 'stranded.ogg',
       'shatter': 'shatter.ogg'}

music = {'reawakening': 'reawakening.ogg'}

def load_resources():
    """This should be called immediately after Pygame is initialized."""
    global fonts, images, sfx, music

    for key, val in images.items():
        images[key] = pygame.image.load(os.path.join(_image_path, val)).convert_alpha()
    for key, val in fonts.items():
        fonts[key] = pygame.font.Font(os.path.join(_font_path, val[0]), val[1])
    for key, val in sfx.items():
        sfx[key] = pygame.mixer.Sound(os.path.join(_sound_path, val))
    for key, val in music.items():
        # all we need is the full path here
        music[key] = os.path.join(_sound_path, val)

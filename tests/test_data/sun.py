import pygame

from weather import Weather
from mutate_color import MutateColor

class Sun(Weather):
    color = MutateColor(255,0,0)

    def draw(self, surface):
        pass
        #pygame.draw.circle(surface, self.color, (10,10), 100 )

    def affect_flowers(self, flowers):
        for flower in flowers:
            flower.photosynthesis(self)
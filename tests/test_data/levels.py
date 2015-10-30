import pattern

class Level(object):
    
    def __init__(self, xor_val, size, speed, next_timer, pt):
        self.xor_val = xor_val
        self.size = size
        self.speed = speed
        self.next_timer = next_timer
        self.pattern = pt

level_1 = Level([True, False, False, False, False, False, False, False], 32, 70, 2, pattern.simple)
level_2 = Level([True, True, False, False, False, False, False, False], 32, 70, 2, pattern.simple)
level_3 = Level([True, True, False, False, True, True, False, False], 32, 120, 1.25, pattern.simple)
level_4 = Level([True, False, False, False, True, True, False, False], 32, 70, 2, pattern.simple)
level_5 = Level([True, False, False, False, False, False, False, False], 32, 70, 2, pattern.complex)
levels = [level_1, level_2, level_3, level_4, level_5]
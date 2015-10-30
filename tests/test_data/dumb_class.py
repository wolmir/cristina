def some_func(a, b):
    return a + b

def pointer_func(*args, **kwargs):
    return "Nothing"

class DumbClassA:
    def __init__(self):
        self.number = 124
        self.dumb_array = [2,3]

class ClassB:
    def __init__(self):
        self.dumb_var = DumbClassA()
        self.dumb_var.number = 678
        self.n = self.dumb_var.dumb_array[0]
        self.smarties = [6,7,8]
        some_func(456, 908)
        pointer_func(934, 612, *self.dumb_var.dumb_array, ball="me")
        pointer_func(*self.smarties, *self.dumb_var.dumb_array)
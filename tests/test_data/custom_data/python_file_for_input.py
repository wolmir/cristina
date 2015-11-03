no_of_methods = {
    "SomeClass": 2,
    "SampleClass": 3
}

class SomeClass:
    some_var = "skdld"
    var1, var2 = (0, 0)

    def __init__(self):
        self.yet_another_var = "stuff"

    def a_method(self):
        self.var1 = 90
        self.var3 = 98

class SampleClass:
    var1 = 1000
    var2 = 78
    var3 = 93

    def __init__(self):
        self.var4 = 89

    def method1(self):
        self.var3 = self.var2 * 2

    def method2(self):
        self.var4 = self.var2*9
        self.var4 += self.var1

def get_number_of_methods(class_name):
    return no_of_methods[class_name]

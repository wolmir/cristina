class FirstClass:
    def __init__(self):
        self.first_variable = 0
        self.another_variable = 5
        self.yet_another_variable = 10

    def method1(self):
        self.first_variable = 8
        self.another_variable = 6

    def method2(self):
        self.first_variable = 5
        self.yet_another_variable = 9

    def method3(self):
        self.method1()
        self.method2()


class SecondClass(FirstClass):
    def __init__(self):
        FirstClass.__init__(self)
        self.second_variable = 9


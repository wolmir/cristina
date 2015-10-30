class A:
    n = None

    # def __init__(self):
    #     self.n = 10

    def get_n(self, d):
        self.print_n()
        return self.n + d


class B(A):
    n = None

    def sum_n(self, v):
        return sum(v) + self.n


class C(B):
    n = 100

    def print_n(self):
        print self.n

c = C()
print c.get_n(5)
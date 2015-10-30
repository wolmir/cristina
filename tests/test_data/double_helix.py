import random

class Double_Helix(list):
    def __getslice__(self, i, j):
        return Double_Helix(list.__getslice__(self, i, j))

    def rotate_left(self):
        self.append(self.pop(0))

    def rotate_right(self):
        self.insert(0, self.pop(-1) )

    def swap_pair_1(self):
        temp = self.pop(0)
        self.insert(0, self.pop(-1))
        self.append( temp )

    def swap_pair_2(self):
        temp = self.pop(1)
        self.insert(1, self.pop(-2))
        self.insert(-1, temp)

    def swap_pair_3(self):
        temp = self.pop(2)
        self.insert(2, self.pop(-3))
        self.insert(-2, temp)

    def swap_pair_4(self):
        temp = self.pop(3)
        self.insert(3, self.pop(-4))
        self.insert(-3, temp)

    def swap_pair_5(self):
        temp = self.pop(4)
        self.insert(4, self.pop(-5))
        self.insert(-4, temp)

    def swap_pair_6(self):
        temp = self.pop(5)
        self.insert(5, self.pop(-6))
        self.insert(-5, temp)

    def random_mutation(self, nucleobases):
        rand_index = random.randrange(0, len(self)) 
        #print self[rand_index]
        nucleobases.remove( self[rand_index] )
        #print str(rand_index)
        rand_base = random.randrange(0, len(nucleobases) )
        self[ rand_index ] = nucleobases[ rand_base ]

from albow.controls import Label

class Nucleobase_Label(Label):
    def __init__(self, text, index=0):
        Label.__init__(self, text)
        self.index = index
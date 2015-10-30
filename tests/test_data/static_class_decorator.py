#Gambiarra para deixar uma classe estática. Não me pergunte por quê.
def staticclass(class_definition):
    def static_init(implicit_object, *args):
        raise AttributeError(class_definition.__name__ + " is a static class.")
    class_definition.__init__ = static_init
    return class_definition
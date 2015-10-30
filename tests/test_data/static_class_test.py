def staticclass(class_definition):
    def static_init(implicit_object, *args):
        raise AttributeError(class_definition.__name__ + " is a static class.")
    class_definition.__init__ = static_init
    return class_definition


@staticclass
class A:
    @staticmethod
    def m1():
        return 'me'

if __name__=='__main__':
    A(1,2)
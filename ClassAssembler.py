from AstClassWrapper import AstClassWrapperBuilder


class ClassAssembler(object):
    def __init__(self):
        self.current_chain = 0

    def assemble_classes(self, data):
        assembled = [self.chain_to_class(method_chain) for
            method_chain in data]
        if len(data) > 0:
            assembled.append(data[0].get_class_wrapper())
        return assembled

    def chain_to_class(self, method_chain):
        method_nodes = method_chain.get_method_nodes()
        wrapper = method_chain.get_class_wrapper()
        class_name = wrapper.get_class_name()
        class_name += str(self.current_chain)
        class_builder = AstClassWrapperBuilder(
            class_name,
            method_nodes,
            wrapper
        )
        self.current_chain += 1
        return class_builder.build_class(self.current_chain - 1)

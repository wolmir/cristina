import ast

import AstMethodNodeMiner


class InstanceReferencesFinder(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.instance_references = set([])

    def find_references(self, method_node):
        self.visit(method_node)
        return self.instance_references

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            if node.value.id == 'self':
                self.instance_references.add(node.attr)


class AstClassWrapper:
    def __init__(self, class_node):
        self.class_node = class_node
        self.method_nodes = AstMethodNodeMiner.AstMethodNodeMiner().find_nodes(class_node)
        self.method_names = set([method_node.name for method_node in self.method_nodes])
        self.instance_references = set([])
        for method_node in self.method_nodes:
            self.instance_references |= InstanceReferencesFinder().find_references(method_node)
        self.instance_variables = self.instance_references - self.method_names

    def get_method_names(self):
        return self.method_names

    def get_method_nodes(self):
        return self.method_nodes

    def get_class_node(self):
        return self.class_node

    def get_class_name(self):
        return self.class_node.name
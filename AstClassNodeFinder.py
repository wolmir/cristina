import ast


class AstClassNodeFinder(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.class_nodes = set([])

    def find_classes(self, source_root_node):
        self.visit(source_root_node)
        return self.class_nodes

    def visit_ClassDef(self, node):
        self.class_nodes.add(node)
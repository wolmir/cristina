import ast


class AstMethodNodeMiner(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.method_nodes = []

    def find_nodes(self, source_root_node):
        self.visit(source_root_node)
        return self.method_nodes

    def visit_FunctionDef(self, node):
        if node.name != '__init__':
            self.method_nodes.append(node)
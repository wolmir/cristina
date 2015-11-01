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


class InstanceVariablesFinder(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.instance_variables = set([])

    def find_variables(self, class_node):
        self.visit(class_node)
        return self.instance_variables

    def visit_Assign(self, node):
        for target in node.targets:
            self.visit(target)

    def visit_Name(self, node):
        print node.id
        self.instance_variables.add(node.id)

    def visit_Tuple(self, node):
        for element in node.elts:
            self.visit(element)

    #Method nodes can't be visited.
    def visit_FunctionDef(self, node):
        return


class AstClassWrapper:
    def __init__(self, class_node):
        self.class_node = class_node
        self.method_nodes = AstMethodNodeMiner.AstMethodNodeMiner().find_nodes(
            class_node)
        self.method_names = [method_node.name 
            for method_node in self.method_nodes]
        self.instance_references = set([])
        for method_node in self.method_nodes:
            self.instance_references |= InstanceReferencesFinder().find_references(method_node)
        self.instance_variables = self.instance_references - set(self.method_names)
        self.instance_variables |= InstanceVariablesFinder().find_variables(class_node)

    def get_method_names(self):
        return self.method_names

    def get_method_nodes(self):
        return self.method_nodes

    def get_class_node(self):
        return self.class_node

    def get_class_name(self):
        return self.class_node.name

    def get_instance_variables(self):
        return self.instance_variables


class AstClassWrapperBuilder:
    def __init__(self, name, method_nodes):
        self.name = name
        self.method_nodes = method_nodes
        self.fields = set([])
        field_finder = InstanceReferencesFinder()
        for node in method_nodes:
            self.fields |= field_finder.find_references(node)


    def build_class(self):
        named_fields = [ast.Name(id=field, ctx=ast.Store())
            for field in self.fields]
        field_assignments = [ast.Assign(targets=[named_field], 
                value=ast.Name(id='None', ctx=ast.Load()))
            for named_field in named_fields]
        class_node = ast.ClassDef(name=self.name,
            bases=[], body=field_assignments + 
                self.method_nodes, decorator_list=[])
        return AstClassWrapper(class_node)

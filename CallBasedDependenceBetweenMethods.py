import ast

import Metric


class MethodCallsVisitor(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.method_name = ""
        self.method_calls = 0

    def count_calls_in_method_node_to_method_name(self, method_node, method_name):
        self.method_name = method_name
        self.visit(method_node)
        return self.method_calls

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            if node.value.id == 'self':
                if node.attr == self.method_name:
                    self.method_calls += 1
        self.generic_visit(node)


class CallBasedDependenceBetweenMethods(Metric.Metric):
    def __init__(self):
        Metric.Metric.__init__(self)

    def count_calls(self, method_node1, method_node2):
        method2_name = method_node2.name
        return MethodCallsVisitor().count_calls_in_method_node_to_method_name(method_node1, method2_name)

    def count_calls_in(self, called_method_node, class_wrapper):
        calls_in = 0
        called_method_name = called_method_node.name
        for method_node in class_wrapper.get_method_nodes():
            if method_node.name != called_method_name:
                calls_in += \
                    MethodCallsVisitor().count_calls_in_method_node_to_method_name(method_node, called_method_name)
        return calls_in

    def __calculate(self, method_node1, method_node2, class_wrapper):
        calls_m1_m2 = self.count_calls(method_node1, method_node2)
        calls_in = self.count_calls_in(method_node2, class_wrapper)
        if calls_in > 0:
            return (calls_m1_m2 * 1.0) / calls_in
        return 0.0

    def calculate(self, method_node1, method_node2, class_wrapper):
        m12 = self.__calculate(method_node1, method_node2, class_wrapper)
        m21 = self.__calculate(method_node2, method_node1, class_wrapper)
        return max(m12, m21)
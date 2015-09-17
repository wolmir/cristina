import Metric
import ast


class StructuralSimilarityBetweenMethods(Metric.Metric):

    class InstanceVariablesFinder(ast.NodeVisitor):

        def __init__(self):
            ast.NodeVisitor.__init__(self)
            self.instance_variables = set([])
            self.method_names = set([])

        def find_variables(self, method_node, class_wrapper):
            self.method_names = class_wrapper.get_method_names()
            self.visit(method_node)
            return self.instance_variables

        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name):
                if node.value.id == 'self':
                    if not node.attr in self.method_names:
                        self.instance_variables.add(node.attr)
            self.generic_visit(node)

    def __init__(self):
        Metric.Metric.__init__(self)

    def calculate(self, method_node1, method_node2, class_wrapper):
        method1_variables = self.find_instance_variables(method_node1, class_wrapper)
        method2_variables = self.find_instance_variables(method_node2, class_wrapper)
        common_variables = method1_variables & method2_variables
        all_variables = method1_variables | method2_variables
        if len(all_variables) == 0:
            return 0.0
        return (len(common_variables) * 1.0) / len(all_variables)

    def find_instance_variables(self, method_node, class_wrapper):
        instance_variables_finder = StructuralSimilarityBetweenMethods.InstanceVariablesFinder()
        return instance_variables_finder.find_variables(method_node, class_wrapper)


def main():
    pass


if __name__ == '__main__':
    main()

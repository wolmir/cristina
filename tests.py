import ast

import StructuralSimilarityBetweenMethods
import CallBasedDependenceBetweenMethods
import AstClassNodeMiner
import AstClassWrapper
import MethodMatrix


def loop_through_methods(method_list, func):
    for i in range(0, len(method_list)):
        for j in range(0, len(method_list)):
            if i == j:
                continue
            func(method_list[i], method_list[j])


def main():
    with open("metric_test_source_codes.py") as source_file:
        code = source_file.read()
        file_node = ast.parse(code)
        astClassNodeMiner = AstClassNodeMiner.AstClassNodeMiner()
        class_nodes = astClassNodeMiner.find_classes(file_node)
        ssm = StructuralSimilarityBetweenMethods.StructuralSimilarityBetweenMethods()
        cdm = CallBasedDependenceBetweenMethods.CallBasedDependenceBetweenMethods()
        for class_node in class_nodes:
            class_wrapper = AstClassWrapper.AstClassWrapper(class_node)
            #method_miner = AstMethodNodeMiner.AstMethodNodeMiner()
            print ""
            print "Class: " + class_wrapper.get_class_name()
            method_nodes = class_wrapper.get_method_nodes()
            for i in range(0, len(method_nodes) - 1):
                for j in range(i + 1, len(method_nodes)):
                    print "Methods: " + method_nodes[i].name + ", " + method_nodes[j].name
                    #print ast.dump(method_nodes[i])
                    print ssm.calculate(method_nodes[i], method_nodes[j], class_wrapper)
                    print cdm.calculate(method_nodes[i], method_nodes[j], class_wrapper)
            method_matrix = MethodMatrix.MethodMatrix(class_wrapper)
            method_matrix.build_matrix([ssm, cdm], [0.5, 0.5])
            method_matrix.print_matrix()


if __name__ == '__main__':
    main()
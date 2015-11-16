from MatrixSplitter import MatrixSplitter

class MethodChain(object):
    def __init__(self, method_matrix, method_nodes):
        self.method_matrix = method_matrix
        self.method_ast_nodes = [
            self.method_matrix.get_node(node) for node in method_nodes]

    def get_coupling(self, method_chain, metrics, weights):
        method_pairs = [(x, y) for x in self.method_ast_nodes
            for y in method_chain.method_ast_nodes]
        average_coupling = 0.0
        for method_pair in method_pairs:
            for metric, weight in zip(metrics, weights):
                average_coupling += weight * metric.calculate(
                    method_pair[0],
                    method_pair[1],
                    self.method_matrix.ast_class_wrapper)
        average_coupling *= 1.0 / len(method_pairs)
        return average_coupling

    def merge(self, method_chain):
        self.method_ast_nodes = list(
            set(self.method_ast_nodes) | set(method_chain.method_ast_nodes))

    def get_method_names(self):
        return [node.name for node in self.method_ast_nodes]

    def get_method_nodes(self):
        return self.method_ast_nodes

    def get_length(self):
        return len(self.method_ast_nodes)

    def get_class_wrapper(self):
        return self.method_matrix.get_class_wrapper()


class MethodChainsAssembler(object):
    @staticmethod
    def assemble(method_matrix):
        matrix_splitter = MatrixSplitter(method_matrix)
        subgraphs = matrix_splitter.split_matrix()
        method_chains = [MethodChain(method_matrix, method_nodes)
            for method_nodes in subgraphs]
        return method_chains

import copy

class MethodMatrix:
    def __init__(self, metrics, weights):
        self.matrix = []
        self.ast_class_wrapper = None
        self.method_nodes = []
        self.weights = weights
        self.metrics = metrics

    def build_matrix(self, ast_class_wrapper):
        self.clear_matrix()
        self.ast_class_wrapper = ast_class_wrapper
        self.method_nodes = self.ast_class_wrapper.get_method_nodes()
        # pdb.set_trace()
        for i in range(0, len(self.method_nodes)):
            self.matrix.append([])
            for j in range(0, len(self.method_nodes)):
                self.matrix[i].append(0.0)
        for i in range(0, len(self.method_nodes)):
            for j in range(0, len(self.method_nodes)):
                if i == j:
                    self.matrix[i][j] = 1.0
                elif i > j:
                    self.matrix[i][j] = self.matrix[j][i]
                else:
                    for w in range(0, len(self.metrics)):
                        measure = self.metrics[w].calculate(
                            self.method_nodes[i], self.method_nodes[j],
                            self.ast_class_wrapper)
                        self.matrix[i][j] += self.weights[w] * measure
        return copy.copy(self)

    def clear_matrix(self):
        self.matrix = []

    def print_matrix(self):
        for line in self.matrix:
            print line
        print ""

    def get_matrix(self):
        return self.matrix

    def set_matrix(self, matrix):
        self.matrix = matrix

    def get_node(self, node):
        return self.method_nodes[node]

    def get_metrics(self):
        return self.metrics

    def set_metrics(self, metrics):
        self.metrics = metrics

    def add_metric(self, metric):
        self.metrics.append(metric)

    def get_class_wrapper(self):
        return self.ast_class_wrapper

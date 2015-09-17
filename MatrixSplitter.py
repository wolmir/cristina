import MethodMatrix


class MatrixSplitter:
    def __init__(self, method_matrix, min_coupling):
        self.matrix = method_matrix.get_matrix()
        self.min_coupling = min_coupling
        #self.subgraphs = []
        #self.unlabelled_nodes = [[node] for node in range(len(self.matrix))]
        #self.labelled_nodes = []


    @staticmethod
    def split_graph(graph):
        subgraphs = []
        unlabelled_nodes = graph.get_nodes()
        while unlabelled_nodes:
            labelled_nodes = []
            MatrixSplitter.flood_fill(unlabelled_nodes[0], labelled_nodes, unlabelled_nodes, [])
            subgraphs.append(labelled_nodes)
        return subgraphs

    @staticmethod
    def flood_fill(node, labelled, unlabelled, visited):
        visited.append(node)
        for adjacent_node in node.adjacent_nodes():
            if not adjacent_node in visited:
                MatrixSplitter.flood_fill(adjacent_node, labelled, unlabelled, visited)
        unlabelled.remove(node)
        labelled.append(node)

    # def split_graph(self):
    #     while self.unlabeled_nodes:
    #         unlabeled_node = self.unlabeled_nodes[0]
    #         self.labeled_nodes.append(unlabeled_node)
    #         self.unlabeled_nodes.remove(unlabeled_node)
    #         self.flood_fill(unlabeled_node, 0)
    #
    # def flood_fill(self, unlabeled_node, last_index):
    #     for node in range(0, len(self.matrix[last_index])):
    #         if self.matrix[last_index][node] > self.min_coupling:
    #             unlabeled_node.append(node)
    #             self.flood_fill(unlabeled_node, last_index + 1)
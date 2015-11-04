class MatrixToGraphAdapter(object):
    def __init__(self, method_matrix):
        self.method_matrix = method_matrix.get_matrix()

    def get_nodes(self):
        return range(len(self.method_matrix))

    def adjacent_nodes(self, node):
        return [x for x in self.get_nodes()
            if self.method_matrix[node][x] > 0 and x != node]

class MatrixSplitter:
    def __init__(self, method_matrix):
        self.matrix = method_matrix

    def split_matrix(self):
        return GraphSplitter.split_graph(
            MatrixToGraphAdapter(self.matrix))


class GraphSplitter(object):
    @staticmethod
    def split_graph(graph):
        subgraphs = []
        unlabelled_nodes = graph.get_nodes()
        while unlabelled_nodes:
            labelled_nodes = []
            GraphSplitter.flood_fill(graph, unlabelled_nodes[0],
                labelled_nodes, unlabelled_nodes, [])
            subgraphs.append(labelled_nodes)
        return subgraphs

    @staticmethod
    def flood_fill(graph, node, labelled, unlabelled, visited):
        visited.append(node)
        for adjacent_node in graph.adjacent_nodes(node):
            if not adjacent_node in visited:
                GraphSplitter.flood_fill(graph, adjacent_node, labelled,
                    unlabelled, visited)
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

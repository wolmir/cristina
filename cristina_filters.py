import re
import os
import ast
import pypeline
import logging
import pdb
from AstClassNodeFinder import AstClassNodeFinder
from AstClassWrapper import AstClassWrapper
from MethodMatrix import MethodMatrix
from MethodChainFilter import MethodChainFilter
from MethodChainsAssembler import MethodChainsAssembler
from TrivialChainMerger import TrivialChainMerger
from ClassAssembler import ClassAssembler
from AstToCodeTransformer import AstToCodeTransformer


def print_matrix(matrix):
    if len(matrix) == 0:
        return '[]'
    fmatrix = [['%.2f' % col for col in row]
        for row in matrix]
    ret_s = '     '.join([' '] + [str(c) for c in range(len(fmatrix[0]))]) +\
     "\n"
    for n, row in enumerate(fmatrix):
        ret_s += '  '.join([str(n)] + row) + "\n"
    return ret_s + '\n'


class CrisDataSourceSingleFile(pypeline.DataSource):
    def __init__(self, file_path):
        pypeline.DataSource.__init__(self)
        self.data = []
        with open(file_path, 'r') as source_file:
            self.data.append(source_file.read())

    def has_next(self):
        return len(self.data) > 0

    def next(self):
        return self.data.pop()

class InvalidPathException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class CrisDataSourceDirectory(pypeline.DataSource):
    python_file_pattern = re.compile(r".+\.py$")

    def __init__(self, path):
        if not os.path.exists(path):
            raise InvalidPathException("The path doesn't exist.")
        pypeline.DataSource.__init__(self)
        self.file_paths = self.load_files(path)

    def load_files(self, path):
        file_paths = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                if CrisDataSourceDirectory.python_file_pattern.match(filename):
                    file_path = os.path.join(root, filename)
                    file_paths.append(file_path)
        return file_paths

    def has_next(self):
        return len(self.file_paths) > 0

    def next(self):
        next_path = self.file_paths.pop()
        # logging.warning("CrisDataSourceDirectory::next: " + next_path)
        with open(next_path, 'r') as open_file:
            return open_file.read()
        return None


class CrisDataSourceFactory(object):
    @staticmethod
    def create(path, recursive=False):
        if recursive:
            return CrisDataSourceDirectory(path)
        return CrisDataSourceSingleFile(path)


class CrisCodeToAstTransformer(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    @staticmethod
    def code_to_ast(code):
        ast_node = None
        try:
            ast_node = ast.parse(code)
        except SyntaxError:
            logging.warning("CrisCodeToAstTransformer: SyntaxError while" +
                " trying to parse the source_code. Ignoring the source.")
        return ast_node

    def filter_process(self, data):
        return CrisCodeToAstTransformer.code_to_ast(data)


class CrisClassNodeFinder(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    @staticmethod
    def find_class_nodes(ast_node):
        class_node_finder = AstClassNodeFinder()
        return list(class_node_finder.find_classes(ast_node))

    def filter_process(self, data):
        output = CrisClassNodeFinder.find_class_nodes(data)
        if len(output) == 0:
            return None
        return output


class CrisAstClassWrapper(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    @staticmethod
    def wrap_class_node(class_node):
        return AstClassWrapper(class_node)

    def filter_process(self, data):
        return [CrisAstClassWrapper.wrap_class_node(item)
            for item in data]


class CrisMethodByMethodMatrix(pypeline.Filter):
    def __init__(self, metrics_with_weights):
        pypeline.Filter.__init__(self)
        self.weights = [item[1] for item in metrics_with_weights]
        self.metrics = [item[0] for item in metrics_with_weights]
        self.method_matrix_builder = MethodMatrix(self.metrics, self.weights)

    def build_method_matrix(self, class_wrapper):
        matrix = self.method_matrix_builder.build_matrix(class_wrapper)
        logging.warning("CrisMethodByMethodMatrix::" +
            "build_method_matrix:\n" + print_matrix(matrix.matrix))
        return matrix

    def filter_process(self, data):
        matrices = [self.build_method_matrix(item)
            for item in data]
        for mat in matrices:
            logging.warning("CrisMethodByMethodMatrix::" +
                "matrix:\n" + print_matrix(mat.matrix))
        return matrices


class CrisChainsOfMethodsFilterFactory(object):
    @staticmethod
    def create(min_coupling):
        if min_coupling:
            return CrisCOMConstantThresholdFilter(min_coupling)
        return CrisCOMVariableThresholdFilter()


class CrisCOMConstantThresholdFilter(pypeline.Filter):
    def __init__(self, min_coupling):
        pypeline.Filter.__init__(self)
        self.method_chain_filter = MethodChainFilter(min_coupling)

    def filter_process(self, data):
        for item in data:
            logging.warning("CrisCOMConstantThresholdFilter::matrix:\n"
                + print_matrix(item.matrix))
            item.set_matrix(self.method_chain_filter.filter_matrix(item))
        return data


class CrisCOMVariableThresholdFilter(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)
        self.method_chain_filter = MethodChainFilter(0.0)

    def filter_matrix(self, matrix):
        if len(matrix.get_matrix()) > 0:
            median = CrisCOMVariableThresholdFilter.calculate_median(
                matrix.get_matrix())
            self.method_chain_filter.set_min_coupling(median)
            matrix.set_matrix(self.method_chain_filter.filter_matrix(matrix))
        return matrix

    def filter_process(self, data):
        return [self.filter_matrix(matrix) for matrix in data]

    @staticmethod
    def calculate_median(matrix):
        biggest_value = max([max(row) for row in matrix])
        smallest_value = min([min(row) for row in matrix])
        return (biggest_value + smallest_value) / 2.0


class CrisMethodChainsAssembler(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        chains = [MethodChainsAssembler.assemble(item) for item in data]
        if len(chains) > 0:
            logging.warning("CrisMethodChainsAssembler: chains: " +
                str(len(chains[0])))
        return chains


class CrisTrivialChainMerger(pypeline.Filter):
    def __init__(self, metrics, min_length):
        pypeline.Filter.__init__(self)
        self.weights = [m[1] for m in metrics]
        self.metrics = [m[0] for m in metrics]
        self.trivial_chain_merger = TrivialChainMerger(min_length,
            self.metrics,
            self.weights)

    def filter_process(self, data):
        merged_chains = [self.trivial_chain_merger.merge_chains(item)
            for item in data]
        logging.warning("CrisTrivialChainMerger::merged_chains: " +
            str(merged_chains))
        return merged_chains


class CrisClassAssembler(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        assembled_classes = [ClassAssembler().assemble_classes(item)
            for item in data]
        #pdb.set_trace()
        logging.warning("CrisClassAssembler::assembled_classes: " +
            str(assembled_classes))
        return assembled_classes

class CrisAstToCodeTransformer(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        return [[AstToCodeTransformer.transform(class_wrapper.get_class_node())
            for class_wrapper in item] for item in data]


class CrisDataSink(pypeline.DataSink):
    def __init__(self, output_path):
        pypeline.DataSink.__init__(self)
        self.output_file = open(output_path, 'w')

    def handle_output(self, data):
        for item in data:
            for class_code in item:
                self.output_file.write(class_code + '\n\n')

    def close_sink(self):
        self.output_file.close()

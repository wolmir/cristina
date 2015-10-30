import re
import os
import ast
import pypeline
from AstClassNodeFinder import AstClassNodeFinder
from AstClassWrapper import AstClassWrapper
from MethodMatrix import MethodMatrix
from MethodChainFilter import MethodChainFilter
from MethodChainsAssembler import MethodChainsAssembler
from TrivialChainMerger import TrivialChainMerger
from ClassAssembler import ClassAssembler
from AstToCodeTransformer import AstToCodeTransformer


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


class CrisDataSourceDirectory(pypeline.DataSource):
    python_file_pattern = re.compile(r".+\.py$")

    def __init__(self, path):
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
        with open(self.file_paths.pop(), 'r') as open_file:
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
        return ast.parse(code)

    def filter_process(self, data):
        return CrisCodeToAstTransformer.code_to_ast(data)


class CrisClassNodeFinder(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    @staticmethod
    def find_class_nodes(ast_node):
        class_node_finder = AstClassNodeFinder()
        return class_node_finder.find_classes(ast_node)

    def filter_process(self, data):
        return CrisClassNodeFinder.find_class_nodes(data)


class CrisAstClassWrapper(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    @staticmethod
    def wrap_class_node(class_node):
        return AstClassWrapper(class_node)

    def filter_process(self, data):
        return CrisAstClassWrapper.wrap_class_node(data)


class CrisMethodByMethodMatrix(pypeline.Filter):
    def __init__(self, metrics, weight_ssm, weight_cdm):
        pypeline.Filter.__init__(self)
        self.weights = []
        self.weights.append(weight_cdm)
        self.weights.append(weight_ssm)
        self.metrics = metrics

    def build_method_matrix(self, class_wrapper):
        method_matrix_builder = MethodMatrix(class_wrapper, self.metrics)
        return method_matrix_builder.build_matrix(self.weights)

    def filter_process(self, data):
        return self.build_method_matrix(data)


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
        data.set_matrix(self.method_chain_filter.filter_matrix(data))
        return data


class CrisCOMVariableThresholdFilter(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)
        self.method_chain_filter = MethodChainFilter(0.0)

    def filter_process(self, data):
        median = CrisCOMVariableThresholdFilter.calculate_median(
            data.get_matrix())
        self.method_chain_filter.set_min_coupling(median)
        data.set_matrix(self.method_chain_filter.filter_matrix(data))
        return data

    @staticmethod
    def calculate_median(matrix):
        biggest_value = max([max(row) for row in matrix])
        smallest_value = min([min(row) for row in matrix])
        return (biggest_value + smallest_value) / 2.0


class CrisMethodChainsAssembler(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        return MethodChainsAssembler.assemble(data)


class CrisTrivialChainMerger(pypeline.Filter):
    def __init__(self, metrics, weight_ssm, weight_cdm, min_length):
        pypeline.Filter.__init__(self)
        self.weights = []
        self.weights.append(weight_cdm)
        self.weights.append(weight_ssm)
        self.trivial_chain_merger = TrivialChainMerger(min_length, metrics,
            self.weights)

    def filter_process(self, data):
        return self.trivial_chain_merger.merge_chains(data)


class CrisClassAssembler(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        return ClassAssembler().assemble_classes(data)

class CrisAstToCodeTransformer(pypeline.Filter):
    def __init__(self):
        pypeline.Filter.__init__(self)

    def filter_process(self, data):
        return [AstToCodeTransformer.transform(class_wrapper.get_class_node())
            for class_wrapper in data]


class CrisDataSink(pypeline.DataSink):
    def __init__(self, output_path):
        pypeline.DataSink.__init__(self)
        self.output_file = open(output_path, 'w')

    def handle_output(self, data):
        for class_code in data:
            self.output_file.write(class_code)

    def close_sink(self):
        self.output_file.close()

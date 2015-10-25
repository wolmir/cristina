"""Define Cristina and execute it."""
import argparse
import pypeline
import os
import ast
from AstClassNodeFinder import AstClassNodeFinder
from AstClassWrapper import AstClassWrapper
from StructuralSimilarityBetweenMethods import \
    StructuralSimilarityBetweenMethods
from CallBasedDependenceBetweenMethods import \
    CallBasedDependenceBetweenMethods
from MethodMatrix import MethodMatrix
from MethodChainFilter import MethodChainFilter

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
    def __init__(self, path):
        pypeline.DataSource.__init__(self)
        self.file_paths = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                self.file_paths.append(file_path)

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
    def __init__(self, weight_ssm, weight_cdm):
        pypeline.Filter.__init__(self)
        self.weights = []
        self.weights.append(weight_cdm)
        self.weights.append(weight_ssm)
        self.metrics = []
        self.metrics.append(StructuralSimilarityBetweenMethods())
        self.metrics.append(CallBasedDependenceBetweenMethods())

    def build_method_matrix(self, class_wrapper):
        method_matrix_builder = MethodMatrix(class_wrapper)
        return method_matrix_builder.build_matrix(self.metrics, self.weights)

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
        return MethodChainAssembler.assemble(data)

class Cristina(object):
    """Parse arguments and create the pipeline."""
    def __init__(self):
        """Parse arguments."""
        parser = argparse.ArgumentParser()
        # Main argument. Specify a file or directory
        # to be processed
        parser.add_argument("path", help="Source path. Can be a Python file" + \
            " or a directory with the -r or --recursive option.")
        parser.add_argument("-r", "--recursive", help="Process a target " + \
            "directory recursively.", action="store_true")
        parser.add_argument("-c", "--configuration-file", help="Specify a " + \
            "configuration file.")
        parser.add_argument("-w-ssm", "" + \
            "--weight-structural-similarity-between-methods", help="Weight" + \
            " for the SSM metric.", type=float)
        parser.add_argument("-w-cdm", "" + \
            "--weight-call-based-dependence-between-methods", help="Weight" + \
            " for the CDM metric.", type=float)
        parser.add_argument("-mC", "--min-coupling", help="Minimum coupling" + \
            " value for the method-by-method matrix.", type=float)
        parser.add_argument("-mL", "--min-length", help="Minimum length for" + \
            " a method chain. Defaults to 1.", type=int)
        parser.add_argument("-o", "--output-path", help="The path for a " + \
            "file or directory where the refactored classes will be stored.")
        parser.add_argument("-rF", "--report-file", help="File where the " + \
            "report will be stored.")
        self.args = parser.parse_args()
        self.pipeline = None


    def create_pipeline(self):
        """Create the pipeline."""
        pipeline = pypeline.Pipeline()
        python_code_data_source = CrisDataSourceFactory.create(self.args.path,
            self.args.recursive)
        pipeline.set_data_source(python_code_data_source)
        code_to_ast_filter = CrisCodeToAstTransformer()
        pipeline.connect(code_to_ast_filter)
        class_finder_filter = CrisClassNodeFinder()
        pipeline.connect(class_finder_filter)
        class_wrapping_filter = CrisAstClassWrapper()
        pipeline.connect(class_wrapping_filter)
        method_matrix_filter = CrisMethodByMethodMatrix(
            self.args.weight_structural_similarity_between_methods,
            self.args.weight_call_based_dependence_between_methods)
        pipeline.connect(method_matrix_filter)
        chains_of_methods_filter = CrisChainsOfMethodsFilterFactory.create(
            self.args.min_coupling)
        pipeline.connect(chains_of_methods_filter)
        method_chains_assembler_filter = CrisMethodChainsAssembler()
        pipeline.connect(method_chains_assembler_filter)
        trivial_chains_merging_filter = CrisTrivialChainMerger(
            self.args.min_length)
        pipeline.connect(trivial_chains_merging_filter)
        ast_to_code_filter = CrisAstToCodeTransformer()
        pipeline.connect(ast_to_code_filter)
        python_code_data_sink = CrisDataSink(self.args.output_path)
        pipeline.set_data_sink(python_code_data_sink)
        self.pipeline = pipeline


    def main(self):
        """Run the pipeline"""
        self.pipeline = self.create_pipeline()
        self.pipeline.run()


if __name__ == '__main__':
    Cristina().main()

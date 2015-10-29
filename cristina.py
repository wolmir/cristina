"""Define Cristina and execute it."""
import argparse
import pypeline
from StructuralSimilarityBetweenMethods import \
    StructuralSimilarityBetweenMethods
from CallBasedDependenceBetweenMethods import \
    CallBasedDependenceBetweenMethods
from cristina_filters import *


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
        metrics = [CallBasedDependenceBetweenMethods(),
            StructuralSimilarityBetweenMethods()]
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
        method_matrix_filter = CrisMethodByMethodMatrix(metrics,
            self.args.weight_structural_similarity_between_methods,
            self.args.weight_call_based_dependence_between_methods)
        pipeline.connect(method_matrix_filter)
        chains_of_methods_filter = CrisChainsOfMethodsFilterFactory.create(
            self.args.min_coupling)
        pipeline.connect(chains_of_methods_filter)
        method_chains_assembler_filter = CrisMethodChainsAssembler()
        pipeline.connect(method_chains_assembler_filter)
        trivial_chains_merging_filter = CrisTrivialChainMerger(metrics,
            self.args.weight_structural_similarity_between_methods,
            self.args.weight_call_based_dependence_between_methods,
            self.args.min_length)
        pipeline.connect(trivial_chains_merging_filter)
        class_assembler_filter = CrisClassAssembler()
        pipeline.connect(class_assembler_filter)
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

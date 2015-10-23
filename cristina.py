"""Define Cristina and execute it."""
import argparse
import pipeline
import os

class CristinaDataSourceSingleFile(pipeline.DataSource):
    def __init__(self, file_path):
        pipeline.DataSource.__init__(self)
        self.data = []
        with open(file_path, 'r') as source_file:
            self.data.append(source_file.read())

    def has_next(self):
        return len(self.data) > 0

    def next(self):
        return self.data.pop()


class CristinaDataSourceDirectory(pipeline.DataSource):
    def __init__(self, path):
        pipeline.DataSource.__init__(self)
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


class CristinaDataSourceFactory:
    @staticmethod
    def create(path, recursive=False):
        if recursive:
            return CristinaDataSourceDirectory(path)
        return CristinaDataSourceSingleFile(path)

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
        pipeline = Pipeline()
        python_code_data_source = CrisDataSourceFactory.create(self.args.path,
            self.args.recursive)
        pipeline.set_data_source(python_code_data_source)
        code_to_ast_filter = CrisCodeToAstTransformer()
        pipeline.connect(code_to_ast_filter)
        class_finder_filter = CrisClassNodeFinder()
        pipeline.connect(class_finder_filter)
        method_matrix_filter = CrisMethodByMethodMatrixBuilder(
            self.args.weight_structural_similarity_between_methods,
            self.args.weight_call_based_dependence_between_methods)
        pipeline.connect(method_matrix_filter)
        class_extractor_filter = CrisClassExtractor(self.args.min_coupling)
        pipeline.connect(class_extractor_filter)
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

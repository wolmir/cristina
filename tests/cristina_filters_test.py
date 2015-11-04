import pytest
import os
import ast
import logging
import astpp

from conftest import *
from copy import deepcopy
from cristina_filters import *
from AstClassWrapper import *
from StructuralSimilarityBetweenMethods import *
from CallBasedDependenceBetweenMethods import *


logging.basicConfig(filename='pytest.log', level=logging.DEBUG)

# TEST_DATA_DIR = 'tests/test_data'
# TEST_TMP_DIR = ''


class TestCrisDataSourceSingleFile:
    def test_next(self, create_file):
        file_data = ''
        with open(create_file.name, 'r') as tmp_file:
            file_data = tmp_file.read()
        cdssf = CrisDataSourceSingleFile(create_file.name)
        assert cdssf.next() == file_data

    def test_has_next(self, create_file):
        cdssf = CrisDataSourceSingleFile(create_file.name)
        assert cdssf.has_next()
        cdssf.next()
        assert cdssf.has_next() == False


class TestCrisDataSourceDirectory:
    def test_regex_python_pattern(self):
        assert CrisDataSourceDirectory.python_file_pattern.match("skfgg.py")
        assert not CrisDataSourceDirectory.python_file_pattern.match(
            "skfgg.pyc")

    def test_constructor(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        assert cdsd != None

    def test_load_files(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        file_paths = cdsd.load_files(tmp_dir)
        assert file_paths != None
        assert len(file_paths) > 0
        for python_file in list_of_python_files:
            assert python_file in file_paths

    def test_post_constructor(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        assert cdsd.file_paths != None
        assert len(cdsd.file_paths) > 0

    def test_next(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        for python_file in list_of_python_files:
            next_file = cdsd.next()
            assert next_file != None
        with pytest.raises(IndexError):
            cdsd.next()

    def test_has_next(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        assert cdsd.has_next()
        for python_file in list_of_python_files:
            cdsd.next()
        assert not cdsd.has_next()


class TestCrisCodeToAstTransformer:
    def test_code_to_ast(self, list_of_python_files):
        cctat = CrisCodeToAstTransformer()
        for python_file in list_of_python_files:
            with open(python_file, 'r') as source_file:
                source_code = source_file.read()
                ast_dump = None
                try:
                    ast_dump = ast.dump(ast.parse(source_code))
                except SyntaxError:
                    pass
                cctat_dump = None
                cctat_ast = cctat.code_to_ast(source_code)
                if cctat_ast:
                    cctat_dump = ast.dump(cctat_ast)
                assert cctat_dump == ast_dump


class TestCrisClassNodeFinder:
    def test_find_class_nodes(self, list_of_python_files):
        for python_file in list_of_python_files:
            source_code = ""
            with open(python_file, 'r') as source:
                source_code = source.read()
            ast_node = None
            try:
                ast_node = ast.parse(source_code)
            except SyntaxError:
                continue
            class_finder = ClassFinder()
            class_finder.visit(ast_node)
            #class_nodes = CrisClassNodeFinder.find_class_nodes(ast_node)
            #class_dict = pyclbr.readmodule(python_file[:-3], path=[TEST_DATA_DIR])
            assert len(CrisClassNodeFinder.find_class_nodes(ast_node)) == \
                len(class_finder.class_nodes)
            for node_a in CrisClassNodeFinder.find_class_nodes(ast_node):
                assert ast.dump(node_a) in [ast.dump(node_b)
                    for node_b in class_finder.class_nodes]


class TestAstClassWrapper:
    def test_constructor(self, list_of_ast_class_nodes):
        for python_file, node, class_nodes in list_of_ast_class_nodes:
            for class_node in class_nodes:
                class_wrapper = AstClassWrapper(class_node)
                assert class_wrapper != None
                assert len(class_wrapper.method_nodes) == \
                    len(class_wrapper.method_names)

    @pytest.mark.skipif(True, reason="Not working right now.")
    def test_get_instance_variables(self, custom_python_code):
        custom_fields_by_class_name = \
        {
            'SomeClass': ['some_var', 'var1', 'var2', 'yet_another_var', 'var3']
        }
        ast_node = ast.parse(custom_python_code)
        class_finder = ClassFinder()
        class_finder.visit(ast_node)
        class_nodes = class_finder.class_nodes_dict
        for class_name in class_nodes.keys():
            class_node = class_nodes[class_name]
            class_fields = custom_fields_by_class_name[class_name]
            ast_wrapper = AstClassWrapper(class_node)
            ast_wrapper_instance_vars = ast_wrapper.get_instance_variables()
            assert len(ast_wrapper_instance_vars) > 0
            assert len(class_fields) == len(ast_wrapper_instance_vars)
            assert len(ast_wrapper_instance_vars - set(class_fields)) == 0

    def test_get_method_nodes(self, custom_python_code):
        import imp
        custom_dir = os.path.join(TEST_DATA_DIR, 'custom_data')
        fname = os.path.join(custom_dir, 'python_file_for_input.py')
        mod = imp.load_source("python_file_for_input", fname)
        ast_node = ast.parse(custom_python_code)
        class_finder = ClassFinder()
        class_finder.visit(ast_node)
        class_nodes = class_finder.class_nodes_dict
        for class_name in class_nodes.keys():
            class_node = class_nodes[class_name]
            ast_wrapper = AstClassWrapper(class_node)
            no_of_methods = mod.get_number_of_methods(class_name)
            assert len(ast_wrapper.get_method_nodes()) == no_of_methods


class TestCrisMethodByMethodMatrix:
    custom_code_fname = "method_matrix_input.py"

    def get_matrix_factory(self):
        import imp
        custom_dir = os.path.join(TEST_DATA_DIR, 'custom_data')
        fname = os.path.join(custom_dir, self.custom_code_fname)
        mod = imp.load_source("method_matrix_input", fname)
        return mod.get_method_matrix

    @pytest.mark.skipif(MAX_NO_OF_FILES >= 50, reason='Takes too long.')
    def test_for_crashes(self, list_of_ast_class_nodes):
        counter = 0
        for python_file, node, class_nodes in list_of_ast_class_nodes:
            for class_node in class_nodes:
                ast_wrapper = AstClassWrapper(class_node)
                weight_ssm = 0.5
                weight_cdm = 0.5
                metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
                    (CallBasedDependenceBetweenMethods(), weight_cdm)]
                cmmm = CrisMethodByMethodMatrix(metrics)
                assert cmmm.build_method_matrix(ast_wrapper) != None
                counter += 1

    def test_build_method_matrix(self, custom_python_code):
        ast_node = ast.parse(custom_python_code)
        class_finder = ClassFinder()
        class_finder.visit(ast_node)
        weight_ssm = 0.7
        weight_cdm = 0.3
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        class_nodes = class_finder.class_nodes_dict
        matrix_factory = self.get_matrix_factory()
        #method_matrices = self.get_method_matrices()
        for class_name in class_nodes.keys():
            custom_matrix = matrix_factory(class_name, weight_ssm, weight_cdm)
            class_node = class_nodes[class_name]
            ast_wrapper = AstClassWrapper(class_node)
            method_matrix = cmmm.build_method_matrix(ast_wrapper)
            matrix = method_matrix.matrix
            no_of_nodes = len(method_matrix.method_nodes)
            mm_weights = method_matrix.weights
            assert matrix == custom_matrix


class TestCrisCOMConstantThresholdFilter:

    def has_value_less_than(self, matrix, value):
        for row in matrix:
            if len(filter(lambda x: x <= value and x > 0, row)) > 0:
                return True
        return False

    @pytest.mark.skipif(MAX_NO_OF_FILES >= 50, reason='Takes too long.')
    def test_filter_process(self, list_of_ast_class_nodes):
        weight_ssm = 0.7
        weight_cdm = 0.3
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = random.random()
        ccctf = CrisCOMConstantThresholdFilter(min_coupling)
        for python_file, node, class_nodes in list_of_ast_class_nodes:
            for class_node in class_nodes:
                wrapper = AstClassWrapper(class_node)
                matrix = cmmm.build_method_matrix(wrapper)
                original = deepcopy(matrix.matrix)
                filtered_matrix = ccctf.filter_process(matrix)
                assert filtered_matrix != None
                assert not self.has_value_less_than(filtered_matrix.matrix,
                    min_coupling)


class TestCrisCOMVariableThresholdFilter:

    def has_value_less_than(self, matrix, value):
        if value < 0:
            return False
        for row in matrix:
            if len(filter(lambda x: x <= value and x > 0, row)) > 0:
                return True
        return False

    @pytest.mark.skipif(MAX_NO_OF_FILES >= 50, reason='Takes too long.')
    def test_filter_process(self, list_of_ast_class_nodes):
        weight_ssm = 0.7
        weight_cdm = 0.3
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        ccctf = CrisCOMVariableThresholdFilter()
        for python_file, node, class_nodes in list_of_ast_class_nodes:
            for class_node in class_nodes:
                ast_dump = astpp.dump(class_node)
                wrapper = AstClassWrapper(class_node)
                matrix = cmmm.build_method_matrix(wrapper)
                original = deepcopy(matrix.matrix)
                min_coupling = -1
                if len(original) > 0:
                    min_coupling = CrisCOMVariableThresholdFilter.\
                        calculate_median(original)
                filtered_matrix = ccctf.filter_process(matrix)
                assert filtered_matrix != None
                assert not self.has_value_less_than(filtered_matrix.matrix,
                    min_coupling)

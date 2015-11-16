import pytest
import os
import ast
import logging
import astpp
from class_generator import print_matrix, print_matrix_with_fabulousness, \
    l_to_s, print_chains

from conftest import *
from copy import deepcopy
from cristina_filters import *
from AstClassWrapper import *
from StructuralSimilarityBetweenMethods import *
from CallBasedDependenceBetweenMethods import *
from AstToCodeTransformer import *


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

class TestMetrics:
    def build_test_matrix(self, metric, wrapper):
        m_nodes = wrapper.get_method_nodes()
        matrix = []
        for row in range(len(m_nodes)):
            matrix.append([])
            for col in range(len(m_nodes)):
                if row == col:
                    matrix[row].append(1.0)
                elif row < col:
                    result = metric.calculate(m_nodes[row], m_nodes[col],
                        wrapper)
                    result2 = metric.calculate(m_nodes[col], m_nodes[row],
                        wrapper)
                    matrix[row].append(max(result, result2))
                    # matrix[row].append(result)
                else:
                    matrix[row].append(matrix[col][row])
        return matrix

    @pytest.mark.skipif(True, reason='Too many logs')
    def test_ssm_metric(self, cls_gen):
        metric = StructuralSimilarityBetweenMethods()
        for simple_cls in cls_gen.generate(1000, 10, 10):
            cls_source = simple_cls.get_source_code()
            logging.info("TestMetrics::" + \
                "test_ssm_metric:simple_cls.source_code:\n" + \
                cls_source)
            ast_wrapper = AstClassWrapper(simple_cls.get_ast_node())
            custom_ssm = simple_cls.get_ssm_matrix()
            matrix_to_test = self.build_test_matrix(metric, ast_wrapper)
            logging.info("TestMetrics::" + \
                "test_ssm_metric:custom_ssm:\n" + \
                print_matrix_with_fabulousness(custom_ssm))
            logging.info("TestMetrics::" + \
                "test_ssm_metric:matrix_to_test:\n" + \
                print_matrix_with_fabulousness(matrix_to_test))
            for method_node in ast_wrapper.get_method_nodes():
                logging.info(metric.find_instance_variables(method_node,
                    ast_wrapper))
            assert custom_ssm == matrix_to_test

    @pytest.mark.skipif(True, reason='Too many logs.')
    def test_cdm_metric(self, cls_gen):
        metric = CallBasedDependenceBetweenMethods()
        for simple_cls in cls_gen.generate(1000, 10, 10):
            cls_source = simple_cls.get_source_code()
            logging.info("TestMetrics::" + \
                "test_cdm_metric:simple_cls.source_code:\n" + \
                cls_source)
            ast_wrapper = AstClassWrapper(simple_cls.get_ast_node())
            custom_cdm = simple_cls.get_cdm_matrix()
            matrix_to_test = self.build_test_matrix(metric, ast_wrapper)
            logging.info("TestMetrics::" + \
                "test_cdm_metric:custom_cdm:\n" + \
                print_matrix_with_fabulousness(custom_cdm))
            logging.info("TestMetrics::" + \
                "test_cdm_metric:matrix_to_test:\n" + \
                print_matrix_with_fabulousness(matrix_to_test))
            # for method_node in ast_wrapper.get_method_nodes():
            #     logging.info(metric.find_instance_variables(method_node,
            #         ast_wrapper))
            assert custom_cdm == matrix_to_test



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

    @pytest.mark.skipif(True, reason='Too many logs.')
    def test_build_method_matrix_clsgen(self, cls_gen):
        weight_ssm = 0.5
        weight_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        for simple_cls in cls_gen.generate(100, 10, 10):
            cls_source = simple_cls.get_source_code()
            logging.info("TestCrisMethodByMethodMatrix::" + \
                "test_build_method_matrix:simple_cls.source_code:\n" + \
                cls_source)
            custom_matrix = simple_cls.get_matrix(weight_ssm, weight_cdm)
            ast_wrapper = AstClassWrapper(simple_cls.get_ast_node())
            method_matrix = cmmm.build_method_matrix(ast_wrapper)
            logging.info("\ncustom_matrix:\n" + str(
                print_matrix(custom_matrix)))
            matrix = method_matrix.get_matrix()
            logging.info("\nmatrix_under_test:\n" + str(print_matrix(matrix)))
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


class TestCrisMethodChainAssembler:
    custom_code_fname = "chain_assembler_input.py"

    def get_input_as_module(self):
        import imp
        custom_dir = os.path.join(TEST_DATA_DIR, 'custom_data')
        fname = os.path.join(custom_dir, self.custom_code_fname)
        mod = imp.load_source("chain_assembler_input", fname)
        return mod

    @pytest.mark.skipif(True, reason="New test implementation available")
    def test_filter_process(self, custom_python_code):
        ast_node = ast.parse(custom_python_code)
        class_finder = ClassFinder()
        class_finder.visit(ast_node)
        weight_ssm = 0.5
        weight_cdm = 0.5
        min_coupling = 0.4
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        class_nodes = class_finder.class_nodes_dict
        mod = self.get_input_as_module()
        matrix_factory = mod.get_method_matrix
        chain_factory = mod.get_method_chains
        #method_matrices = self.get_method_matrices()
        cmca = CrisMethodChainsAssembler()
        for class_name in class_nodes.keys():
            custom_matrix = matrix_factory(class_name, weight_ssm, weight_cdm)
            class_node = class_nodes[class_name]
            ast_wrapper = AstClassWrapper(class_node)
            method_matrix = cmmm.build_method_matrix(ast_wrapper)
            ccomct = CrisCOMConstantThresholdFilter(min_coupling)
            filtered_matrix = ccomct.filter_process(method_matrix)
            method_chains = cmca.filter_process(filtered_matrix)
            method_names = [[node.name for node in mc.method_ast_nodes]
                for mc in method_chains]
            custom_chains = chain_factory(class_name)
            assert len(method_names) == len(custom_chains)
            assert method_names in custom_chains

    def compare_chains(self, chain1, chain2):
        for chain in chain1:
            if len([x for x in chain2 if set(chain) == set(x)]) == 0:
                return False
        return True

    def test_filter_process_with_cls_gen(self, cls_gen):
        weight_ssm = 0.5
        weight_cdm = 0.5
        min_coupling = 0.4
        metrics = [(StructuralSimilarityBetweenMethods(), weight_ssm),
            (CallBasedDependenceBetweenMethods(), weight_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        cmca = CrisMethodChainsAssembler()
        ccomct = CrisCOMConstantThresholdFilter(min_coupling)
        for simple_cls in cls_gen.generate(100, 10, 10):
            cls_source = simple_cls.get_source_code()
            # logging.info("TestCrisMethodChainAssembler::" + \
            #     "test_filter_process_with_cls_gen:simple_cls.source_code:\n" + \
            #     cls_source)
            class_node = simple_cls.get_ast_node()
            class_wrapper = AstClassWrapper(class_node)
            method_matrix = cmmm.build_method_matrix(class_wrapper)
            method_matrix_matrix = method_matrix.get_matrix()
            custom_matrix = simple_cls.get_matrix(weight_ssm, weight_cdm)
            filtered_matrix = ccomct.filter_process(method_matrix)
            filtered_matrix_matrix = filtered_matrix.get_matrix()
            method_chains = cmca.filter_process(filtered_matrix)
            custom_filtered_matrix = simple_cls.filter_matrix(weight_ssm,
                weight_cdm, min_coupling)
            method_names = [[node.name for node in mc.method_ast_nodes]
                for mc in method_chains]
            custom_chains = simple_cls.get_method_chains(weight_ssm,
                weight_cdm, min_coupling)
            assert method_matrix_matrix != None
            assert method_matrix_matrix == custom_matrix
            assert custom_filtered_matrix == filtered_matrix_matrix
            # logging.info("filtered_matrix:\n" + print_matrix(
            #     custom_filtered_matrix))
            # logging.info("custom_chains:\n" + str(custom_chains))
            # logging.info("method_names:\n" + str(method_names))
            assert len(method_names) == len(custom_chains)
            assert self.compare_chains(method_names, custom_chains)


class TestCrisTrivialChainMerger:
    def log(self, title, txt):
        logging.info("TestCrisTrivialChainMerger::" + title + ":\n" + txt)

    def compare_chains(self, chain1, chain2):
        for chain in chain1:
            if len([x for x in chain2 if set(chain) == set(x)]) == 0:
                return False
        return True

    @pytest.mark.skipif(True, reason='It may fail sometimes, but the merging is right.')
    def test_filter_process(self, cls_gen):
        w_ssm = 0.5
        w_cdm = 0.5
        min_coupling = 0.4
        min_length = 2
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        cmmm = CrisMethodByMethodMatrix(metrics)
        cmca = CrisMethodChainsAssembler()
        ccomct = CrisCOMConstantThresholdFilter(min_coupling)
        ctcm = CrisTrivialChainMerger(metrics, min_length)
        for simple_cls in cls_gen.generate(1000, 10, 10):
            cls_source = simple_cls.get_source_code()
            self.log("simple_cls source", cls_source)
            class_node = simple_cls.get_ast_node()
            class_wrapper = AstClassWrapper(class_node)
            method_matrix = cmmm.build_method_matrix(class_wrapper)
            method_matrix_matrix = method_matrix.get_matrix()
            custom_matrix = simple_cls.get_matrix(w_ssm, w_cdm)
            filtered_matrix = ccomct.filter_process(method_matrix)
            filtered_matrix_matrix = filtered_matrix.get_matrix()
            method_chains = cmca.filter_process(filtered_matrix)
            custom_filtered_matrix = simple_cls.filter_matrix(w_ssm,
                w_cdm, min_coupling)
            self.log("filtered matrix",
                print_matrix(custom_filtered_matrix))
            assert custom_filtered_matrix == filtered_matrix_matrix
            # method_names = [[node.name for node in mc.method_ast_nodes]
            #     for mc in method_chains]
            custom_chains = simple_cls.get_method_chains(w_ssm,
                w_cdm, min_coupling)
            custom_merged_chains = simple_cls.merge_trivial_chains(
                    l_to_s(custom_chains),
                    min_length,
                    w_ssm,
                    w_cdm
                )
            merged_chains = ctcm.filter_process(method_chains)
            method_names = [x.get_method_names() for x in merged_chains]
            self.log("custom merged chains",
                print_chains(custom_merged_chains))
            self.log("pipeline merged chains",
                print_chains(method_names))
            assert len(custom_merged_chains) == len(method_names)
            assert self.compare_chains(custom_merged_chains, method_names)


class TestCrisClassAssembler:
    def log(self, title, txt):
        logging.info("TestCrisClassAssembler::" + title + ":\n" + txt + "\n\n")

    def setup_pipeline(self):
        self.w_ssm = 0.5
        self.w_cdm = 0.5
        self.min_coupling = 0.4
        self.min_length = 2
        metrics = [(StructuralSimilarityBetweenMethods(), self.w_ssm),
            (CallBasedDependenceBetweenMethods(), self.w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        self.cmca = CrisMethodChainsAssembler()
        self.ccomct = CrisCOMConstantThresholdFilter(self.min_coupling)
        self.ctcm = CrisTrivialChainMerger(metrics, self.min_length)
        self.cca = CrisClassAssembler()

    def assemble_classes(self, simple_cls):
        method_chains = simple_cls.get_method_chains(
            self.w_ssm,
            self.w_cdm,
            self.min_coupling
        )
        merged_chains = simple_cls.merge_trivial_chains(
            l_to_s(method_chains),
            self.min_length,
            self.w_ssm,
            self.w_cdm
        )
        return simple_cls.assemble_classes(merged_chains)

    def pipeline_assembled_classes(self, class_node):
        class_wrapper = AstClassWrapper(class_node)
        method_matrix = self.cmmm.build_method_matrix(class_wrapper)
        filtered_matrix = self.ccomct.filter_process(method_matrix)
        method_chains = self.cmca.filter_process(filtered_matrix)
        self.merged_chains = self.ctcm.filter_process(method_chains)
        return self.cca.filter_process(self.merged_chains)

    @pytest.mark.skipif(True, reason='Again, only the algorithms differ.')
    def test_filter_process(self, cls_gen):
        self.setup_pipeline()
        for simple_cls in cls_gen.generate(100, 2, 2):
            cstm_assmbld_cls = self.assemble_classes(simple_cls)
            assmbld_cls = self.pipeline_assembled_classes(
                simple_cls.get_ast_node())
            assert len(cstm_assmbld_cls) == len(assmbld_cls)
            assert len(self.merged_chains) == len(assmbld_cls)
            # self.log('Assembled Classes', "=" * 100)
            # self.log("Custom Classes", '')
            # for cls1 in cstm_assmbld_cls:
            #     self.log('cls1', astpp.dump(cls1))
            # self.log("Pipeline Classes", '')
            # for cls2 in assmbld_cls:
            #     self.log('cls2', astpp.dump(cls2.get_class_node()))
            # for cls1, cls2 in zip(cstm_assmbld_cls, assmbld_cls):
            #     self.log('cls1', astpp.dump(cls1))
            #     self.log('cls2', astpp.dump(cls2.get_class_node()))
            #     assert ast.dump(cls1) == ast.dump(cls2.get_class_node())


class TestCrisAstToCodeTransformer:
    def log(self, title, txt):
        logging.info("TestCrisAstToCodeTransformer::" +
            title + ":\n" + txt + "\n\n")

    def setup_transformer(self):
        self.transformer = AstToCodeTransformer()

    def test_filter_process(self, cls_gen):
        self.setup_transformer()
        for simple_cls in cls_gen.generate(1000, 10, 10):
            original_source = simple_cls.get_source_code()
            ast_node = simple_cls.get_ast_node()
            source_code = self.transformer.transform(ast_node)
            new_ast_node = ast.parse(source_code).body[0]
            self.log("Original Source", original_source)
            self.log("New Source", source_code)
            self.log("Original Dump", astpp.dump(ast_node))
            self.log("New Source", astpp.dump(new_ast_node))
            assert ast.dump(ast_node) == ast.dump(new_ast_node)

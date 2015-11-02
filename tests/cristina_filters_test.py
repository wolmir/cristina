import pytest
import tempfile
import string
import random
import os
import ast

from cristina_filters import *
from AstClassWrapper import *

TEST_DATA_DIR = 'tests/test_data'

@pytest.fixture
def create_file():
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    file_size = random.randint(100, 1000)
    stuff_to_write = ''.join([random.choice(string.printable)
        for i in range(file_size)])
    tmp_file.write(stuff_to_write)
    tmp_file.close()
    return tmp_file


@pytest.fixture(scope="module")
def list_of_python_files():
    python_files = ''
    with open(os.path.join(TEST_DATA_DIR, 'python_files'), 'r') as ls_file:
        python_files = ls_file.read()
    return python_files.split('\n')[:-1]


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

    def test_constructor(self):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        assert cdsd != None

    def test_load_files(self, list_of_python_files):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        file_paths = cdsd.load_files(TEST_DATA_DIR)
        assert file_paths != None
        assert len(file_paths) > 0
        for python_file in list_of_python_files:
            assert os.path.join(TEST_DATA_DIR, python_file) in file_paths

    def test_post_constructor(self):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        assert cdsd.file_paths != None
        assert len(cdsd.file_paths) > 0

    def test_next(self, list_of_python_files):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        for python_file in list_of_python_files:
            next_file = cdsd.next()
            assert next_file != None
        with pytest.raises(IndexError):
            cdsd.next()

    def test_has_next(self, list_of_python_files):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        assert cdsd.has_next()
        for python_file in list_of_python_files:
            cdsd.next()
        assert not cdsd.has_next()


class TestCrisCodeToAstTransformer:
    def test_code_to_ast(self, list_of_python_files):
        cctat = CrisCodeToAstTransformer()
        for python_file in list_of_python_files:
            with open(os.path.join(TEST_DATA_DIR, python_file), 'r')\
              as source_file:
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


class ClassFinder(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.class_nodes = []
        self.class_nodes_dict = {}

    def visit_ClassDef(self, node):
        self.class_nodes.append(node)
        self.class_nodes_dict[node.name] = node
        self.generic_visit(node)

@pytest.fixture(scope="module")
def list_of_ast_module_nodes(list_of_python_files):
    ast_module_nodes = []
    for python_file in list_of_python_files:
        with open(os.path.join(TEST_DATA_DIR, python_file), 'r') as source:
            try:
                ast_module_nodes.append((python_file, ast.parse(source.read())))
            except SyntaxError:
                continue
    return ast_module_nodes


@pytest.fixture(scope="module")
def list_of_ast_class_nodes(list_of_ast_module_nodes):
    ast_class_nodes = []
    for python_file, node in list_of_ast_module_nodes:
        class_finder = ClassFinder()
        class_finder.visit(node)
        ast_class_nodes.append((python_file, node, class_finder.class_nodes))
    return ast_class_nodes


class TestCrisClassNodeFinder:
    def test_find_class_nodes(self, list_of_python_files):
        for python_file in list_of_python_files:
            source_code = ""
            with open(os.path.join(TEST_DATA_DIR, python_file), 'r') as source:
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


@pytest.fixture
def custom_python_code(request):
    custom_dir = os.path.join(TEST_DATA_DIR, 'custom_data')
    fname = getattr(request.cls, "custom_code_fname",
        "python_file_for_input.py")
    fname = os.path.join(custom_dir, fname)
    custom_code = ''
    with open(fname, 'r') as src:
        custom_code = src.read()
    return custom_code


class TestAstClassWrapper:
    def test_constructor(self, list_of_ast_class_nodes):
        for python_file, node, class_nodes in list_of_ast_class_nodes:
            for class_node in class_nodes:
                class_wrapper = AstClassWrapper(class_node)
                assert class_wrapper != None
                assert len(class_wrapper.method_nodes) == \
                    len(class_wrapper.method_names)

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

    # def test_get_method_names(self, list_of_ast_class_nodes):
    #     for class_node in list_of_ast_class_nodes:
    #         class_wrapper = AstClassWrapper(class_node)
    #         assert class_wrapper.get_method_names() != None

import pytest
import tempfile
import string
import random
import shutil
import ast
import os

TEST_DATA_DIR = 'tests/test_data'
TEST_TMP_DIR = ''
MAX_NO_OF_FILES = 300

class ClassFinder(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.class_nodes = []
        self.class_nodes_dict = {}

    def visit_ClassDef(self, node):
        self.class_nodes.append(node)
        self.class_nodes_dict[node.name] = node
        self.generic_visit(node)

@pytest.fixture
def create_file():
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    file_size = random.randint(100, 1000)
    stuff_to_write = ''.join([random.choice(string.printable)
        for i in range(file_size)])
    tmp_file.write(stuff_to_write)
    tmp_file.close()
    return tmp_file

#This works, but the number of files
#makes the tests slow.
# @pytest.fixture(scope="module")
# def list_of_python_files():
#     python_files = ''
#     with open(os.path.join(TEST_DATA_DIR, 'python_files'), 'r') as ls_file:
#         python_files = ls_file.read()
#     return python_files.split('\n')[:-1]

#This should ammend the problem.
@pytest.fixture
def list_of_python_files(request, tmpdir):
    def clean_up():
        print "Deleting temporary files."
        shutil.rmtree(str(tmpdir))
    request.addfinalizer(clean_up)
    TEST_TMP_DIR = str(tmpdir)
    python_files = ''
    with open(os.path.join(TEST_DATA_DIR, 'python_files'), 'r') as ls_file:
        python_files = ls_file.read().split('\n')[:-1]
    python_files = random.sample(python_files, MAX_NO_OF_FILES)
    for python_file in python_files:
        shutil.copy(os.path.join(TEST_DATA_DIR, python_file), TEST_TMP_DIR)
    python_files = [os.path.join(TEST_TMP_DIR, src) for src in python_files]
    return python_files


@pytest.fixture
def list_of_ast_module_nodes(list_of_python_files):
    ast_module_nodes = []
    for python_file in list_of_python_files:
        with open(python_file, 'r') as source:
            try:
                ast_module_nodes.append((python_file, ast.parse(source.read())))
            except SyntaxError:
                continue
    return ast_module_nodes


@pytest.fixture
def list_of_ast_class_nodes(list_of_ast_module_nodes):
    ast_class_nodes = []
    for python_file, node in list_of_ast_module_nodes:
        class_finder = ClassFinder()
        class_finder.visit(node)
        ast_class_nodes.append((python_file, node, class_finder.class_nodes))
    return ast_class_nodes


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



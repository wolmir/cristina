import pytest
import tempfile
import string
import random

from cristina_filters import CrisDataSourceSingleFile,\
    CrisDataSourceDirectory
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

class TestCrisDataSourceSingleFile:
    def test_next(self, create_file):
        file_data = ''
        with open(create_file.name, 'r') as tmp_file:
            file_data = tmp_file.read()
        cdssf = CrisDataSourceSingleFile(create_file.name)
        assert cdssf.next() == file_data

    def test_has_next(self, create_file):
        cdssf = CrisDataSourceSingleFile(create_file.name)
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
    
    def test_load_files(self):
        cdsd = CrisDataSourceDirectory(TEST_DATA_DIR)
        file_paths = cdsd.load_files(TEST_DATA_DIR)
        assert file_paths != None
        assert len(file_paths) > 0

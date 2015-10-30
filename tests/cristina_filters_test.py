import pytest
import tempfile
import string
import random

from cristina_filters import CrisDataSourceSingleFile


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
    pass

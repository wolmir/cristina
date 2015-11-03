import pytest
import os

from cristina_filters import *
from pypeline import *


class AssertionsSink(DataSink):
    def __init__(self):
        DataSink.__init__(self)

    def handle_output(self, output):
        assert output != None

class TestPypeline1:
    def test_cris_source_and_ast_gen(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        cctat = CrisCodeToAstTransformer()
        pipeline = pypeline.Pipeline()
        assert pipeline != None
        pipeline.set_data_source(cdsd)
        pipeline.connect(cctat)
        pipeline.set_data_sink(AssertionsSink())
        pipeline.run()

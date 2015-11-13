import pytest
import os
import pdb

from Queue import Queue, Empty
from cristina_filters import *
from pypeline import *
from conftest import *


class AssertionsSink(DataSink):
    def __init__(self):
        DataSink.__init__(self)
        self.queue = Queue()

    def handle_output(self, output):
        self.queue.put_nowait(output)

    def close_sink(self):
        pass

    def make_assertions(self):
        assert not self.queue.empty()
        try:
            while True:
                assert self.queue.get_nowait() != None
        except Empty:
            pass


# class SimpleClsSource(DataSource):
#     def __init__(self, simple_cls_vec):
#         DataSource.__init__(self)
#         self.cls_source = simple_cls_vec

#     def has_next(self):
#         return len(self.cls_source) > 0

#     def next(self):
#         return self.cls_source.pop()


# class Test2AssertionSink(DataSink):
#     def __init__(self):
#         pass


class TestPypeline1:
    def test_cris_source_and_ast_gen(self, list_of_python_files):
        tmp_dir = os.path.dirname(list_of_python_files[0])
        cdsd = CrisDataSourceDirectory(tmp_dir)
        cctat = CrisCodeToAstTransformer()
        assertion_sink = AssertionsSink()
        pipeline = pypeline.Pipeline()
        assert pipeline != None
        pipeline.set_data_source(cdsd)
        pipeline.connect(cctat)
        assert cctat.in_pipe != None
        assert cdsd.out_pipe != None
        assert cctat.in_pipe == cdsd.out_pipe
        assert cctat.in_pipe.is_open()
        pipeline.set_data_sink(assertion_sink)
        assert cctat.out_pipe != None
        assert assertion_sink.in_pipe != None
        assert cctat.out_pipe == assertion_sink.in_pipe
        assert assertion_sink.in_pipe.is_open()
        pipeline.run()
        assertion_sink.make_assertions()


# class TestPypeline2:
#     def test_until_chain_merging(self, cls_gen):
#         pass

import pytest
import os
import pdb

from Queue import Queue, Empty
from cristina_filters import *
from pypeline import *
from conftest import *
from StructuralSimilarityBetweenMethods import *
from CallBasedDependenceBetweenMethods import *


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


class TestPypeline2:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline2(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline3:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline3(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline4:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline4(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline5:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.connect(self.ccomf)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline5(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline6:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.cmca = CrisMethodChainsAssembler()
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.connect(self.ccomf)
        self.pipeline.connect(self.cmca)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline6(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline7:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.cmca = CrisMethodChainsAssembler()
        min_length = 2
        self.ctcm = CrisTrivialChainMerger(metrics, min_length)
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.connect(self.ccomf)
        self.pipeline.connect(self.cmca)
        self.pipeline.connect(self.ctcm)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline7(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline8:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.cmca = CrisMethodChainsAssembler()
        min_length = 2
        self.ctcm = CrisTrivialChainMerger(metrics, min_length)
        self.cca = CrisClassAssembler()
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.connect(self.ccomf)
        self.pipeline.connect(self.cmca)
        self.pipeline.connect(self.ctcm)
        self.pipeline.connect(self.cca)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline8(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline9:
    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.cmca = CrisMethodChainsAssembler()
        min_length = 2
        self.ctcm = CrisTrivialChainMerger(metrics, min_length)
        self.cca = CrisClassAssembler()
        self.catct = CrisAstToCodeTransformer()
        self.assertion_sink = AssertionsSink()
        self.pipeline = pypeline.Pipeline()
        self.pipeline.set_data_source(self.cdsd)
        self.pipeline.connect(self.cctat)
        self.pipeline.connect(self.ccnf)
        self.pipeline.connect(self.cacw)
        self.pipeline.connect(self.cmmm)
        self.pipeline.connect(self.ccomf)
        self.pipeline.connect(self.cmca)
        self.pipeline.connect(self.ctcm)
        self.pipeline.connect(self.cca)
        self.pipeline.connect(self.catct)
        self.pipeline.set_data_sink(self.assertion_sink)

    def test_pipeline9(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        self.pipeline.run()
        self.assertion_sink.make_assertions()


class TestPypeline10:
    def log(self, title, txt):
        logging.info("TestPypeline10::" +
            title + ":\n" + txt + "\n\n")

    def set_up_pipeline(self, dir_path):
        self.cdsd = CrisDataSourceDirectory(dir_path)
        self.cctat = CrisCodeToAstTransformer()
        self.ccnf = CrisClassNodeFinder()
        self.cacw = CrisAstClassWrapper()
        w_ssm = 0.5
        w_cdm = 0.5
        metrics = [(StructuralSimilarityBetweenMethods(), w_ssm),
            (CallBasedDependenceBetweenMethods(), w_cdm)]
        self.cmmm = CrisMethodByMethodMatrix(metrics)
        min_coupling = 0.2
        self.ccomf = CrisChainsOfMethodsFilterFactory.create(min_coupling)
        self.cmca = CrisMethodChainsAssembler()
        min_length = 2
        self.ctcm = CrisTrivialChainMerger(metrics, min_length)
        self.cca = CrisClassAssembler()
        self.catct = CrisAstToCodeTransformer()
        self.assertion_sink = AssertionsSink()

    def test_pipeline10(self, list_of_python_files):
        self.set_up_pipeline(os.path.dirname(list_of_python_files[0]))
        while self.cdsd.has_next():
            p0 = self.cdsd.next()
            p1 = self.cctat.filter_process(p0)
            if p1 == None:
                continue
            p2 = self.ccnf.filter_process(p1)
            p3 = self.cacw.filter_process(p2)
            p4 = self.cmmm.filter_process(p3)
            p5 = self.ccomf.filter_process(p4)
            p6 = self.cmca.filter_process(p5)
            p7 = self.ctcm.filter_process(p6)
            p8 = self.cca.filter_process(p7)
            p9 = self.catct.filter_process(p8)
            self.assertion_sink.handle_output(p9)
        self.assertion_sink.make_assertions()

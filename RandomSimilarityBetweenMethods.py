import random

from Metric import Metric


class RandomSimilarityBetweenMethods(Metric):
    def calculate(self, method_node1, method_node2, class_wrapper):
        return random.random()

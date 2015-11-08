class MethodChainFilter:
	def __init__(self, min_coupling):
		self.min_coupling = min_coupling

	def filter_matrix(self, method_matrix):
		return [map(lambda x: max(x - self.min_coupling, 0) and x, row)
			for row in method_matrix.get_matrix()]

	def set_min_coupling(self, min_coupling):
		self.min_coupling = min_coupling

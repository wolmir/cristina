class TrivialChainMerger(object):
    def __init__(self, min_length, metrics, weights):
        self.min_length = min_length
        self.metrics = metrics
        self.weights = weights

    def merge_chains(self, method_chains):
        merged_chains = []
        trivial_chains = self.identify_trivial_chains(method_chains)
        for trivial_chain in trivial_chains:
            most_coupled = self.get_most_coupled(trivial_chain, method_chains)
            most_coupled.merge(trivial_chain)
            merged_chains.append(most_coupled)
        return merged_chains

    def identify_trivial_chains(self, method_chains):
        return [chain for chain in method_chains 
            if chain.get_length() <= self.min_length]

    def get_most_coupled(self, trivial_chain, method_chains):
        most_coupled = method_chains[0]
        biggest_coupling_value = 0
        for chain in method_chains:
            if chain.get_coupling(trivial_chain, 
              self.metrics, 
              self.weights) > biggest_coupling_value:
                most_coupled = chain
        return most_coupled
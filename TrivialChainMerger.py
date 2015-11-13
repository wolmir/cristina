import pdb
class TrivialChainMerger(object):
    def __init__(self, min_length, metrics, weights):
        self.min_length = min_length
        self.metrics = metrics
        self.weights = weights

    def merge_chains(self, method_chains):
        trivial_chains = self.identify_trivial_chains(method_chains)
        non_trivial_chains = self.get_non_trivial_chains(method_chains)
        if len(trivial_chains) == 0:
            return method_chains
        if len(non_trivial_chains) == 0:
            return method_chains
        for trivial_chain in trivial_chains:
            most_coupled = self.get_most_coupled(trivial_chain,
                non_trivial_chains)
            most_coupled.merge(trivial_chain)
        return non_trivial_chains

    def identify_trivial_chains(self, method_chains):
        return [chain for chain in method_chains
            if chain.get_length() < self.min_length]

    def get_non_trivial_chains(self, method_chains):
        return [chain for chain in method_chains
            if chain.get_length() >= self.min_length]

    def get_most_coupled(self, trivial_chain, method_chains):
        most_coupled = method_chains[0]
        max_coupling = 0
        for chain in method_chains:
            coupling = chain.get_coupling(trivial_chain,
                self.metrics,
                self.weights)
            if coupling >= max_coupling:
                most_coupled = chain
                max_coupling = coupling
        return most_coupled

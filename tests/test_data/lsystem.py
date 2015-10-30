#-------------------------------------------------------------------------------
#
#   Mutagenesis - L-Systems
#
#-------------------------------------------------------------------------------

from random import choice

parameter_symbols = "123456789"
command_symbols = "lrwcdob"
terminal_symbols = command_symbols + parameter_symbols
nonterminal_symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#-------------------------------------------------------------------------------

def substitute_substring(string, i, productions, result):
	n = len(string)
	while i < n:
		sym = string[i]
		rhs_list = productions.get(sym)
		if rhs_list:
			repl = choice(rhs_list)
			if repl[-1:] == "]":  # Prevent spurious merging of branch sequences
				repl += "."
		else:
			repl = sym
		#print sym, "-->", repl ###
		result.append(repl)
		i += 1

#-------------------------------------------------------------------------------

class LSystem(object):

	def __init__(self):
		self.productions = {}
	
	def dump(self):
		productions = self.productions
		nonterminals = productions.keys()
		nonterminals.sort()
		for lhs in nonterminals:
			for rhs in productions[lhs]:
				print lhs, "->", rhs
			print
	
	def add_production(self, lhs, rhs):
		productions = self.productions
		rhs_list = productions.get(lhs)
		if rhs_list is None:
			rhs_list = []
			productions[lhs] = rhs_list
		rhs_list.append(rhs)

	def substitute_string(self, string):
		#print "substitute_string:", string ###
		result = []
		substitute_substring(string, 0, self.productions, result)
		result = "".join(result)
		#print "=>", result ###
		return result

#-------------------------------------------------------------------------------
#
#   Mutagenesis - Mutation
#
#-------------------------------------------------------------------------------

from __future__ import division
from random import random, randrange, choice, seed, shuffle
from lsystem import command_symbols, parameter_symbols, terminal_symbols, \
	nonterminal_symbols

def shuffled(items):
	result = list(items)
	shuffle(result)
	return result

def chance(p):
	return random() < p

def set_choice(s):
	return choice(list(s))

def another_choice(s, exclude):
	return choice(s.replace(exclude, ""))

def another_set_choice(s, exclude):
	avail = s - set([exclude])
	return set_choice(avail)

def is_filled_poly(s):
	return "}" in s

def is_nonterminal(sym):
	return sym in nonterminal_symbols

def nonterminal_symbol_set(chromosomes):
	nt = set()
	for c in chromosomes:
		nt.add(c.lhs)
		for sym in c.rhs:
			if sym in nonterminal_symbols:
				nt.add(sym)
	return nt

def random_nonterminal(nt):
	return set_choice(nt)

def random_symbol(nt):
	if chance(0.5):
		if chance(1 / (len(command_symbols) + 1)):
			return choice(parameter_symbols)
		else:
			return choice(command_symbols)
	else:
		return set_choice(nt)

def another_nonterminal(nt, sym):
	return another_set_choice(nt, sym)

def another_terminal(sym):
	return another_set_choice(set(command_symbols), sym)

def another_symbol(nt, sym):
	return another_set_choice(nt | set(command_symbols), sym)

def end_of_branch(s, i):
	i += 1
	n = len(s)
	k = 1
	while k > 0 and i < n:
		sym = s[i]
		if sym == "[":
			k += 1
		elif sym == "]":
			k -= 1
		i += 1
	return i

def insert(s, i, sym):
	print "Inserting %r at %s" % (sym, i)
	return s[:i] + sym + s[i:]

def replace(s, i, sym):
	print "Replacing %r with %r at %s" % (s[i:i+1], sym, i)
	return s[:i] + sym + s[i+1:]

def delete_range(s, i, j):
	print "Deleting %r at %s" % (s[i:j], i)
	return s[:i] + s[j:]

def delete(s, i):
	return delete_range(s, i, i+1)

def mutate_terminal(nt, s, i):
	if chance(0.75):
		sym = another_terminal(s[i])
		if chance(0.75):
			return insert(s, i, sym)
		else:
			return replace(s, i, sym)
	else:
		return delete(s, i)

def mutate_filled_poly(nt, s):
	i = randrange(1, len(s) - 1)
	return mutate_terminal(nt, s, i)

def mutate_nonterminal(nt, s, i):
	if chance(0.75):
		if chance(0.75):
			sym = another_nonterminal(nt, s[i])
		else:
			sym = another_symbol(nt, s[i])
		return replace(s, i, sym)
	else:
		return delete(s, i)

def mutate_beginning_of_branch(nt, s, i):
	j = end_of_branch(s, i)
	if chance(0.75):
		branch = s[i:j]
		return insert(s, i, branch)
	else:
		return delete_range(s, i, j)

def new_branch(s):
	return "[" + s + "]"

def mutate_end_of_branch(nt, s, i):
	if i > 0 and is_nonterminal(s[i-1]):
		return mutate_nonterminal(nt, s, i-1)
	else:
		if chance(0.5):
			sym = new_branch(random_nonterminal(nt))
		else:
			sym = random_symbol(nt)
		return insert(s, i, sym)

def mutate_symbol(nt, s, i):
	sym = s[i]
	if is_nonterminal(sym):
		if chance(0.25):
			return mutate_nonterminal(nt, s, i)
	else:
		return mutate_terminal(nt, s, i)

def mutate_parameter(s, i):
	sym = s[i]
	return replace(s, i, another_choice(parameter_symbols, sym))

def mutate_string(nt, s):
	#i = randrange(len(s) + 1)
	for i in shuffled(range(len(s) + 1)):
		sym = s[i:i+1]
		if "0" <= sym <= "9" and chance(0.9):
			result = mutate_parameter(s, i)
			break
		if sym == "[":
			result = mutate_beginning_of_branch(nt, s, i)
		elif sym == "" or sym == "]":
			result = mutate_end_of_branch(nt, s, i)
		else:
			result = mutate_symbol(nt, s, i)
		if result is not None:
			return result
	# Shouldn't get here, but just in case...
	print "mutate_string: couldn't find a mutation for %r" % s
	return s

def mutate_rhs(nt, rhs):
	if is_filled_poly(rhs):
		return mutate_filled_poly(nt, rhs)
	else:
		return mutate_string(nt, rhs)

def mutate_chromosome(nt, chromosome):
	print "Mutating chromosome:", chromosome
	if chance(0.25 / (len(chromosome.rhs) + 1)):
		sym = another_nonterminal(nt, chromosome.lhs)
		print "Replacing the lhs with", sym
		chromosome.lhs = sym
	else:
		chromosome.rhs = mutate_rhs(nt, chromosome.rhs)

def nonpoly_chromosomes(chromosomes):
	return [c for c in chromosomes if not is_filled_poly(c.rhs)]

def incorporate_nonterminal(new_sym, chromosomes):
	candidates = nonpoly_chromosomes(chromosomes)
	if not candidates:
		print "No non-poly chromosomes to insert %r into" % new_sym
		return
	chromosome = choice(candidates)
	s = chromosome.rhs
	if s == "":
		s = new_sym
	else:
		i = randrange(len(s))
		while 1:
			sym1 = s[i:i+1]
			sym2 = s[i+1:i+2]
			if is_nonterminal(sym1):
				s = replace(s, i, new_sym)
				break
			elif sym2 == "[":
				s = insert(s, i+1, new_branch(new_sym))
				break
			elif sym2 == "]" or sym2 == "":
				s = insert(s, i+1, new_sym)
				break
			i += 1
	chromosome.rhs = s

def add_chromosome(nt, chromosomes):
	old_chromosome = choice(chromosomes)
	print "Duplicating chromosome:", old_chromosome
	new_chromosome = old_chromosome.clone()
	old_sym = new_chromosome.lhs
	new_sym = random_nonterminal(nt)
	print "Replacing lhs with %r" % new_sym
	new_chromosome.lhs = new_sym
	new_chromosome.rhs = new_chromosome.rhs.replace(old_sym, new_sym)
	incorporate_nonterminal(new_sym, chromosomes)
	chromosomes.append(new_chromosome)

def mutate_chromosomes(chromosomes):
	nt = nonterminal_symbol_set(chromosomes)
	print "Nonterminals present are:", nt ###
	if chance(1 / len(chromosomes)):
		add_chromosome(nt, chromosomes)
	else:
		mutate_chromosome(nt, choice(chromosomes))

def mutate_dna(dna):
	mutate_chromosomes(dna.chromosomes)

#-------------------------------------------------------------------------------

def partition_string(s):
	print "Partitioning string %r" % s
	parts = []
	i = 0
	n = len(s)
	while i < n:
		j = s.find("[", i)
		if j < 0:
			j = n
		if i == j:
			j = end_of_branch(s, i)
		parts.append(s[i:j])
		i = j
	print "Result:", parts
	return parts

def append_remaining(result, list1, list2):
	n = min(len(list1), len(list2))
	result.extend(list1[n:])
	result.extend(list2[n:])

def cross_simple_strings(s1, s2):
	if len(s1) < len(s2):
		s2, s1 = s1, s2
	print "Crossing simple string %r with %r" % (s1, s2) ###
	n1 = len(s1)
	n2 = len(s2)
	print "n1 =", n1, "n2 =", n2 ###
	if chance((n1 - 1) / 4):
		k1 = randrange(1, n1)
		print "Splitting s1 at", k1 ###
		k2 = k1 - randrange(0, n1 - n2 + 1)
		print "Splitting s2 at", k2 ###
		a = s1[:k1], s2[:k2]
		b = s1[k1:], s2[k2:]
		i = randrange(2)
		return a[i] + b[1 - i]
	else:
		return choice([s1, s2]) 

def cross_parts(s1, s2):
	b1 = s1.startswith("[")
	b2 = s2.startswith("[")
	if b1 and b2:
		return "[%s]" % cross_strings(s1[1:-1], s2[1:-1])
	elif not b1 and not b2:
		return cross_simple_strings(s1, s2)

def cross_strings(s1, s2):
	print "Crossing strings:" ###
	print s1 ###
	print s2 ###
	parts1 = partition_string(s1)
	parts2 = partition_string(s2)
	parts3 = [cross_parts(*parts) for parts in zip(parts1, parts2)]
	append_remaining(parts3, parts1, parts2)
	try:
		result = "".join(parts3)
	except TypeError:
		#  Last-minute hack to work around a bug
		result = choice([s1, s2])
	print "Result of crossing string %r with %r:" % (s1, s2) ###
	print result ###
	return result

def cross_rhs(rhs1, rhs2):
	f1 = rhs1.startswith("{")
	f2 = rhs2.startswith("{")
	if f1 and f2:
		return "{%s}" % cross_strings(rhs1[1:-1], rhs2[1:-1])
	elif not f1 and not f2:
		return cross_strings(rhs1, rhs2)
	else:
		return choice(rhs1, rhs2)

#-------------------------------------------------------------------------------

#seed(42) ###

import random
import ast
import pdb
import logging

# from colorama import init
from blessings import Terminal
from itertools import product


# init()


def print_matrix(matrix):
    if len(matrix) == 0:
        return '[]'
    fmatrix = [['%.2f' % col for col in row]
        for row in matrix]
    ret_s = '     '.join([' '] + [str(c) for c in range(len(fmatrix[0]))]) +\
     "\n"
    for n, row in enumerate(fmatrix):
        ret_s += '  '.join([str(n)] + row) + "\n"
    return ret_s + '\n'


def print_matrix_with_fabulousness(matrix):
    t = Terminal()
    colors = [t.red, t.green, t.blue]
    if len(matrix) == 0:
        #print t.yellow('[]')
        return t.yellow('[')
    fmatrix = [['%.2f' % col for col in row]
        for row in matrix]
    ret_s = t.bold('     '.join([' '] + [str(c)
        for c in range(len(fmatrix[0]))]) + "\n")
    for n, row in enumerate(fmatrix):
        ret_s += colors[n % 3]('  '.join([str(n)] + row) + "\n")
    return ret_s + '\n'

def print_chains(method_chains):
    txt = "=" * 30 + "\n"
    for chain in method_chains:
        txt += ''.join(['-' + met + '-' for met in chain]) + '\n'
    txt += "=" * 30 + "\n"
    return txt


def rint(n):
    return range(random.randint(0, n))

def rvec(n):
    vec = range(n)
    return [random.choice(vec) for i in range(random.randint(0, n - 1))]


def rsample(v):
    if len(v) == 0:
        return []
    stop = max(len(v) - 1, 1)
    size = random.randint(0, stop)
    if size == 0:
        return []
    return random.sample(v, size)


def var_def_line(n_vars):
    if n_vars == 0:
        return ""
    line = ""
    line_tuple = "("
    for var in range(n_vars):
        line += "var" + str(var) + ", "
        line_tuple += "0, "
    line = line[:-2] + " = " + line_tuple[:-2] + ")"
    return line


def method_body(n_vars, n_mets):
    if n_vars == 0 and n_mets == 0:
        return "pass"
    body = ""
    shuffled_vars = [random.choice(range(n_vars))
        for _ in range(random.randint(0, n_vars - 1))]
    for var in shuffled_vars:
        body += "\t\tvar" + str(var) + " = 0\n"
    shuffled_mets = [random.choice(range(n_mets))
        for _ in range(random.randint(0, n_mets - 1))]
    for met in shuffled_mets:
        body += "\t\tself." + "method" + str(met) + "()\n"
    body += "\t\treturn\n"
    return body


def build_class(n_vars, n_mets):
    code = "class SampleClass:\n"
    code += "\t" + var_def_line(n_vars) + "\n"
    for met in range(n_mets):
        code += "\tdef method" + str(met) + "(self):\n"
        code += method_body(n_vars, n_mets) +"\n"
    return code


def generate_class():
    number_of_vars = random.randint(0, 10)
    number_of_methods = random.randint(0, 10)
    return build_class(number_of_vars, number_of_methods)


def split_chains(chain1, chain2):
    return [x for x in chain1 if not x in chain2]


class SimpleMethod:
    def __init__(self, n, vars, m_calls):
        self.n = n
        self.name = "method" + str(n)
        self.vars = set(vars)
        self.m_calls = m_calls

    def ssm(self, method):
        if len(self.vars | method.vars) == 0:
            return 0
        siv = len(self.vars & method.vars) * 1.0
        suv = len(self.vars | method.vars) * 1.0
        return siv / suv

    def cdm(self, method, methods):
        #pdb.set_trace()
        calls_in = 0
        for m in methods:
            calls_in += len([x for x in m.m_calls if x == method.n])
        if calls_in == 0:
            return 0
        return len([x for x in self.m_calls if x == method.n]) / (calls_in * 1.0)

    def get_source_code(self, tab_level):
        code = ('\t' * tab_level) + "def " + self.name + "(self):\n"
        if len(self.vars) == 0 and len(self.m_calls) == 0:
            code += ('\t' * (tab_level + 1)) + "pass\n\n"
            return code
        for field in self.vars:
            code += ('\t' * (tab_level + 1)) + "self." + field + " = 0\n"
        for call in self.m_calls:
            code += ('\t' * (tab_level + 1)) + "self.method" + \
                str(call) + "()\n"
        code += "\n"
        return code

    def get_ast_node(self):
        return ast.parse(self.get_source_code(1)[1:]).body[0]
        # class GambiVisitor(ast.NodeVisitor):
        #     def visit_FunctionDef(self, node):
        #         return node

        # code = "class Gambiarra:\n" + self.get_source_code(1)
        # pdb.set_trace()
        # return GambiVisitor().visit(ast.parse(code))



def median(matrix):
    biggest_value = max([max(row) for row in matrix])
    smallest_value = min([min(row) for row in matrix])
    return (biggest_value + smallest_value) / 2.0

def matrix_index_of(matrix, e):
    for row in matrix:
        if e in row:
            return row
    return None

def merge(chain1, chain2):
    return list(set(chain1) | set(chain2))


def s_to_l(s):
    return [list(x) for x in s]


class SimpleCls(object):
    def __init__(self, n, max_vars, max_mets):
        self.name = "SimpleCls" + str(n)
        self.fields = ["var" + str(i) for i in rint(max_vars)]
        n_methods = rint(max_mets)
        self.methods = [SimpleMethod(i, rsample(self.fields),
            rvec(len(n_methods))) for i in n_methods]

    def get_source_code(self):
        code = "class " + self.name + ":\n"
        if len(self.fields) == 0 and len(self.methods) == 0:
            code += "\tpass\n"
            return code
        code += "\t" + var_def_line(len(self.fields)) + "\n\n"
        for m in self.methods:
            code += m.get_source_code(1)
        return code

    def get_ast_node(self):
        return ast.parse(self.get_source_code()).body[0]

    def get_matrix(self, w_ssm, w_cdm):
        matrix = []
        for row in range(len(self.methods)):
            matrix.append([])
            for col in range(len(self.methods)):
                if row == col:
                    matrix[row].append(1.0)
                elif row < col:
                    ssm = self.methods[row].ssm(self.methods[col]) * w_ssm
                    cdm_r = self.methods[row].cdm(self.methods[col],
                        self.methods)
                    cdm_c = self.methods[col].cdm(self.methods[row],
                        self.methods)
                    cdm = max(cdm_r, cdm_c) * w_cdm
                    matrix[row].append(ssm + cdm)
                else:
                    matrix[row].append(matrix[col][row])
        return matrix

    def get_ssm_matrix(self):
        matrix = []
        for row in range(len(self.methods)):
            matrix.append([])
            for col in range(len(self.methods)):
                if row == col:
                    matrix[row].append(1.0)
                elif row < col:
                    ssm = self.methods[row].ssm(self.methods[col])
                    matrix[row].append(ssm)
                else:
                    matrix[row].append(matrix[col][row])
        return matrix

    def get_cdm_matrix(self):
        matrix = []
        for row in range(len(self.methods)):
            matrix.append([])
            for col in range(len(self.methods)):
                if row == col:
                    matrix[row].append(1.0)
                elif row < col:
                    cdm = self.methods[row].cdm(self.methods[col],
                        self.methods)
                    cdm2 = self.methods[col].cdm(self.methods[row],
                        self.methods)
                    matrix[row].append(max(cdm, cdm2))
                else:
                    matrix[row].append(matrix[col][row])
        return matrix

    def filter_matrix(self, w_ssm, w_cdm, min_coupling=-1):
        matrix = self.get_matrix(w_ssm, w_cdm)
        cut_value = min_coupling
        if cut_value < 0:
            cut_value = median(matrix)
        for r, row in enumerate(matrix):
            for c, col in enumerate(row):
                if matrix[r][c] <= cut_value:
                    matrix[r][c] = 0.0
        return matrix

    def get_method_chains(self, w_ssm, w_cdm, min_coupling=-1):
        matrix = self.filter_matrix(w_ssm, w_cdm, min_coupling=min_coupling)
        if len(matrix) == 0:
            return []
        chains = [set([0])]
        #pdb.set_trace()
        for row in range(0, len(matrix)):
            tmp_chain = set([row])
            for col in range(row + 1, len(matrix[row])):
                if matrix[row][col] > 0.0:
                    tmp_chain.add(col)
            new_chain_list = []
            for chain in chains:
                if chain & tmp_chain:
                    tmp_chain |= chain
                else:
                    new_chain_list.append(chain)
            new_chain_list.append(tmp_chain)
            chains = new_chain_list
        return [["method" + str(c) for c in chain] for chain in chains]

    def get_method_by_name(self, name):
        method = [x for x in self.methods if x.name == name]
        if len(method) == 1:
            return method[0]
        return None

    def get_coupling(self, chain1, chain2, w_ssm, w_cdm):
        c1mets = [self.get_method_by_name(x) for x in chain1]
        c2mets = [self.get_method_by_name(x) for x in chain2]
        avg_coupling = 0.0
        for x, y in product(c1mets, c2mets):
            avg_coupling += x.ssm(y) * w_ssm
            avg_coupling += max(x.cdm(y, self.methods),
                y.cdm(x, self.methods)) * w_cdm
        return avg_coupling / (len(c1mets) * len(c2mets))

    def merge_trivial_chains(self, method_chains, min_length, w_ssm, w_cdm):
        trivial_chains = [x for x in method_chains if len(x) < min_length]
        if len(trivial_chains) == 0:
            return s_to_l(method_chains)
        non_trivial_chains = split_chains(method_chains, trivial_chains)
        if len(non_trivial_chains) == 0:
            return s_to_l(method_chains)
        for tchain in trivial_chains:
            max_coupling = 0
            chain_to_merge = None
            min_length = float("inf")
            for ntchain in non_trivial_chains:
                coupling = self.get_coupling(tchain, ntchain, w_ssm, w_cdm)
                logging.info("merge_trivial_chains: coupling " +
                    str(tchain) + " " + str(ntchain) + ": " +
                    str(coupling))
                if coupling >= max_coupling and len(ntchain) < min_length:
                    chain_to_merge = ntchain
                    max_coupling = coupling
            chain_to_merge.update(tchain)
            #pdb.set_trace()
        return s_to_l(non_trivial_chains)

    def build_classdef_node(self, n):
        return ast.ClassDef(
            name=self.name + str(n),
            bases=[],
            body=[],
            decorator_list=[]
        )

    def get_vars_from_chain(self, method_chain):
        methods = [self.get_method_by_name(name) for name in method_chain]
        fields = set([])
        for method in methods:
            fields.update(method.vars)
        return fields

    def build_named_fields(self, method_chain):
        fields = self.get_vars_from_chain(method_chain)
        return [ast.Name(id=field, ctx=ast.Store())
            for field in fields]

    def build_field_assignments(self, named_fields):
        return [ast.Assign(targets=[named_field],
                value=ast.Name(id='None', ctx=ast.Load()))
                for named_field in named_fields]

    def build_class(self, method_chain, n):
        class_def = self.build_classdef_node(n)
        named_fields = self.build_named_fields(method_chain)
        field_assignments = self.build_field_assignments(named_fields)
        method_nodes = [self.get_method_by_name(name).get_ast_node()
            for name in method_chain]
        #pdb.set_trace()
        class_def.body = field_assignments + method_nodes
        return class_def

    def assemble_classes(self, merged_chains):
        ast_nodes = [self.build_class(chain, i)
            for i, chain in enumerate(merged_chains)]
        return ast_nodes


class SimpleClsGenerator:
    def generate(self, quantity, max_vars, max_mets):
        return [SimpleCls(i, max_vars, max_mets) for i in range(quantity)]

def l_to_s(array):
    return [set(x) for x in array]

if __name__ == '__main__':
    import astpp
    simple_cls = SimpleCls(0, 10, 10)
    w_ssm = 0.5
    w_cdm = 0.5
    min_coupling = 0.1
    method_chains = simple_cls.get_method_chains(w_ssm, w_cdm, min_coupling)
    print print_chains(method_chains)
    # print method_chains
    merged_chains = simple_cls.merge_trivial_chains(l_to_s(method_chains), 3,
        w_ssm,
        w_cdm)
    print print_chains(merged_chains)
    print print_matrix_with_fabulousness(simple_cls.filter_matrix(0.5, 0.5,
        min_coupling=min_coupling))
    # merged_chains = simple_cls.merge_trivial_chains(l_to_s(method_chains), 3,
    #     w_ssm,
    #     w_cdm)
    # print print_chains(merged_chains)
    # assmbld = simple_cls.assemble_classes(merged_chains)
    # for acls in assmbld:
    #     print astpp.dump(acls)

#19031989
# if __name__ == '__main__':
#     t = Terminal()
#     simple_class = SimpleCls(0, 10, 10)
#     print simple_class.get_source_code()
#     print t.red(("-" * 5) + " matrix " + ("-" * 5))
#     # print t.bold(print_matrix(simple_class.get_matrix(0.5, 0.5)))
#     print print_matrix_with_fabulousness(simple_class.get_matrix(0.5, 0.5))
#     print t.blue(("-" * 5) + " filtered matrix " + ("-" * 5))
#     print print_matrix_with_fabulousness(simple_class.filter_matrix(0.5, 0.5,
#         min_coupling=0.4))
#     print t.green(("-" * 5) + " method chains " + ("-" * 5))
#     print str(simple_class.get_method_chains(0.5, 0.5,
#         min_coupling=0.4))
#     print str(simple_class.get_method_chains(0.5, 0.5,
#         min_coupling=0.4))

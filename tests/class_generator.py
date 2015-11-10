import random
import ast
import pdb

# from colorama import init
from blessings import Terminal

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



def median(matrix):
    biggest_value = max([max(row) for row in matrix])
    smallest_value = min([min(row) for row in matrix])
    return (biggest_value + smallest_value) / 2.0

def matrix_index_of(matrix, e):
    for row in matrix:
        if e in row:
            return row
    return None

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
        return ast.parse(self.get_source_code())

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


class SimpleClsGenerator:
    def generate(self, quantity, max_vars, max_mets):
        return [SimpleCls(i, max_vars, max_mets) for i in range(quantity)]

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

method_matrices = {
    "SampleClass":
    {
        "SSM":
        [
            [1.0, 0.0, 1/3.0, 2.0/3.0, 1/4.0],
            [0.0, 1.0, 0, 0, 1/2.0],
            [1/3.0, 0, 1, 1/2.0, 1/2.0],
            [2.0/3.0, 0, 1/2.0, 1, 1/2.0],
            [1/4.0, 1/2.0, 1/2.0, 1/2.0, 1]
        ],

        "CDM":
        [
            [1, 1/2.0, 1/2.0, 0, 1],
            [1/2.0, 1, 1/2.0, 0, 0],
            [1/2.0, 1/2.0, 1, 0, 0],
            [0, 0, 0, 1, 1],
            [1, 0, 0, 1, 1]
        ],

        "method_chains":
        [
            ["method1"],
            ["method0", "method2", "method3", "method4"]
        ]
    }
}

def matrix_scalar_mult(m, s):
    return [[m[i][j] * s for j in range(len(m[i]))] for i in range(len(m))]

def matrix_sum(m1, m2):
    return [[m1[i][j] + m2[i][j] for j in range(len(m1[i]))]
        for i in range(len(m1))]

def set_diagonal(m):
    rm = m
    for i, j in zip(range(len(m)), range(len(m))):
        rm[i][j] = 1.0
    return rm

class SampleClass:
    var0, var1, var2, var3, var4 = (0, 0, 0, 0, 0)
    def method0(self):
        var3 = 0
        var0 = 0
        var4 = 0
        var3 = 0
        self.method2()
        self.method1()
        return

    def method1(self):
        var1 = 0
        self.method1()
        self.method2()
        return

    def method2(self):
        var4 = 0
        return

    def method3(self):
        var4 = 0
        var0 = 0
        var4 = 0
        self.method4()
        return

    def method4(self):
        var4 = 0
        var1 = 0
        self.method3()
        self.method3()
        self.method0()
        return

def get_method_matrix(class_name, weight_ssm, weight_cdm):
    results = method_matrices[class_name]
    partial = matrix_scalar_mult(results["SSM"], weight_ssm)
    partial2 = matrix_scalar_mult(results["CDM"], weight_cdm)
    total = matrix_sum(partial, partial2)
    return set_diagonal(total)


def get_method_chains(class_name):
    return method_matrices[class_name]["method_chains"]


if __name__ == '__main__':
    matrix = get_method_matrix('SampleClass', 0.5, 0.5)
    for row in matrix:
        print row
    print ""
    n_matrix = []
    for n, row in enumerate(matrix):
        n_matrix.append([])
        for elt in row:
            if elt <= 0.4:
                n_matrix[n].append(0)
            else:
                n_matrix[n].append(elt)
    for row in n_matrix:
        print row

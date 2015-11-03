method_matrices = {
    "SampleClass":
    {
        "SSM":
        [
            [1.0, 0.0, (1.0 / 3.0)],
            [0.0, 1.0, 0.25],
            [(1.0 / 3.0), 0.25, 1.0]
        ],

        "CDM":
        [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
    },

    "SampleClass2":
    {
        "SSM":
        [
            [1.0]
        ],

        "CDM":
        [
            [1.0]
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
    var1 = 1000
    var2 = 78
    var3 = 93

    def __init__(self):
        self.var4 = 89

    def method1(self):
        self.var3 = self.var2 * 2

    def method2(self):
        self.var4 = self.var2*9
        self.var4 += self.var1


class SampleClass2:
    var0, var1, var2, var3, var4, var5, var6, var7, var8, var9 = \
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    def method0(self):
        var0 = 0
        var6 = 0
        var4 = 0
        var2 = 0
        var2 = 0
        var2 = 0


def get_method_matrix(class_name, weight_ssm, weight_cdm):
    results = method_matrices[class_name]
    partial = matrix_scalar_mult(results["SSM"], weight_ssm)
    partial2 = matrix_scalar_mult(results["CDM"], weight_cdm)
    total = matrix_sum(partial, partial2)
    return set_diagonal(total)

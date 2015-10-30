# L = shift left
# R = shift right
# X = xor

simple = ['L', 'R', 'X', 'X', 'LL', 'RR']
complex = simple + ['LX', 'RX', 'XL', 'XR']

def shift_left(pattern):
    return [pattern[(i+1) % 8] for i in range(8)]

def shift_right(pattern):
    return [pattern[(i-1) % 8] for i in range(8)]

def xor(pattern, xor):
    return [(not pattern[i] if xor[i] else pattern[i]) for i in range(8)]

def apply(pattern, code, xor_val):
    for c in code:
        if c == 'L': pattern = shift_left(pattern)
        elif c == 'R': pattern = shift_right(pattern)
        elif c == 'X': pattern = xor(pattern, xor_val)
    return pattern
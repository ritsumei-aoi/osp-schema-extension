import sympy as sp
from itertools import product
import sys

def get_n():
    return 1

n = get_n()

# Oscillators: a_1^+, a_1^-, b_k^+, b_k^- (k=1..n)
# Let's index them: 
# a^+ : 'a+'
# a^- : 'a-'
# b^+_k : ('b+', k)
# b^-_k : ('b-', k)

oscillators = ['a+', 'a-'] + [('b+', k) for k in range(1, n+1)] + [('b-', k) for k in range(1, n+1)]

def parity(o):
    if type(o) == str and o.startswith('a'):
        return 1
    return 0

# Base commutation relations for oscillators
# [A, B} = A B - (-1)^{p(A)p(B)} B A
# {a-, a+} = 1 => a- a+ + a+ a- = 1 => a- a+ = 1 - a+ a-
# [b-_j, b+_k] = \delta_{jk} => b-_j b+_k - b+_k b-_j = \delta_{jk}
# Others are 0.
# Plus the deformation:
# b_j^s a_1^\sigma - a_1^\sigma b_j^s = - gb_{\sigma, j, s} \kappa
# => b_j^s a_1^\sigma = a_1^\sigma b_j^s - gb_{\sigma, j, s} \kappa

# To multiply polynomials in oscillators, we can use a normal ordering:
# order: a+ then a- then b+ then b-

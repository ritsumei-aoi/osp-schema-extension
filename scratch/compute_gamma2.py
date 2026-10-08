import sympy as sp
from itertools import combinations_with_replacement, product

# We will build a simple normal ordering tool for polynomials in the oscillators.
# Oscillators: a+, a-, b1+, b1-, ..., bn+, bn-
# Normal order: b1+ ... bn+ b1- ... bn- a+ a- kappa

def normal_order(term, n):
    # term is a list of tuples: [ (type, idx, sign), ... ]
    # type: 'a', 'b', 'kappa', 'scalar'
    # we sort adjacent elements if they are out of order.
    # We return a list of (coefficient, list of tuples).
    # coefficient can contain symbolic gb variables.
    pass

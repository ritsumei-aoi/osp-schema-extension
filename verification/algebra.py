"""
Verify C(2) = osp(2|2) basis, brackets, deformation, and coboundary.
"""
import sympy as sp
from itertools import product

# Let's represent elements as linear combinations of normal-ordered monomials in oscillators.
# Oscillators for n=1:
# a+, a- (fermions, p=1)
# b+, b- (bosons, p=0)

# Normal ordering convention for monomials:
# (a+)^alpha (a-)^beta (b+)^mu (b-)^nu
# where alpha, beta in {0, 1}, mu, nu in {0, 1, 2, ...}
# Constant term: alpha=beta=mu=nu=0.

def normal_order(expr_dict):
    """
    expr_dict maps tuple of oscillators (e.g. ('b-', 'b+')) to coeff.
    We reduce products of oscillators to normal-ordered form:
    fermions first: a+, then a-
    bosons second: b+, then b-
    
    Relations:
    a- a+ = 1 - a+ a-
    (a+)^2 = 0
    (a-)^2 = 0
    b- b+ = b+ b- + 1
    
    Undeformed:
    [b, a] = 0 => b a = a b
    """
    pass

"""
Examine the bracket [X, Y]_gamma in L = g + kappa g:
Wait! In L = g + kappa g:
If C(n+1) is realized as a subalgebra of End(V), or if gamma(X, Y) is a cocycle with values in g:
Let's check if the commutator of quadratic forms in the pre-oscillator form gives a 2-cocycle gamma: g x g -> g!
In a general Lie superalgebra realized by quadratic elements Q(u, v):
Let's see what gamma(X, Y) actually is!
"""
import sympy as sp
from fractions import Fraction
from collections import defaultdict
from src.C_generators import build_c_basis
from test_fund_action import action_generator_on_osc

# Let's check how g acts on V:
even, odd, gens = build_c_basis(1)
V = ["a_1_p", "a_1_m", "b_1_p", "b_1_m"]

# For each X in g:
# rho(X): V -> V is a linear map!
# Let's check if rho(X) preserves the bilinear form (u|v)_0.
# (rho(X) u | v)_0 + (-1)^{p(X) p(u)} (u | rho(X) v)_0 = 0 ?

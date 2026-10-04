"""
Exact symbolic calculation of C(n+1) inhomogeneous deformations and coboundaries.
"""
import sympy as sp
from itertools import product

# Parity and oscillator algebra definitions:
# For C(n+1) = osp(2|2n):
# Fermionic oscillators: a_1^+, a_1^-
# Bosonic oscillators: b_k^+, b_k^- for k = 1, ..., n.

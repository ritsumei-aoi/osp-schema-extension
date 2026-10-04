"""
Symbolic computation of C(n+1) = osp(2|2n) structure constants,
inhomogeneous deformation gamma_gb, and coboundary delta_f.
"""

import sympy as sp
from sympy import symbols, Matrix, zeros, Rational, simplify

def build_Cn1(n=1):
    # Basis of oscillators:
    # Fermions: a_1^+ (index 'a+'), a_1^- ('a-')
    # Bosons: b_j^+ ('b+j'), b_j^- ('b-j') for j=1..n
    # Parity: p(a) = 1, p(b) = 0
    
    # We will represent generators as quadratic expressions:
    # G = sum c_{uv} u v
    pass


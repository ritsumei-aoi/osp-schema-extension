import sympy as sp
from sympy import Rational

# We can represent an element in the oscillator algebra as a dict of words to sympy Rational coeffs.
# Words are ordered tuples of oscillators:
# For C(n+1): oscillators are ('a_1_p', 'a_1_m', 'b_1_p', 'b_1_m', ..., 'b_n_p', 'b_n_m')
# Relations:
# a_1_m a_1_p = 1 - a_1_p a_1_m
# a_1_p^2 = 0, a_1_m^2 = 0
# b_i_m b_j_p = delta_ij + b_j_p b_i_m
# b_i_s b_j_s = b_j_s b_i_s (all bosons commute among same sign)
# [b, a] = 0 (all bosons commute with all fermions)

# Let's write a canonical reducer for the oscillator algebra.

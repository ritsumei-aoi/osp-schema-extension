"""
Scratch script to compute gamma coefficients symbolically for C(2).
"""
import sympy as sp
from src.C_generators import build_c_basis
from collections import defaultdict
from fractions import Fraction

# Deformed relations:
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# In associative algebra:
# b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma, j, s} * kappa
# and kappa is central: kappa X = (-1)^{p(X)} X kappa ?
# Notice: kappa is odd central. In supercommutator:
# [X, Y} = X Y - (-1)^{pX pY} Y X.
# If [X, Y} = [X, Y}_0 + kappa * gamma(X, Y),
# let's compute [X, Y} directly by expanding products in the enveloping algebra.

# Let's define the gb symbols:
# For n=1, 4 parameters: gb_p_1_p, gb_p_1_m, gb_m_1_p, gb_m_1_m
# where first index is sigma in {+,-}, second is j in {1..n}, third is s in {+,-}.

def commutator_b_a(b, a, gb_dict):
    # b is b_j_s, a is a_1_sigma
    # returns - gb_{sigma, j, s}
    return - gb_dict[(a, b)]

print("Scratch setup ready.")

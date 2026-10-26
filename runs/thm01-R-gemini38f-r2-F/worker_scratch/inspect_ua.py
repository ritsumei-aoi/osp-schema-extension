import sys
sys.path.append('.')
from src.C_generators import build_c_generators, Poly
from fractions import Fraction
from collections import defaultdict

# Let's inspect [X, Y] in U(A) where:
# {a_1^-, a_1^+} = 1
# [b_1^-, b_1^+] = 1
# [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
# [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa

# Let's compute [X, Y] for ALL 64 pairs in C(2):
# We want to see what terms appear in the coefficient of kappa!
data = build_c_generators(1)
full_basis = data["odd_basis"] + data["even_basis"]
generators = data["generators"]
parities = data["parities"]

# In U(A), any product of oscillators can be normally ordered:
# Normal order: kappa * (a_1^+)^fp (a_1^-)^fm (b_1^+)^u (b_1^-)^v
# Since each generator is degree 2:
# X * Y has degree 4.
# The commutator [X, Y] has degree 2!
# In the coefficient of kappa, what degrees appear?
# Since the deformation relation [b, a] = - gb * kappa reduces degree by 2:
# The degree of [X, Y] in kappa is at most: (2 + 2) - 2 = 2!
# So the coefficient of kappa is at most degree 2!
# What monomials of degree <= 2 appear?

import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators, parity_of, normal_order_word

def osc_key(osc: str):
    if osc == 'a_1_p': return (0, 0, 0)
    if osc == 'a_1_m': return (0, 1, 0)
    parts = osc.split('_')
    return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

# In U(A), a word is an ordered tuple of oscillators.
# Each term is coeff * param_factor * word
# At order 1 in kappa, param_factor is either 1 (order 0) or gb_{sigma, j, s} * kappa (order 1).
# Since kappa is odd (parity 1) and central in the Lie superalgebra,
# kappa * a_1^sigma = - a_1^sigma * kappa,
# kappa * b_j^s = b_j^s * kappa.
# What about gb? gb has parity 1.
# So (gb * kappa) is EVEN total parity!
# Wait, if (gb * kappa) has even total parity, then (gb * kappa) commutes with ALL oscillators!
# Let's check:
# (gb * kappa) * u = gb * (kappa * u) = gb * (-1)^{p(u)} u * kappa = (-1)^{p(u)} (-1)^{1 * p(u)} u * (gb * kappa) = u * (gb * kappa)!
# So (gb * kappa) is STRICTLY CENTRAL in U(A)!

print("gb * kappa commutes with EVERYTHING because both gb and kappa are odd!")

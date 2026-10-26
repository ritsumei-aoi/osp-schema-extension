import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
sys.path.insert(0, REPO_ROOT)
from src.C_generators import get_generators

even_basis, odd_basis, realizations, _, _, parity = get_generators(1)

# In C(2), odd generators are:
# E_eps1_del1_pp = a_1^+ b_1^+
# E_eps1_del1_pm = a_1^+ b_1^-
# E_eps1_del1_mp = a_1^- b_1^+
# E_eps1_del1_mm = a_1^- b_1^-

# Let's check comm_0 between each odd generator and oscillators in V:
# Recall:
# {a_1^-, a_1^+} = 1
# [b_1^-, b_1^+] = 1 (so [b_1^+, b_1^-] = -1)

# For E = a_1^sigma b_1^s (parity 1):
# [E, a_1^{sigma'}] = {a_1^sigma, a_1^{sigma'}} b_1^s
# [E, b_1^{s'}] = - a_1^sigma [b_1^s, b_1^{s'}]

# Let's check for each E:
odd_gens = ['E_eps1_del1_pp', 'E_eps1_del1_pm', 'E_eps1_del1_mp', 'E_eps1_del1_mm']
V = ['a_1_p', 'a_1_m', 'b_1_p', 'b_1_m']

# If Theta = c_pp E_pp + c_pm E_pm + c_mp E_mp + c_mm E_mm
# What is [Theta, X] for each generator X of C(2)?
# It is an INNER DERIVATION of C(2)!

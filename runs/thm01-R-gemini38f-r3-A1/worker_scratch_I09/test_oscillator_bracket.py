import sys, os
from fractions import Fraction
from collections import defaultdict
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../thm01-R-gemini38f-r3-A1")))
from src.C_generators import get_generators, normal_order_word

def parity_of(osc: str) -> int:
    return 1 if osc.startswith('a_') else 0

def osc_key(osc: str):
    if osc == 'a_1_p': return (0, 0, 0)
    if osc == 'a_1_m': return (0, 1, 0)
    parts = osc.split('_')
    return (1, int(parts[1]), 0 if parts[2] == 'p' else 1)

# Let's test the commutator [H_1, H_2] in U(A)
# H_1 = a_1^+ a_1^- + b_1^+ b_1^-
# H_2 = -b_1^+ b_1^- - 1/2
# Let's compute [H_1, H_2] = H_1 H_2 - H_2 H_1 in U(A) using:
# b_1^s a_1^sigma = a_1^sigma b_1^s - gb_{sigma, 1, s} * kappa
# where kappa * a_1^sigma = - a_1^sigma * kappa, kappa * b_1^s = b_1^s * kappa.
# And kappa is central in the Lie superalgebra, kappa^2 = 0.

# Notice H_1 H_2:
# (a_1^+ a_1^- + b_1^+ b_1^-)(-b_1^+ b_1^- - 1/2)
# = - a_1^+ a_1^- b_1^+ b_1^- - 1/2 a_1^+ a_1^- - (b_1^+ b_1^-)^2 - 1/2 b_1^+ b_1^-

# H_2 H_1:
# (-b_1^+ b_1^- - 1/2)(a_1^+ a_1^- + b_1^+ b_1^-)
# = - b_1^+ b_1^- a_1^+ a_1^- - (b_1^+ b_1^-)^2 - 1/2 a_1^+ a_1^- - 1/2 b_1^+ b_1^-

# So [H_1, H_2] = - a_1^+ a_1^- b_1^+ b_1^- + b_1^+ b_1^- a_1^+ a_1^-
# Now move b_1^+ b_1^- past a_1^+ a_1^-:
# b_1^- a_1^+ = a_1^+ b_1^- - gb_{a1+, b1-} kappa
# b_1^+ a_1^+ = a_1^+ b_1^+ - gb_{a1+, b1+} kappa
# b_1^- a_1^- = a_1^- b_1^- - gb_{a1-, b1-} kappa
# b_1^+ a_1^- = a_1^- b_1^+ - gb_{a1-, b1+} kappa

print("Let's analyze b_1^+ b_1^- a_1^+ a_1^-:")
# b_1^+ (b_1^- a_1^+) a_1^- = b_1^+ (a_1^+ b_1^- - gb_{a1+, b1-} kappa) a_1^-
# = (b_1^+ a_1^+) b_1^- a_1^- - b_1^+ gb_{a1+, b1-} kappa a_1^-
# = (a_1^+ b_1^+ - gb_{a1+, b1+} kappa) (a_1^- b_1^- - gb_{a1-, b1-} kappa) - gb_{a1+, b1-} kappa b_1^+ a_1^-
# Keep to order 1 in kappa:
# = a_1^+ b_1^+ a_1^- b_1^- - a_1^+ b_1^+ gb_{a1-, b1-} kappa - gb_{a1+, b1+} kappa a_1^- b_1^- - gb_{a1+, b1-} kappa (a_1^- b_1^+ - gb_{a1-, b1+} kappa)
# In the first term: a_1^+ (b_1^+ a_1^-) b_1^- = a_1^+ (a_1^- b_1^+ - gb_{a1-, b1+} kappa) b_1^- = a_1^+ a_1^- b_1^+ b_1^- - gb_{a1-, b1+} a_1^+ kappa b_1^-

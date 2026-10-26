"""
Scratch script to derive gamma coefficients from deformed oscillator relations.
[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
with kappa^2 = 0, p(kappa) = 1, p(gb) = 1.
"""
from collections import defaultdict
from fractions import Fraction
import sympy as sp
from src.C_generators import build_c_basis, order_key

# Let's inspect generators of C(2) (n=1):
even, odd, gens = build_c_basis(1)
print("Generators:")
for k, v in gens.items():
    print(f"  {k} (p={v['parity']}): {v['frappat_form']} -> {v['poly']}")

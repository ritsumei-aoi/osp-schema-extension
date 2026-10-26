"""
Check which elements failed to solve in M_sp.
"""
from derive_gamma import normal_order_deformed, get_gb_label
from src.C_generators import build_c_basis
from test_gamma_decomp import deformed_superbracket
from collections import defaultdict
from fractions import Fraction
import sympy as sp

even, odd, gens = build_c_basis(1)
full = even + odd

all_basis_words = set()
for g in gens.values():
    all_basis_words.update(g["poly"].keys())
word_list = sorted(list(all_basis_words))

M_sp = sp.Matrix(
    [[gens[name]["poly"].get(w, Fraction(0)) for name in full] for w in word_list]
)
print("M_sp shape:", M_sp.shape)
print("M_sp rank:", M_sp.rank())
# Notice M_sp is 9 x 8 !
# Because there are 9 words and 8 basis elements!
# Which vector in R^9 is not in the column space?
# Let's find the left nullspace of M_sp:
null_left = M_sp.T.nullspace()
print("Left nullspace vectors (constraints on word coefficients):", null_left)
for v in null_left:
    for idx, w in enumerate(word_list):
        if v[idx] != 0:
            print(f"   {v[idx]} * {w}")

"""
Examine the exact words in br_k for all pairs in C(2).
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
print("Basis words:", word_list)

extra_words = set()
for X in full:
    pX = gens[X]["parity"]
    for Y in full:
        pY = gens[Y]["parity"]
        b0, bk = deformed_superbracket(gens[X]["poly"], pX, gens[Y]["poly"], pY)
        for (w, gb), c in bk.items():
            if w not in all_basis_words:
                extra_words.add(w)

print("Extra words not in basis:", extra_words)

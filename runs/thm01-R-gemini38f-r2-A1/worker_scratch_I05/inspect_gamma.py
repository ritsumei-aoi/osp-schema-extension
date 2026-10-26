"""
Inspect what terms appear in br_k for n=1.
"""
from derive_gamma import normal_order_deformed, get_gb_label
from src.C_generators import build_c_basis
from collections import defaultdict
from fractions import Fraction

def inspect_gamma():
    even, odd, gens = build_c_basis(1)
    full = even + odd
    from test_gamma_decomp import deformed_superbracket
    for X in full:
        for Y in full:
            pX, pY = gens[X]["parity"], gens[Y]["parity"]
            b0, bk = deformed_superbracket(gens[X]["poly"], pX, gens[Y]["poly"], pY)
            if bk:
                print(f"[{X}, {Y}]_kappa:")
                for (w, gb), c in bk.items():
                    print(f"   gb={gb}: word={w}, coeff={c}")

if __name__ == "__main__":
    inspect_gamma()

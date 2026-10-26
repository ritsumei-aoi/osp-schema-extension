"""
Test decomposing gamma with Cartan + K=1 identification.
"""
from test_quadratic_bracket import superbracket_polys
from src.C_generators import build_c_basis
import sympy as sp
from collections import defaultdict
from fractions import Fraction

even, odd, gens = build_c_basis(1)
full = even + odd

all_words = set()
for g in gens.values():
    all_words.update(g["poly"].keys())
all_words.add(()) # scalar 1
word_list = sorted(list(all_words))

# Add K (scalar 1) to basis or allow scalar!
# If we allow scalar 1 as K:
full_with_K = full + ["K"]
M_sp = sp.Matrix(
    [[gens[name]["poly"].get(w, Fraction(0)) if name != "K" else (Fraction(1) if w == () else Fraction(0))
      for name in full_with_K] for w in word_list]
)
print("M_sp rank with K:", M_sp.rank(), "shape:", M_sp.shape)

all_closed = True
gamma_entries = []
for i, X in enumerate(full):
    for j, Y in enumerate(full):
        r0, rk = superbracket_polys(gens[X]["poly"], gens[Y]["poly"])
        for gb, wdict in rk.items():
            vk = sp.Matrix([wdict.get(w, Fraction(0)) for w in word_list])
            try:
                sol, _ = M_sp.gauss_jordan_solve(vk)
                for k, Z in enumerate(full_with_K):
                    if sol[k] != 0:
                        gamma_entries.append((X, Y, gb, Z, sol[k]))
            except Exception as e:
                print(f"Failed to decompose [{X}, {Y}] gb={gb}")
                all_closed = False

print("All closed with K:", all_closed)
print("Total gamma entries with K:", len(gamma_entries))
# Check if K actually appears with non-zero coeff:
K_entries = [e for e in gamma_entries if e[3] == "K"]
print("Entries with Z = K:", len(K_entries))
if K_entries:
    for e in K_entries[:10]:
        print(f"  [{e[0]}, {e[1]}]_gamma ({e[2]}) -> {e[4]} * K")

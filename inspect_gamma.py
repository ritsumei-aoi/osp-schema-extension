"""
Inspect violating triplets for cocycle condition
"""
import sympy as sp
from verify_cn1 import get_algebra
from verify_brackets import compute_brackets

alg = get_algebra(1)
dim_g = alg['dim_g']
generators = alg['generators']
p = [g['parity'] for g in generators]
bracket_0, gamma_def = compute_brackets(alg)

print("Inspecting non-zero gamma values:")
for i in range(dim_g):
    for j in range(dim_g):
        non_zero = [(generators[k]['name'], gamma_def[i][j][k]) for k in range(dim_g) if gamma_def[i][j][k] != 0]
        if non_zero:
            print(f"gamma({generators[i]['name']}, {generators[j]['name']}) = {non_zero}")

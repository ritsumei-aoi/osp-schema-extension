import json, os, sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"

with open(f"{REPO_ROOT}/data/C_1_structure.json") as f: s1 = json.load(f)
basis_even = s1["basis"]["even"]
basis_odd = s1["basis"]["odd"]
all_basis = basis_even + basis_odd
parity = s1["parity"]

c_base = defaultdict(Fraction)
for e in s1["structure_constants"]:
    c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

# For ANY Theta in g_1:
# Let f_Theta(X) = [X, Theta]
# What is (delta f_Theta)(X, Y)?
# By definition of coboundary of an inner derivation:
# (delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])

# Let's test for Theta = E_eps1_del1_pp:
Theta = 'E_eps1_del1_pp'

def f(X):
    # [X, Theta]
    res = defaultdict(Fraction)
    for Z in all_basis:
        c = c_base.get((X, Theta, Z), Fraction(0))
        if c != 0:
            res[Z] += c
    return res

def delta_f(X, Y):
    pX, pY = parity[X], parity[Y]
    res = defaultdict(Fraction)
    s1_sign = -1 if pX == 1 else 1
    s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)

    # Term 1: (-1)^pX [X, f(Y)]
    fY = f(Y)
    for w, cw in fY.items():
        for Z in all_basis:
            c = c_base.get((X, w, Z), Fraction(0))
            if c != 0:
                res[Z] += s1_sign * cw * c

    # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
    fX = f(X)
    for w, cw in fX.items():
        for Z in all_basis:
            c = c_base.get((Y, w, Z), Fraction(0))
            if c != 0:
                res[Z] += s2_sign * cw * c

    # Term 3: - f([X, Y])
    for w in all_basis:
        c_XY = c_base.get((X, Y, w), Fraction(0))
        if c_XY != 0:
            fw = f(w)
            for Z, cw in fw.items():
                res[Z] -= c_XY * cw

    return {k: v for k, v in res.items() if v != 0}

nonzero_brackets = 0
for X in all_basis:
    for Y in all_basis:
        df = delta_f(X, Y)
        if df:
            nonzero_brackets += 1
            print(f"(delta f)({X}, {Y}) = {df}")

print(f"Total non-zero brackets of delta f: {nonzero_brackets}")

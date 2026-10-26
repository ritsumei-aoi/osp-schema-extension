import json, os, sys
from fractions import Fraction
from collections import defaultdict

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"
with open(f"{REPO_ROOT}/data/C_1_structure.json") as f: s1 = json.load(f)
c_base = defaultdict(Fraction)
for e in s1["structure_constants"]:
    c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

# For param gb_a1p_b1m = 1:
# Theta = -1/2 E_eps1_del1_mp
# Let's check (delta f_Theta)(H_1, E_eps1_del1_pm):
# f(X) = [X, Theta]
Theta = 'E_eps1_del1_mp'
scale = Fraction(-1, 2)

def f(X):
    res = defaultdict(Fraction)
    for Z in s1["basis"]["even"] + s1["basis"]["odd"]:
        c = c_base.get((X, Theta, Z), Fraction(0))
        if c != 0: res[Z] += scale * c
    return res

def delta_f(X, Y):
    pX = s1["parity"][X]
    pY = s1["parity"][Y]
    s1_sign = -1 if pX == 1 else 1
    s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)
    res = defaultdict(Fraction)
    for w, cw in f(Y).items():
        for Z in s1["basis"]["even"] + s1["basis"]["odd"]:
            c = c_base.get((X, w, Z), Fraction(0))
            if c != 0: res[Z] += s1_sign * cw * c
    for w, cw in f(X).items():
        for Z in s1["basis"]["even"] + s1["basis"]["odd"]:
            c = c_base.get((Y, w, Z), Fraction(0))
            if c != 0: res[Z] += s2_sign * cw * c
    for w in s1["basis"]["even"] + s1["basis"]["odd"]:
        c_XY = c_base.get((X, Y, w), Fraction(0))
        if c_XY != 0:
            for Z, cw in f(w).items():
                res[Z] -= c_XY * cw
    return {k: v for k, v in res.items() if v != 0}

print("(delta f)(H_1, E_eps1_del1_pm) =", delta_f('H_1', 'E_eps1_del1_pm'))

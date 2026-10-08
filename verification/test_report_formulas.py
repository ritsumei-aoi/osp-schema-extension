"""
Cross-check of the closed-form (general-n) formulas stated in
docs/issues/mathematical_proof.md against the computed data, for n = 1, 2, 3:

  * f(H_1) formula (Def. 2.3)
  * f = 0 on all purely bosonic basis elements
  * scalar part f^0(E_{sigma eps + s delta_l}) = gb[sigma,l,s]/2, f^0 = 0 on even part
  * gamma(E_{eps+delta_k}, E_{eps+delta_l}) = gb[+,k,+] E_{eps+delta_l} + gb[+,l,+] E_{eps+delta_k}
  * [H_1, E_{eps+delta_l}]_0 = (1 + delta_{l1}) E_{eps+delta_l}
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from cn1 import CN1  # noqa: E402


def lab(sig, s, l):
    return "E[" + ("" if sig == "+" else "-") + "e" + ("+" if s == "+" else "-") + f"d{l}]"


def check(n):
    g = CN1(n)
    A = g.A
    L = {l: i for i, l in enumerate(g.labels)}
    phi, phi0 = g.explicit_f()
    ok = True
    exp = {}
    for j in range(1, n + 1):
        exp[L[lab("+", "+", j)]] = {(A.gb_flat("-", j, "-"),): Fraction(1)}
        exp[L[lab("+", "-", j)]] = {(A.gb_flat("-", j, "+"),): Fraction(-1)}
        exp[L[lab("-", "+", j)]] = {(A.gb_flat("+", j, "-"),): Fraction(-1)}
        exp[L[lab("-", "-", j)]] = {(A.gb_flat("+", j, "+"),): Fraction(1)}
    ok &= all(phi[i][L["H1"]] == exp.get(i, {}) for i in range(g.dim)) and not phi0[L["H1"]]
    for j in range(g.dim):
        if g.parity[j] == 0 and g.labels[j] != "H1":
            ok &= all(not phi[i][j] for i in range(g.dim)) and not phi0[j]
    for l in range(1, n + 1):
        for sig in "+-":
            for s in "+-":
                ok &= phi0[L[lab(sig, s, l)]] == {(A.gb_flat(sig, l, s),): Fraction(1, 2)}
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            a, b = L[lab("+", "+", k)], L[lab("+", "+", l)]
            exp = {}
            for c, key in ((b, (A.gb_flat("+", k, "+"),)), (a, (A.gb_flat("+", l, "+"),))):
                exp.setdefault(c, {})
                exp[c][key] = exp[c].get(key, Fraction(0)) + 1
            ok &= all(g.G[a][b].get(c, {}) == exp.get(c, {}) for c in range(g.dim))
    for l in range(1, n + 1):
        ok &= g.C[L["H1"]][L[lab("+", "+", l)]] == {L[lab("+", "+", l)]: Fraction(1 + (l == 1))}
    print(f"n={n}: all closed-form formulas of the report match the computed data: {ok}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if all(check(n) for n in (1, 2, 3)) else 1)

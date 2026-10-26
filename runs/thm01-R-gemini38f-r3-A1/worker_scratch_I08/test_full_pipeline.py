import json, os, sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"

def build_gamma_data(n: int):
    with open(f"{REPO_ROOT}/data/C_{n}_structure.json") as f: s1 = json.load(f)
    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    parity = s1["parity"]

    c_base = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

    gb_to_theta = {}
    for j in range(1, n + 1):
        gb_to_theta[f"gb_a1p_b{j}p"] = (f"E_eps1_del{j}_mm", Fraction(1, 2))
        gb_to_theta[f"gb_a1p_b{j}m"] = (f"E_eps1_del{j}_mp", Fraction(-1, 2))
        gb_to_theta[f"gb_a1m_b{j}p"] = (f"E_eps1_del{j}_pm", Fraction(1, 2))
        gb_to_theta[f"gb_a1m_b{j}m"] = (f"E_eps1_del{j}_pp", Fraction(-1, 2))

    def delta_f(Theta_element, scale):
        def f(X):
            res = defaultdict(Fraction)
            for Z in all_basis:
                c = c_base.get((X, Theta_element, Z), Fraction(0))
                if c != 0: res[Z] += scale * c
            return res

        df_entries = []
        for X in all_basis:
            pX = parity[X]
            s1_sign = -1 if pX == 1 else 1
            fX = f(X)
            for Y in all_basis:
                pY = parity[Y]
                s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)
                fY = f(Y)

                res = defaultdict(Fraction)
                for w, cw in fY.items():
                    for Z in all_basis:
                        c = c_base.get((X, w, Z), Fraction(0))
                        if c != 0: res[Z] += s1_sign * cw * c

                for w, cw in fX.items():
                    for Z in all_basis:
                        c = c_base.get((Y, w, Z), Fraction(0))
                        if c != 0: res[Z] += s2_sign * cw * c

                for w in all_basis:
                    c_XY = c_base.get((X, Y, w), Fraction(0))
                    if c_XY != 0:
                        for Z, cw in f(w).items():
                            res[Z] -= c_XY * cw

                for Z in all_basis:
                    val = res[Z]
                    if val != 0:
                        df_entries.append((X, Y, Z, val))
        return df_entries

    gamma_entries = []
    for param in sorted(gb_to_theta.keys()):
        theta_gen, scale = gb_to_theta[param]
        entries = delta_f(theta_gen, scale)
        for X, Y, Z, coeff in entries:
            gamma_entries.append({
                "X": X, "Y": Y, "Z": Z,
                "param": param,
                "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            })

    print(f"Rank n = {n}: Total gamma entries = {len(gamma_entries)}")
    return gamma_entries

for n in [1, 2, 3]:
    build_gamma_data(n)

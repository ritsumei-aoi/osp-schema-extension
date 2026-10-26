import json, os, sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"

def test_coboundary_for_rank(n: int):
    with open(f"{REPO_ROOT}/data/C_{n}_structure.json") as f: s1 = json.load(f)
    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    parity = s1["parity"]

    c_base = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

    # For each gb parameter, define Theta(p)
    # gb_a1p_b{j}p -> + 1/2 E_eps1_del{j}_mm
    # gb_a1p_b{j}m -> - 1/2 E_eps1_del{j}_mp
    # gb_a1m_b{j}p -> + 1/2 E_eps1_del{j}_pm
    # gb_a1m_b{j}m -> - 1/2 E_eps1_del{j}_pp

    gb_to_theta = {}
    for j in range(1, n + 1):
        gb_to_theta[f"gb_a1p_b{j}p"] = (f"E_eps1_del{j}_mm", Fraction(1, 2))
        gb_to_theta[f"gb_a1p_b{j}m"] = (f"E_eps1_del{j}_mp", Fraction(-1, 2))
        gb_to_theta[f"gb_a1m_b{j}p"] = (f"E_eps1_del{j}_pm", Fraction(1, 2))
        gb_to_theta[f"gb_a1m_b{j}m"] = (f"E_eps1_del{j}_pp", Fraction(-1, 2))

    # Let's compute delta f_Theta for each elementary Theta
    # f_Theta(X) = [X, Theta]
    def delta_f(Theta_element):
        def f(X):
            res = defaultdict(Fraction)
            for Z in all_basis:
                c = c_base.get((X, Theta_element, Z), Fraction(0))
                if c != 0: res[Z] += c
            return res

        df_dict = defaultdict(lambda: defaultdict(Fraction))
        for X in all_basis:
            pX = parity[X]
            s1_sign = -1 if pX == 1 else 1
            fX = f(X)
            for Y in all_basis:
                pY = parity[Y]
                s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)
                fY = f(Y)

                # Term 1: (-1)^pX [X, f(Y)]
                res = defaultdict(Fraction)
                for w, cw in fY.items():
                    for Z in all_basis:
                        c = c_base.get((X, w, Z), Fraction(0))
                        if c != 0: res[Z] += s1_sign * cw * c

                # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
                for w, cw in fX.items():
                    for Z in all_basis:
                        c = c_base.get((Y, w, Z), Fraction(0))
                        if c != 0: res[Z] += s2_sign * cw * c

                # Term 3: - f([X, Y])
                for w in all_basis:
                    c_XY = c_base.get((X, Y, w), Fraction(0))
                    if c_XY != 0:
                        fw = f(w)
                        for Z, cw in fw.items():
                            res[Z] -= c_XY * cw

                for Z, val in res.items():
                    if val != 0:
                        df_dict[(X, Y)][Z] = val
        return df_dict

    print(f"\n--- Rank n = {n} ({s1['algebra']['cartan_type']}) ---")
    for param, (theta_gen, scale) in sorted(gb_to_theta.items()):
        df = delta_f(theta_gen)
        num_brackets = sum(len(v) for v in df.values())
        print(f"Param {param}: Theta = {scale} * {theta_gen}, non-zero coboundary entries = {num_brackets}")

test_coboundary_for_rank(1)
test_coboundary_for_rank(2)
test_coboundary_for_rank(3)

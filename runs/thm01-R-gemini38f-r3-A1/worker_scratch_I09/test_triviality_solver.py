import json, os, sys
from fractions import Fraction
from collections import defaultdict
import sympy as sp

REPO_ROOT = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1"

def test_triviality_solver(n: int):
    with open(f"{REPO_ROOT}/data/C_{n}_structure.json") as f: s1 = json.load(f)
    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    parity = s1["parity"]

    c_base = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

    gb_labels = []
    gb_to_theta = {}
    for j in range(1, n + 1):
        for sigma in ['p', 'm']:
            for s in ['p', 'm']:
                label = f"gb_a1{sigma}_b{j}{s}"
                gb_labels.append(label)
                if sigma == 'p' and s == 'p': gb_to_theta[label] = (f"E_eps1_del{j}_mm", Fraction(1, 2))
                elif sigma == 'p' and s == 'm': gb_to_theta[label] = (f"E_eps1_del{j}_mp", Fraction(-1, 2))
                elif sigma == 'm' and s == 'p': gb_to_theta[label] = (f"E_eps1_del{j}_pm", Fraction(1, 2))
                elif sigma == 'm' and s == 'm': gb_to_theta[label] = (f"E_eps1_del{j}_pp", Fraction(-1, 2))

    gb_syms = [sp.Symbol(p) for p in gb_labels]
    gb_idx = {p: idx for idx, p in enumerate(gb_syms)}

    # Elementary coboundary for each theta component
    def delta_f_elem(Theta_element, scale):
        def f(X):
            res = defaultdict(Fraction)
            for Z in all_basis:
                c = c_base.get((X, Theta_element, Z), Fraction(0))
                if c != 0: res[Z] += scale * c
            return res

        df_dict = defaultdict(Fraction)
        for idx_X, X in enumerate(all_basis):
            pX = parity[X]
            s1_sign = -1 if pX == 1 else 1
            fX = f(X)
            for idx_Y, Y in enumerate(all_basis):
                if idx_X > idx_Y: continue
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
                        df_dict[(X, Y, Z)] = val
        return df_dict

    gamma_sym = defaultdict(lambda: sp.Integer(0))
    for param in gb_labels:
        t_gen, scale = gb_to_theta[param]
        df_elem = delta_f_elem(t_gen, scale)
        for (X, Y, Z), val in df_elem.items():
            gamma_sym[(X, Y, Z)] += val * sp.Symbol(param)

    # General odd linear map parameters phi_{target, source}
    phi_syms = []
    for j in basis_even:
        for i in basis_odd:
            phi_syms.append((i, j))
    for j in basis_odd:
        for i in basis_even:
            phi_syms.append((i, j))

    phi_idx = {pair: idx for idx, pair in enumerate(phi_syms)}
    n_phi = len(phi_syms)
    n_gb = len(gb_syms)

    # Linear system (delta f)(X, Y) - gamma(X, Y) = 0
    rows = []
    for idx_X, X in enumerate(all_basis):
        pX = parity[X]
        for idx_Y, Y in enumerate(all_basis):
            if idx_X > idx_Y: continue
            pY = parity[Y]
            for Z in all_basis:
                pZ = parity[Z]
                if pZ != (pX + pY + 1) % 2: continue

                row = [Fraction(0, 1)] * (n_phi + n_gb)
                s1_sign = -1 if pX == 1 else 1
                s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)

                for i in all_basis:
                    if (i, Y) in phi_idx:
                        c = c_base.get((X, i, Z), 0)
                        if c != 0: row[phi_idx[(i, Y)]] += s1_sign * c

                for i in all_basis:
                    if (i, X) in phi_idx:
                        c = c_base.get((Y, i, Z), 0)
                        if c != 0: row[phi_idx[(i, X)]] += s2_sign * c

                for k in all_basis:
                    c = c_base.get((X, Y, k), 0)
                    if c != 0 and (Z, k) in phi_idx:
                        row[phi_idx[(Z, k)]] -= c

                # gamma term
                g_expr = gamma_sym.get((X, Y, Z), sp.Integer(0))
                if g_expr != 0:
                    for p_sym in gb_syms:
                        coeff_p = g_expr.coeff(p_sym)
                        if coeff_p != 0:
                            row[n_phi + gb_idx[p_sym]] = -Fraction(coeff_p)

                if any(x != 0 for x in row):
                    rows.append(row)

    M = sp.Matrix(rows)
    rref_M, pivots = M.rref()

    gb_constraints = []
    for r in range(rref_M.rows):
        if all(rref_M[r, c] == 0 for c in range(n_phi)):
            expr = sum(rref_M[r, n_phi + c] * gb_syms[c] for c in range(n_gb))
            if expr != 0:
                gb_constraints.append(expr)

    print(f"Rank n = {n}: Augmented matrix rows = {M.rows}, cols = {M.cols}")
    print(f"Rank n = {n}: Constraints on gb for delta f = gamma: {gb_constraints}")
    print(f"Is gamma in im(delta) for ALL gb? {len(gb_constraints) == 0}")

test_triviality_solver(1)
test_triviality_solver(2)

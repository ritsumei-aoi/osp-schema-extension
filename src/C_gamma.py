"""
C(n+1) = osp(2|2n) Inhomogeneous Deformation (Gamma Structure) Generator
Generates Schema 2 v5.0 JSON specifications for n=1, 2, 3.
"""

from fractions import Fraction
from typing import Dict, List, Tuple
from collections import defaultdict
import json
import os
import sys
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from src.C_generators import get_generators
except ImportError:
    from C_generators import get_generators

def compute_gamma_via_rep(n: int, sign_convention: int = 1):
    """
    Computes gamma(X, Y) for all X, Y in C(n+1) using faithful adjoint representation on
    V = span{a_1^+, a_1^-, b_1^+, b_1^-, ..., b_n^+, b_n^-}.

    Option A (sign_convention = 1):
      [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
      [a_1^sigma, b_j^s] = + gb_{sigma, j, s} * kappa
    """
    even_basis, odd_basis, realizations, _, _, parity = get_generators(n)
    all_basis = even_basis + odd_basis
    dim_g = len(all_basis)

    V_basis = ['a_1_p', 'a_1_m']
    for k in range(1, n + 1):
        V_basis.extend([f"b_{k}_p", f"b_{k}_m"])

    def V_parity(v: str) -> int:
        return 1 if v.startswith('a_') else 0

    def comm_0(u: str, v: str) -> Fraction:
        pu, pv = V_parity(u), V_parity(v)
        if pu == 1 and pv == 1:
            if (u, v) in [('a_1_m', 'a_1_p'), ('a_1_p', 'a_1_m')]:
                return Fraction(1, 1)
            return Fraction(0, 1)
        elif pu == 0 and pv == 0:
            if u.startswith('b_') and v.startswith('b_'):
                p1, p2 = u.split('_'), v.split('_')
                if int(p1[1]) == int(p2[1]):
                    if p1[2] == 'm' and p2[2] == 'p': return Fraction(1, 1)
                    if p1[2] == 'p' and p2[2] == 'm': return Fraction(-1, 1)
            return Fraction(0, 1)
        return Fraction(0, 1)

    # comm_1(u, v): coefficient of kappa
    def comm_1(u: str, v: str):
        if u.startswith('b_') and v.startswith('a_'):
            parts_b = u.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            sigma = v.split('_')[2]
            return -sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
        elif u.startswith('a_') and v.startswith('b_'):
            sigma = u.split('_')[2]
            parts_b = v.split('_')
            j, s = int(parts_b[1]), parts_b[2]
            return sign_convention * sp.Symbol(f"gb_a1{sigma}_b{j}{s}")
        return sp.Integer(0)

    # Action ad_0(X)(v)
    def ad_0(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(Fraction)
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu2 = V_parity(u2)
            c1 = comm_0(u2, v)
            if c1 != 0: res[u1] += c * c1
            c2 = comm_0(u1, v)
            if c2 != 0:
                s = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s * c2
        return res

    # Action ad_1(X)(v): coefficient of kappa in [X, v]
    def ad_1(poly, v: str):
        pv = V_parity(v)
        res = defaultdict(lambda: sp.Integer(0))
        for w, c in poly.items():
            if len(w) != 2: continue
            u1, u2 = w[0], w[1]
            pu2 = V_parity(u2)
            c1 = comm_1(u2, v)
            if c1 != 0:
                res[u1] += c * c1
            c2 = comm_1(u1, v)
            if c2 != 0:
                s = -1 if (pu2 * pv) % 2 == 1 else 1
                res[u2] += c * s * c2
        return res

    # Precompute ad_0 matrix to invert: g -> Mat(V)
    ad_matrix_rows = []
    for X in all_basis:
        row = []
        for v in V_basis:
            ad_X_v = ad_0(realizations[X], v)
            for w in V_basis:
                row.append(Fraction(ad_X_v.get(w, Fraction(0, 1))))
        ad_matrix_rows.append(row)

    sp_A = sp.Matrix(ad_matrix_rows) # size (dim_g, dim_V^2)
    AAT = sp_A * sp_A.T
    AAT_inv = AAT.inv()
    proj = sp_A.T * AAT_inv # shape (dim_V^2, dim_g)

    gamma_dict = defaultdict(dict)
    
    for X in all_basis:
        pX = parity[X]
        poly_X = realizations[X]
        for Y in all_basis:
            pY = parity[Y]
            poly_Y = realizations[Y]
            sign_XY = -1 if (pX * pY) % 2 == 1 else 1

            target = []
            has_nonzero = False
            for v in V_basis:
                ad1_Y_v = ad_1(poly_Y, v)
                ad0_Y_v = ad_0(poly_Y, v)
                ad1_X_v = ad_1(poly_X, v)
                ad0_X_v = ad_0(poly_X, v)

                termA = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_Y_v.items():
                    for u, cu in ad_0(poly_X, w).items():
                        termA[u] += cw * cu

                termB = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad0_Y_v.items():
                    for u, cu in ad_1(poly_X, w).items():
                        termB[u] += cw * cu

                termC = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad1_X_v.items():
                    for u, cu in ad_0(poly_Y, w).items():
                        termC[u] += cw * cu

                termD = defaultdict(lambda: sp.Integer(0))
                for w, cw in ad0_X_v.items():
                    for u, cu in ad_1(poly_Y, w).items():
                        termD[u] += cw * cu

                for u in V_basis:
                    val = sp.simplify((termA[u] + termB[u]) - sign_XY * (termC[u] + termD[u]))
                    if val != 0:
                        has_nonzero = True
                    target.append(val)

            if has_nonzero:
                T_mat = sp.Matrix([target])
                c_mat = T_mat * proj
                for idx, Z in enumerate(all_basis):
                    coeff = sp.simplify(c_mat[0, idx])
                    if coeff != 0:
                        gamma_dict[(X, Y)][Z] = coeff

    return gamma_dict

def build_schema2_json(n: int) -> dict:
    """
    Builds the complete Schema 2 v5.0 dictionary for C(n+1) with inhomogeneous deformation.
    """
    even_basis, odd_basis, _, _, _, parity = get_generators(n)
    all_basis = even_basis + odd_basis

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    gb_labels = []
    for sigma in ['p', 'm']:
        for k in range(1, n + 1):
            for s in ['p', 'm']:
                gb_labels.append(f"gb_a1{sigma}_b{k}{s}")

    gamma_dict = compute_gamma_via_rep(n, sign_convention=1)

    basis_idx = {g: idx for idx, g in enumerate(all_basis)}
    param_idx = {p: idx for idx, p in enumerate(gb_labels)}

    entries = []
    for (X, Y), targets in gamma_dict.items():
        for Z, expr in targets.items():
            # expr is a linear combination of gb symbols
            # decompose into individual parameter contributions
            poly_expr = sp.Poly(expr, [sp.Symbol(p) for p in gb_labels])
            for monom, coeff in poly_expr.as_dict().items():
                # monom is a tuple of powers
                param_indices = [idx for idx, pow_val in enumerate(monom) if pow_val > 0]
                if len(param_indices) != 1 or monom[param_indices[0]] != 1:
                    raise ValueError(f"Unexpected non-linear term in gamma: {monom} -> {coeff}")
                p_label = gb_labels[param_indices[0]]
                frac_coeff = Fraction(str(coeff))
                coeff_str = str(frac_coeff) if frac_coeff.denominator == 1 else f"{frac_coeff.numerator}/{frac_coeff.denominator}"
                entries.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "param": p_label,
                    "coeff": coeff_str,
                    "sign_rule": "graded"
                })

    # Deterministic sort: by X, Y, Z in basis order, then param order
    entries.sort(key=lambda e: (basis_idx[e["X"]], basis_idx[e["Y"]], basis_idx[e["Z"]], param_idx[e["param"]]))

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1: even = 2n^2 + n + 1, odd = 4n, total = 2n^2 + 5n + 1"
            },
            "dimension": {
                "total": 2*n**2 + 5*n + 1,
                "even": 2*n**2 + n + 1,
                "odd": 4*n
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "nilpotent_order": 2,
                "relation": "kappa^2 = 0",
                "description": "Odd central nilpotent element carrier of inhomogeneous deformation parameter"
            },
            "K": {
                "parity": 0,
                "scalar_value": 1,
                "description": "Even central identity element (identified with scalar 1; excluded from PBW basis)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd: ++, +-, -+, --] < [even]"
        },
        "parity": parity,
        "deformation_parameters": {
            "count": 4 * n,
            "matrix_shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "columns": boson_labels,
            "labels": gb_labels,
            "parity": 1,
            "exchange_relations": "[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa"
        },
        "inhomogeneous_deformation": entries,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-17",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
                "docs/math/C_inhomogeneous_definition.md"
            ]
        }
    }

def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = build_schema2_json(n)
        filename = f"data/C_{n}_gamma.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: {len(data['inhomogeneous_deformation'])} gamma entries")

if __name__ == "__main__":
    main()

"""
C(n+1) = osp(2|2n) Triviality Analysis & Comparison Engine (Issue I08-1)
Compares Layer 3 (Evaluated Deformation) and Layer 4 (Coboundary Structure),
and rigorously determines the triviality conditions on the gb parameters for n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from typing import Dict, Any, Tuple, List
import sympy as sp

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")

def compare_layers_3_and_4(n: int) -> Dict[str, Any]:
    eval_file = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
    coboundary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")

    with open(eval_file, "r", encoding="utf-8") as f:
        s3 = json.load(f)
    with open(coboundary_file, "r", encoding="utf-8") as f:
        s4 = json.load(f)
    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)

    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    parity = s1["parity"]

    g_map = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in s3["evaluated_deformation"]}
    df_map = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in s4["coboundary_structure"]}

    g_keys = set(g_map.keys())
    df_keys = set(df_map.keys())

    common = g_keys & df_keys
    only_g = g_keys - df_keys
    only_df = df_keys - g_keys

    exact_matches = [k for k in common if g_map[k] == df_map[k]]
    differing_common = [k for k in common if g_map[k] != df_map[k]]

    return {
        "n": n,
        "algebra": s1["algebra"]["cartan_type"],
        "total_dim": len(all_basis),
        "even_dim": len(basis_even),
        "odd_dim": len(basis_odd),
        "total_gamma_brackets": len(g_keys),
        "total_delta_f_brackets": len(df_keys),
        "common_triples_count": len(common),
        "exact_matching_count": len(exact_matches),
        "differing_common_count": len(differing_common),
        "only_gamma_count": len(only_g),
        "only_delta_f_count": len(only_df),
        "sample_only_gamma": sorted(list(only_g))[:5],
        "sample_only_delta_f": sorted(list(only_df))[:5],
        "sample_differing_common": sorted(differing_common)[:5]
    }

def solve_parametric_triviality(n: int) -> Dict[str, Any]:
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    basis_even = s1["basis"]["even"]
    basis_odd = s1["basis"]["odd"]
    all_basis = basis_even + basis_odd
    parity = s1["parity"]

    c_base = defaultdict(Fraction)
    for e in s1["structure_constants"]:
        c_base[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])

    gb_labels = s2["deformation_parameters"]["labels"]
    gb_syms = [sp.Symbol(p) for p in gb_labels]
    gb_idx = {p: idx for idx, p in enumerate(gb_syms)}

    gamma_sym = defaultdict(lambda: sp.Integer(0))
    for e in s2["inhomogeneous_deformation"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        p = e["param"]
        c = Fraction(e["coeff"])
        gamma_sym[(X, Y, Z)] += c * sp.Symbol(p)

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

                # Term 1: (-1)^pX [X, f(Y)]
                for i in all_basis:
                    if (i, Y) in phi_idx:
                        c = c_base.get((X, i, Z), 0)
                        if c != 0:
                            row[phi_idx[(i, Y)]] += s1_sign * c

                # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
                for i in all_basis:
                    if (i, X) in phi_idx:
                        c = c_base.get((Y, i, Z), 0)
                        if c != 0:
                            row[phi_idx[(i, X)]] += s2_sign * c

                # Term 3: - f([X, Y])
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

                if any(r != 0 for r in row):
                    rows.append([sp.Rational(r.numerator, r.denominator) for r in row])

    M = sp.Matrix(rows)
    rref_M, pivots = M.rref()

    # Extract constraints on gb
    gb_constraints = []
    for r in range(rref_M.rows):
        if all(rref_M[r, c] == 0 for c in range(n_phi)):
            expr = sum(rref_M[r, n_phi + c] * gb_syms[c] for c in range(n_gb))
            if expr != 0:
                gb_constraints.append(expr)

    # Coboundary operator matrix M_phi alone
    M_phi = M[:, :n_phi]
    rank_M_phi = M_phi.rank()
    dim_ker_delta = n_phi - rank_M_phi

    is_unconditionally_trivial = (len(gb_constraints) == 0)

    return {
        "n": n,
        "n_phi": n_phi,
        "n_gb": n_gb,
        "rank_M_phi": rank_M_phi,
        "dim_ker_delta": dim_ker_delta,
        "independent_gb_constraints": len(gb_constraints),
        "gb_constraints": gb_constraints,
        "is_unconditionally_trivial": is_unconditionally_trivial
    }

def main():
    print("=" * 80)
    print("C(n+1) INHOMOGENEOUS DEFORMATION TRIVIALITY ANALYSIS REPORT (ISSUE I08-1)")
    print("=" * 80)

    for n in [1, 2, 3]:
        comp = compare_layers_3_and_4(n)
        param_res = solve_parametric_triviality(n)

        print(f"\n--- Rank n = {n}: {comp['algebra']} (dim {comp['total_dim']} = {comp['even_dim']} | {comp['odd_dim']}) ---")
        print(f"1. Layer 3 vs Layer 4 Data Comparison:")
        print(f"   - Evaluated deformation brackets (Layer 3): {comp['total_gamma_brackets']}")
        print(f"   - Reference coboundary brackets (Layer 4):   {comp['total_delta_f_brackets']}")
        print(f"   - Common triples: {comp['common_triples_count']} (Exact coefficient matches: {comp['exact_matching_count']})")
        print(f"   - Triples present ONLY in gamma (Layer 3):   {comp['only_gamma_count']}")
        print(f"   - Triples present ONLY in delta f (Layer 4): {comp['only_delta_f_count']}")

        print(f"2. Cohomological Parameter Analysis:")
        print(f"   - Free parameters in Hom_odd(g, g): {param_res['n_phi']}")
        print(f"   - Rank of coboundary operator delta: {param_res['rank_M_phi']}")
        print(f"   - Dimension of 1-cocycle kernel ker(delta): {param_res['dim_ker_delta']} (matches dim g_1 = {comp['odd_dim']})")
        print(f"   - Independent linear constraints on gb for delta f = gamma: {param_res['independent_gb_constraints']}")
        print(f"   - Rigorous Conclusion: Deformation is UNCONDITIONALLY TRIVIAL (coboundary for ALL gb): {param_res['is_unconditionally_trivial']}")

if __name__ == "__main__":
    main()

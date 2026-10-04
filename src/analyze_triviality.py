import os
import sys
import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any
import numpy as np
import sympy as sp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def analyze_triviality_for_n(n: int):
    # Load Schema 1, 2, 4
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r") as f:
        s2 = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        s4 = json.load(f)

    basis = s1["basis"]["odd"] + s1["basis"]["even"]
    gb_params = s2["gb_matrix"]["parameters"]
    phi_params = s4["linear_map_parameters"]["parameters"]

    # Map (X, Y, Z) triples
    # Collect all (X, Y, Z) with X <= Y in basis ordering
    # (since skew-symmetry holds, X <= Y contains all independent equations)
    basis_idx = {name: i for i, name in enumerate(basis)}

    all_triples = set()
    # From gamma
    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        if basis_idx[X] <= basis_idx[Y]:
            all_triples.add((X, Y, Z))

    # From coboundary
    for entry in s4["coboundary_structure"]["entries"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        if basis_idx[X] <= basis_idx[Y]:
            all_triples.add((X, Y, Z))

    triple_list = sorted(list(all_triples))
    triple_to_row = {t: i for i, t in enumerate(triple_list)}
    phi_to_col = {p: j for j, p in enumerate(phi_params)}
    gb_to_col = {p: k for k, p in enumerate(gb_params)}

    n_rows = len(triple_list)
    n_phi = len(phi_params)
    n_gb = len(gb_params)

    # Build SymPy Rational matrices for exact computation
    M_sp = sp.zeros(n_rows, n_phi)
    G_sp = sp.zeros(n_rows, n_gb)

    for entry in s4["coboundary_structure"]["entries"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        if basis_idx[X] <= basis_idx[Y]:
            r = triple_to_row[(X, Y, Z)]
            c = phi_to_col[entry["phi_param"]]
            M_sp[r, c] += sp.Rational(entry["coeff"])

    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        if basis_idx[X] <= basis_idx[Y]:
            r = triple_to_row[(X, Y, Z)]
            c = gb_to_col[entry["gb_param"]]
            G_sp[r, c] += sp.Rational(entry["coeff"])

    print(f"\n=======================================================")
    print(f"TRIVIALITY ANALYSIS FOR C({n+1}) [n={n}]")
    print(f"=======================================================")
    print(f"Independent (X, Y, Z) equations: {n_rows}")
    print(f"Odd linear map variables (phi): {n_phi}")
    print(f"Deformation parameters (gb): {n_gb} -> {gb_params}")

    # Compute rank of M
    # Convert to float for fast rank check, and sympy for exact nullspace
    M_np = np.array(M_sp.tolist(), dtype=float)
    rank_M = np.linalg.matrix_rank(M_np)
    print(f"Rank of Coboundary Matrix M: {rank_M} / {n_phi}")

    # Left nullspace of M (coker of M): W^T M = 0
    # Augmented matrix [M | G]
    aug = M_sp.row_join(G_sp)
    rref_aug, pivot_cols = aug.rref()
    
    # Check if there are non-zero rows in RREF that have pivots in the G block
    g_pivot_cols = [c - n_phi for c in pivot_cols if c >= n_phi]
    print(f"Number of independent obstruction equations on gb: {len(g_pivot_cols)}")

    # Extract the exact linear constraints on gb
    # For rows where M part is 0, the G part gives linear constraints on gb
    constraints = []
    for r in range(rank_M, n_rows):
        row = rref_aug[r, n_phi:]
        if any(v != 0 for v in row):
            # Form linear combination
            eq_terms = []
            for k, param in enumerate(gb_params):
                coeff = row[k]
                if coeff != 0:
                    eq_terms.append(f"{coeff} * {param}")
            eq_str = " + ".join(eq_terms).replace("+ -", "- ") + " == 0"
            constraints.append(eq_str)

    print(f"\nExact linear constraints on gb for triviality ({len(constraints)} equations):")
    for i, eq in enumerate(constraints, 1):
        print(f"  ({i}) {eq}")

    # Test all-ones assignment (gb = +1)
    gb_ones = sp.Matrix([1] * n_gb)
    # Check if M * phi = G * gb_ones is solvable
    rhs_ones = G_sp * gb_ones
    sol_ones = None
    try:
        sol_ones = M_sp.gauss_jordan_solve(rhs_ones)
        is_ones_trivial = True
    except ValueError:
        is_ones_trivial = False
    print(f"\nRepresentative assignment (all gb = +1): {'TRIVIAL' if is_ones_trivial else 'NON-TRIVIAL (OBSTRUCTED)'}")

    # Test single-parameter assignments
    print("\nSingle-parameter assignments (one gb=1, all other 0):")
    single_param_results = {}
    for k, param in enumerate(gb_params):
        gb_single = sp.zeros(n_gb, 1)
        gb_single[k, 0] = 1
        rhs = G_sp * gb_single
        try:
            M_sp.gauss_jordan_solve(rhs)
            single_param_results[param] = "TRIVIAL"
        except ValueError:
            single_param_results[param] = "NON-TRIVIAL"
        print(f"  {param}: {single_param_results[param]}")

    return {
        "n": n,
        "n_rows": n_rows,
        "n_phi": n_phi,
        "n_gb": n_gb,
        "rank_M": int(rank_M),
        "obstruction_count": len(g_pivot_cols),
        "constraints": constraints,
        "is_all_ones_trivial": is_ones_trivial,
        "single_param_results": single_param_results
    }


def run_all_analysis():
    results = {}
    for n in [1, 2, 3]:
        results[n] = analyze_triviality_for_n(n)
    return results


if __name__ == "__main__":
    run_all_analysis()

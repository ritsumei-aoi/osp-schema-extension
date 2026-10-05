"""
Triviality Condition Solver & Linear Algebra Analysis for C(n+1)
"""
import json
import os
import sys
import numpy as np
from fractions import Fraction
from typing import Dict, List, Tuple

def solve_triviality_for_n(n: int, gb_values: Dict[str, Fraction] = None):
    filepath_gamma = f"data/C_{n}_gamma.json"
    filepath_coboundary = f"data/C_{n}_coboundary.json"
    filepath_struct = f"data/C_{n}_structure.json"

    with open(filepath_struct, "r") as f:
        data_struct = json.load(f)
    with open(filepath_gamma, "r") as f:
        data_gamma = json.load(f)
    with open(filepath_coboundary, "r") as f:
        data_coboundary = json.load(f)

    basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
    gb_labels = data_gamma["gb_parameters"]["labels"]
    phi_params = [p["name"] for p in data_coboundary["linear_map_f"]["parameters"]]

    # Default: evaluate with given gb_values, or all 1s
    if gb_values is None:
        gb_values = {gb: Fraction(1) for gb in gb_labels}

    # Build target vector V_gamma: key (X, Y, Z) -> Fraction
    v_gamma_map: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in data_gamma["gamma_terms"]:
        gb_name = entry["gb_param"]
        gb_val = gb_values.get(gb_name, Fraction(0))
        if gb_val != 0:
            key = (entry["X"], entry["Y"], entry["Z"])
            c = Fraction(entry["coeff"]) * gb_val
            v_gamma_map[key] = v_gamma_map.get(key, Fraction(0)) + c

    # Index all equations (X, Y, Z) that have non-zero entries in coboundary or gamma
    eq_keys = set(v_gamma_map.keys())
    for entry in data_coboundary["coboundary_terms"]:
        eq_keys.add((entry["X"], entry["Y"], entry["Z"]))

    eq_list = sorted(list(eq_keys))
    phi_idx_map = {name: i for i, name in enumerate(phi_params)}
    eq_idx_map = {eq: i for i, eq in enumerate(eq_list)}

    num_eqs = len(eq_list)
    num_vars = len(phi_params)

    # Build matrix M and rhs vector V
    M = np.zeros((num_eqs, num_vars), dtype=np.float64)
    V = np.zeros(num_eqs, dtype=np.float64)

    for key, val in v_gamma_map.items():
        if key in eq_idx_map:
            V[eq_idx_map[key]] = float(val)

    for entry in data_coboundary["coboundary_terms"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        phi_name = entry["phi_param"]
        if key in eq_idx_map and phi_name in phi_idx_map:
            M[eq_idx_map[key], phi_idx_map[phi_name]] = float(Fraction(entry["coeff"]))

    # Solve least squares / rank check
    rank_M = np.linalg.matrix_rank(M)
    M_augmented = np.hstack([M, V.reshape(-1, 1)])
    rank_aug = np.linalg.matrix_rank(M_augmented)

    is_trivial = (rank_M == rank_aug)

    # Calculate residual norm
    if is_trivial:
        phi_sol, residuals, rank, s = np.linalg.lstsq(M, V, rcond=None)
        res_norm = np.linalg.norm(M @ phi_sol - V)
    else:
        phi_sol, residuals, rank, s = np.linalg.lstsq(M, V, rcond=None)
        res_norm = np.linalg.norm(M @ phi_sol - V)

    # Find worst discrepancies (equations where M @ phi_sol != V)
    discrepancies = []
    if not is_trivial:
        diff = V - M @ phi_sol
        for i, d in enumerate(diff):
            if abs(d) > 1e-5:
                x, y, z = eq_list[i]
                discrepancies.append((x, y, z, V[i], (M @ phi_sol)[i], d))

    return {
        "n": n,
        "algebra": f"C({n+1})",
        "num_equations": num_eqs,
        "num_phi_vars": num_vars,
        "rank_M": int(rank_M),
        "rank_augmented": int(rank_aug),
        "is_trivial": is_trivial,
        "residual_norm": float(res_norm),
        "discrepancies_count": len(discrepancies),
        "discrepancies_sample": discrepancies[:10]
    }

def analyze_all_ranks():
    print("=" * 70)
    print("TRIVIALITY CONDITION ANALYSIS FOR C(n+1) = osp(2|2n)")
    print("=" * 70)

    for n in (1, 2, 3):
        # 1. Test all gb = +1
        res = solve_triviality_for_n(n)
        print(f"Rank n={n} ({res['algebra']}): Profile ALL gb = +1")
        print(f"  Equations: {res['num_equations']}, Phi Variables: {res['num_phi_vars']}")
        print(f"  Rank(M): {res['rank_M']}, Rank([M|V]): {res['rank_augmented']}")
        print(f"  Is Trivial (Coboundary): {res['is_trivial']}")
        print(f"  Residual Norm: {res['residual_norm']:.6f}")
        print(f"  Discrepancies Count: {res['discrepancies_count']}")
        if res['discrepancies_sample']:
            print("  Sample Discrepancies (X, Y -> Z, V_gamma, (delta f)_proj, diff):")
            for x, y, z, v_g, v_cb, diff in res['discrepancies_sample']:
                print(f"    [{x}, {y}] -> {z}: V_gamma = {v_g:.3f}, (delta f) = {v_cb:.3f}, diff = {diff:.3f}")
        print("-" * 70)

        # 2. Test single parameter gb_a1p_b1p = 1 (all others 0)
        filepath_gamma = f"data/C_{n}_gamma.json"
        with open(filepath_gamma, "r") as f:
            data_gamma = json.load(f)
        gb_labels = data_gamma["gb_parameters"]["labels"]
        single_gb = {gb: Fraction(0) for gb in gb_labels}
        single_gb["gb_a1p_b1p"] = Fraction(1)
        res_single = solve_triviality_for_n(n, single_gb)

        print(f"Rank n={n} ({res_single['algebra']}): Profile SINGLE gb_a1p_b1p = 1")
        print(f"  Rank(M): {res_single['rank_M']}, Rank([M|V]): {res_single['rank_augmented']}")
        print(f"  Is Trivial (Coboundary): {res_single['is_trivial']}")
        print(f"  Residual Norm: {res_single['residual_norm']:.6f}")
        print("-" * 70)

if __name__ == "__main__":
    analyze_all_ranks()

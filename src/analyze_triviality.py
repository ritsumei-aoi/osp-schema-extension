"""
Analysis script for C(n+1) triviality search.
Sets up the linear system gamma(X, Y) = (delta f)(X, Y) and solves for phi.
"""

import json
from fractions import Fraction
import numpy as np
from typing import Dict, List, Tuple, Any

def analyze_triviality_for_n(n: int, gb_value_map: Dict[str, Fraction] = None) -> Dict[str, Any]:
    with open(f"data/C_{n}_structure.json") as f:
        struct_data = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        coboundary_data = json.load(f)

    gb_params = gamma_data["gb_matrix"]["parameters"]
    if gb_value_map is None:
        gb_value_map = {param: Fraction(1) for param in gb_params}

    all_basis = struct_data["basis"]["odd"] + struct_data["basis"]["even"]
    parity_map = struct_data["parity"]

    # 1. Collect all non-zero equations (X, Y, Z) where gamma or delta_f is non-zero
    eq_indices = {}
    eq_list = []

    # Calculate gamma_eval(X, Y) for target Z
    gamma_eval: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in gamma_data["gamma_structure"]:
        x, y = entry["X"], entry["Y"]
        for gb_param, term_list in entry["gamma_value"].items():
            val = gb_value_map.get(gb_param, Fraction(0))
            if val != 0:
                for term in term_list:
                    z = term["Z"]
                    key = (x, y, z)
                    gamma_eval[key] = gamma_eval.get(key, Fraction(0)) + Fraction(term["coeff"]) * val
                    if key not in eq_indices:
                        eq_indices[key] = len(eq_list)
                        eq_list.append(key)

    # Calculate delta_f expressions in terms of phi_{target}_{source}
    phi_params = []
    phi_indices = {}

    for x in all_basis:
        px = parity_map[x]
        for y in all_basis:
            if parity_map[y] != px:
                param_name = f"phi_{y}_{x}"
                if param_name not in phi_indices:
                    phi_indices[param_name] = len(phi_params)
                    phi_params.append(param_name)

    # Build matrix M and vector b for M phi = b
    # First, collect all (x, y, z) equations from coboundary structure
    for entry in coboundary_data["coboundary_structure"]:
        x, y = entry["X"], entry["Y"]
        for phi_param, term_list in entry["delta_f_value"].items():
            for term in term_list:
                z = term["Z"]
                key = (x, y, z)
                if key not in eq_indices:
                    eq_indices[key] = len(eq_list)
                    eq_list.append(key)

    num_eqs = len(eq_list)
    num_vars = len(phi_params)

    M = np.zeros((num_eqs, num_vars), dtype=float)
    b = np.zeros(num_eqs, dtype=float)

    # Fill b
    for key, val in gamma_eval.items():
        row_idx = eq_indices[key]
        b[row_idx] = float(val)

    # Fill M
    for entry in coboundary_data["coboundary_structure"]:
        x, y = entry["X"], entry["Y"]
        for phi_param, term_list in entry["delta_f_value"].items():
            col_idx = phi_indices[phi_param]
            for term in term_list:
                z = term["Z"]
                key = (x, y, z)
                row_idx = eq_indices[key]
                M[row_idx, col_idx] = float(Fraction(term["coeff"]))

    # Solve linear system using SVD / least squares / rank test
    rank_M = np.linalg.matrix_rank(M)
    M_aug = np.hstack([M, b.reshape(-1, 1)])
    rank_aug = np.linalg.matrix_rank(M_aug)

    is_trivial = (rank_M == rank_aug)

    # Find residual
    phi_sol, residuals, rank, s = np.linalg.lstsq(M, b, rcond=None)
    max_error = np.max(np.abs(M @ phi_sol - b))

    # Identify largest discrepancy equations if non-trivial
    diff = np.abs(M @ phi_sol - b)
    worst_eqs = []
    top_indices = np.argsort(diff)[::-1][:5]
    for idx in top_indices:
        if diff[idx] > 1e-5:
            key = eq_list[idx]
            worst_eqs.append({
                "X": key[0], "Y": key[1], "Z": key[2],
                "gamma_val": b[idx],
                "delta_f_val": (M @ phi_sol)[idx],
                "error": diff[idx]
            })

    return {
        "n": n,
        "cartan_type": f"C({n+1})",
        "num_equations": num_eqs,
        "num_variables": num_vars,
        "rank_M": int(rank_M),
        "rank_aug": int(rank_aug),
        "is_trivial": is_trivial,
        "max_error": float(max_error),
        "worst_discrepancies": worst_eqs
    }


def run_triviality_analysis():
    print("=== Triviality Analysis for C(n+1) = osp(2|2n) ===")
    for n in [1, 2, 3]:
        # Test unit profile gb = 1
        res = analyze_triviality_for_n(n)
        print(f"\n[C({n+1}) Unit Profile gb=1]:")
        print(f"  Equations: {res['num_equations']}, Variables: {res['num_variables']}")
        print(f"  Rank M: {res['rank_M']}, Rank [M|b]: {res['rank_aug']}")
        print(f"  Is Trivial: {res['is_trivial']} (Max error: {res['max_error']:.6e})")

        if not res['is_trivial']:
            print("  Top Discrepancies:")
            for disc in res['worst_discrepancies']:
                print(f"    ({disc['X']}, {disc['Y']}) -> {disc['Z']}: gamma = {disc['gamma_val']:.4f}, delta_f = {disc['delta_f_val']:.4f}, diff = {disc['error']:.4f}")

        # Also test individual gb parameter activations
        with open(f"data/C_{n}_gamma.json") as f:
            g_data = json.load(f)
        params = g_data["gb_matrix"]["parameters"]

        print(f"  Testing individual gb parameter activations ({len(params)} params):")
        for p in params:
            single_map = {k: Fraction(1) if k == p else Fraction(0) for k in params}
            res_p = analyze_triviality_for_n(n, single_map)
            print(f"    Param {p:15s}: Is Trivial = {res_p['is_trivial']}, Rank M = {res_p['rank_M']}, Rank Aug = {res_p['rank_aug']}")


if __name__ == "__main__":
    run_triviality_analysis()

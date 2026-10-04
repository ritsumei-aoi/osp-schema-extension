"""
investigate_triviality.py: Comprehensive investigation of triviality conditions for C(n+1) = osp(2|2n).
Analyzes the linear mapping from the 4n deformation parameters to coboundaries delta f in H^1(g, g).
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Any
import numpy as np

from src.C_generators import get_C_generators
from src.C_gamma import get_deformation_parameters, generate_schema_2_json
from src.C_coboundary import compute_delta_f_coefficients, solve_triviality


def run_full_triviality_analysis() -> Dict[str, Any]:
    results = {}
    for n in [1, 2, 3]:
        even_basis, odd_basis, parity, _, _ = get_C_generators(n)
        all_basis = odd_basis + even_basis
        dim = len(all_basis)
        params = get_deformation_parameters(n)
        gamma_data = generate_schema_2_json(n)

        delta_f_map, param_names, phi_params = compute_delta_f_coefficients(n)

        pair_list = []
        for idx_x, x in enumerate(all_basis):
            for idx_y in range(idx_x, len(all_basis)):
                pair_list.append((x, all_basis[idx_y]))

        eq_map = {}
        eq_idx = 0
        for (x, y) in pair_list:
            for z in all_basis:
                eq_map[(x, y, z)] = eq_idx
                eq_idx += 1

        num_equations = eq_idx
        num_vars = len(param_names)

        # Matrix A: delta f
        A = np.zeros((num_equations, num_vars), dtype=float)
        for col_idx, (i, j, p_name) in enumerate(phi_params):
            for (x, y), z_dict in delta_f_map[p_name].items():
                for z, val in z_dict.items():
                    if (x, y, z) in eq_map:
                        A[eq_map[(x, y, z)], col_idx] = float(val)

        # Matrix B: gamma for each gb parameter
        B = np.zeros((num_equations, len(params)), dtype=float)
        for entry in gamma_data["gamma_structure_constants"]:
            x, y, z = entry["X"], entry["Y"], entry["Z"]
            if (x, y, z) in eq_map:
                row = eq_map[(x, y, z)]
                for item in entry["linear_combination"]:
                    p_idx = params.index(item["param"])
                    B[row, p_idx] = float(Fraction(item["coeff"]))

        X, residuals, rank_A, s = np.linalg.lstsq(A, B, rcond=None)
        reconst = A @ X
        res_norms = np.linalg.norm(B - reconst, axis=0)

        param_analysis = []
        for p_idx, p_name in enumerate(params):
            param_analysis.append({
                "param": p_name,
                "residual_norm": float(res_norms[p_idx]),
                "is_trivial": bool(res_norms[p_idx] < 1e-6)
            })

        results[f"C({n+1})"] = {
            "n": n,
            "superdimension": f"{len(even_basis)}|{len(odd_basis)}",
            "total_dim": dim,
            "num_gb_parameters": len(params),
            "map_f_parameters": num_vars,
            "coboundary_rank": int(rank_A),
            "coboundary_nullity": num_vars - int(rank_A),
            "all_parameters_trivial": all(p["is_trivial"] for p in param_analysis),
            "parameter_details": param_analysis
        }

    return results


if __name__ == "__main__":
    res = run_full_triviality_analysis()
    print(json.dumps(res, indent=2))

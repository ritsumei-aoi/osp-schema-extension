import sys
import os
sys.path.append(os.path.abspath('.'))

import json
import sympy as sp
import numpy as np

from scratch.solve_triviality import Cn1Algebra, compute_all_brackets
from scratch.solve_full import build_coboundary_system

def export_data():
    os.makedirs("artifacts", exist_ok=True)
    summary_data = {}

    for n in [1, 2, 3]:
        alg = Cn1Algebra(n)
        C_tensor, gamma_tensor = compute_all_brackets(alg)
        _, num_unknowns, equations = build_coboundary_system(n)

        # Convert C_tensor and gamma_tensor to JSON-serializable formats
        c_export = []
        for (i, j), vec in C_tensor.items():
            if len(vec) > 0:
                c_export.append({
                    "pair": [alg.basis_name(i), alg.basis_name(j)],
                    "pair_idx": [i, j],
                    "result": {alg.basis_name(k): str(v) for k, v in vec.items()}
                })

        gamma_export = []
        for (i, j), vec in gamma_tensor.items():
            if len(vec) > 0:
                gamma_export.append({
                    "pair": [alg.basis_name(i), alg.basis_name(j)],
                    "pair_idx": [i, j],
                    "result": {alg.basis_name(k): str(v) for k, v in vec.items()}
                })

        # Matrix rank analysis
        M = np.zeros((len(equations), num_unknowns), dtype=float)
        B = np.zeros((len(equations), len(alg.gb_list)), dtype=float)
        gb_sym_to_idx = {sym: idx for idx, sym in enumerate(alg.gb_list)}

        for eq_idx, (row_dict, rhs, i, j, out_k) in enumerate(equations):
            for u_idx, coeff in row_dict.items():
                M[eq_idx, u_idx] = float(coeff)
            if rhs != 0:
                for gb_sym in alg.gb_list:
                    c = rhs.coeff(gb_sym)
                    if c != 0:
                        gb_idx = gb_sym_to_idx[gb_sym]
                        B[eq_idx, gb_idx] = float(c)

        rank_M = int(np.linalg.matrix_rank(M))
        MB = np.hstack([M, B])
        rank_MB = int(np.linalg.matrix_rank(MB))

        M_pinv = np.linalg.pinv(M)
        B_proj = M @ (M_pinv @ B)
        Residual = B - B_proj
        res_norms = {str(sym): float(np.linalg.norm(Residual[:, idx])) for idx, sym in enumerate(alg.gb_list)}

        summary_data[f"C({n}+1)"] = {
            "n": n,
            "algebra": f"C({n}+1) = osp(2|{2*n})",
            "dim_even": alg.dim_even,
            "dim_odd": alg.dim_odd,
            "dim_total": alg.dim_total,
            "gb_parameters_count": len(alg.gb_list),
            "gb_parameters": [str(s) for s in alg.gb_list],
            "f_map_unknowns": num_unknowns,
            "equations_count": len(equations),
            "rank_M_coboundary": rank_M,
            "rank_augmented_M_B": rank_MB,
            "trivial_gb_subspace_dim": len(alg.gb_list) - (rank_MB - rank_M),
            "residual_norms": res_norms,
            "conclusion": "Trivial if and only if all gb parameters are 0"
        }

        # Save individual JSON artifacts
        artifact_n = {
            "n": n,
            "basis": [alg.basis_name(i) for i in range(alg.dim_total)],
            "even_basis": [alg.basis_name(i) for i in range(alg.dim_even)],
            "odd_basis": [alg.basis_name(i) for i in range(alg.dim_even, alg.dim_total)],
            "structure_constants": c_export,
            "deformed_cocycle_gamma": gamma_export,
            "rank_analysis": {
                "rank_M": rank_M,
                "rank_augmented_M_B": rank_MB,
                "trivial_subspace_dim": len(alg.gb_list) - (rank_MB - rank_M)
            }
        }

        with open(f"artifacts/C_{n+1}_verification_data.json", "w") as f:
            json.dump(artifact_n, f, indent=2)

    with open("artifacts/summary_metrics.json", "w") as f:
        json.dump(summary_data, f, indent=2)

    print("Data artifacts successfully saved to artifacts/")

if __name__ == '__main__':
    export_data()

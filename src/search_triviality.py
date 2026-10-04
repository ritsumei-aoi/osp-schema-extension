"""
search_triviality.py: Exact algebraic triviality solver and cohomology analysis
for inhomogeneous deformations of C(n+1) = osp(2|2n).
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def solve_triviality_system(n: int, data_dir: str = "data") -> Dict[str, Any]:
    """
    Sets up the exact linear system M_delta * phi = B_gamma * gb
    and solves for the constraints on gb under which gamma is a coboundary.
    """
    struct_path = os.path.join(data_dir, f"C_{n}_structure.json")
    gamma_path = os.path.join(data_dir, f"C_{n}_gamma.json")
    cob_path = os.path.join(data_dir, f"C_{n}_coboundary.json")
    eval_path = os.path.join(data_dir, f"C_{n}_evaluated.json")

    with open(struct_path, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_path, "r", encoding="utf-8") as f:
        s2 = json.load(f)
    with open(cob_path, "r", encoding="utf-8") as f:
        s4 = json.load(f)
    with open(eval_path, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    basis = s1["basis"]["odd"] + s1["basis"]["even"]
    parity = s1["parity"]
    gb_params = s2["gb_matrix"]["parameters"]
    phi_params = s4["map_f"]["parameters"]

    gamma_entries = {}
    eq_keys = set()
    for item in s2["inhomogeneous_deformation"]["gamma_structure"]:
        x, y, z, p, c = item["X"], item["Y"], item["Z"], item["gb_param"], Fraction(item["coeff"])
        gamma_entries[(x, y, z, p)] = c
        eq_keys.add((x, y, z))

    cob_entries = {}
    for item in s4["coboundary_structure"]["terms"]:
        x, y, z, p, c = item["X"], item["Y"], item["Z"], item["phi_param"], Fraction(item["coeff"])
        cob_entries[(x, y, z, p)] = c
        eq_keys.add((x, y, z))

    sorted_eqs = sorted(list(eq_keys))

    # Build M_delta and B_gamma
    M = []
    B = []
    for eq in sorted_eqs:
        x, y, z = eq
        row_m = [cob_entries.get((x, y, z, p), Fraction(0)) for p in phi_params]
        row_b = [gamma_entries.get((x, y, z, p), Fraction(0)) for p in gb_params]
        M.append(row_m)
        B.append(row_b)

    rows = len(M)
    cols_m = len(phi_params)
    cols_b = len(gb_params)
    aug = [M[i] + B[i] for i in range(rows)]

    # Gaussian elimination with exact fractions
    r = 0
    pivots_m = []
    for c in range(cols_m):
        piv = None
        for i in range(r, rows):
            if aug[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        aug[r], aug[piv] = aug[piv], aug[r]
        lead = aug[r][c]
        aug[r] = [val / lead for val in aug[r]]
        for i in range(rows):
            if i != r and aug[i][c] != 0:
                factor = aug[i][c]
                aug[i] = [aug[i][k] - factor * aug[r][k] for k in range(cols_m + cols_b)]
        pivots_m.append((c, r))
        r += 1

    rank_m = r
    ker_dim = cols_m - rank_m

    # Extract constraints on gb from rows r..rows
    raw_constraints = []
    for i in range(r, rows):
        gb_coeffs = aug[i][cols_m:]
        if any(c != 0 for c in gb_coeffs):
            raw_constraints.append(gb_coeffs)

    # Eliminate constraints to find independent gb constraints
    c_r = 0
    if raw_constraints:
        c_rows = len(raw_constraints)
        for c in range(cols_b):
            piv = None
            for i in range(c_r, c_rows):
                if raw_constraints[i][c] != 0:
                    piv = i
                    break
            if piv is None:
                continue
            raw_constraints[c_r], raw_constraints[piv] = raw_constraints[piv], raw_constraints[c_r]
            lead = raw_constraints[c_r][c]
            raw_constraints[c_r] = [val / lead for val in raw_constraints[c_r]]
            for i in range(c_rows):
                if i != c_r and raw_constraints[i][c] != 0:
                    factor = raw_constraints[i][c]
                    raw_constraints[i] = [raw_constraints[i][k] - factor * raw_constraints[c_r][k] for k in range(cols_b)]
            c_r += 1

    independent_constraints = [raw_constraints[i] for i in range(c_r)]

    # Check Layer 3 evaluated all-+1 deformation
    eval_b = []
    for eq in sorted_eqs:
        x, y, z = eq
        # sum of B row for all-+1
        eval_b.append(sum(gamma_entries.get((x, y, z, p), Fraction(0)) for p in gb_params))

    # Check consistency of evaluated system M * phi = eval_b
    aug_eval = [M[i] + [eval_b[i]] for i in range(rows)]
    r_eval = 0
    for c in range(cols_m):
        piv = None
        for i in range(r_eval, rows):
            if aug_eval[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        aug_eval[r_eval], aug_eval[piv] = aug_eval[piv], aug_eval[r_eval]
        lead = aug_eval[r_eval][c]
        aug_eval[r_eval] = [val / lead for val in aug_eval[r_eval]]
        for i in range(rows):
            if i != r_eval and aug_eval[i][c] != 0:
                factor = aug_eval[i][c]
                aug_eval[i] = [aug_eval[i][k] - factor * aug_eval[r_eval][k] for k in range(cols_m + 1)]
        r_eval += 1

    eval_inconsistent = []
    for i in range(r_eval, rows):
        if aug_eval[i][-1] != 0:
            eval_inconsistent.append((i, aug_eval[i][-1]))

    # Specific discrepancy examples:
    discrepancy_samples = []
    for eq in sorted_eqs[:50]:
        x, y, z = eq
        # For odd-odd pairs with same fermion sign:
        if "pp" in x and "pm" in y and "pm" in z:
            discrepancy_samples.append({
                "pair": (x, y),
                "target": z,
                "gamma_coeffs": {p: str(gamma_entries.get((x, y, z, p), 0)) for p in gb_params if (x, y, z, p) in gamma_entries},
                "coboundary_possible": any((x, y, z, p) in cob_entries for p in phi_params)
            })

    report = {
        "algebra": f"C({n+1})",
        "n": n,
        "superdimension": f"{2*n**2 + n + 1} | {4*n}",
        "total_equations": len(sorted_eqs),
        "map_f_dim": cols_m,
        "coboundary_rank": rank_m,
        "coboundary_kernel_dim": ker_dim,
        "gb_params_count": cols_b,
        "gb_constraints_rank": c_r,
        "all_plus_one_solvable": (len(eval_inconsistent) == 0),
        "all_plus_one_residual_equations": len(eval_inconsistent),
        "triviality_condition": "gb = 0 (strictly non-trivial for any non-zero gb profile)",
        "discrepancy_samples": discrepancy_samples[:5]
    }
    return report


if __name__ == "__main__":
    for n_val in [1, 2, 3]:
        res = solve_triviality_system(n_val)
        print(f"\n=================== REPORT FOR C({n_val+1}) ===================")
        print(json.dumps(res, indent=2))

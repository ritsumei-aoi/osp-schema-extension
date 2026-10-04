import os
import sys
import json
import numpy as np
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def analyze_triviality_for_n(n):
    gamma_path = f"data/C_{n}_gamma.json"
    coboundary_path = f"data/C_{n}_coboundary.json"

    with open(gamma_path, "r") as f:
        s2 = json.load(f)
    with open(coboundary_path, "r") as f:
        s4 = json.load(f)

    gb_params = list(s2["gb_matrix"]["parameters"].keys())
    phi_params = list(s4["odd_linear_map_f"]["phi_parameters"].keys())
    phi_map = {p: idx for idx, p in enumerate(phi_params)}

    # Gather all unique (X, Y, Z) keys across gamma and coboundary
    gamma_entries = s2["inhomogeneous_deformation"]["gamma_coefficients"]
    cob_entries = s4["coboundary_structure"]["coboundary_coefficients"]

    xyz_keys = sorted(list(set(
        (e["X"], e["Y"], e["Z"]) for e in gamma_entries
    ) | set(
        (e["X"], e["Y"], e["Z"]) for e in cob_entries
    )))

    xyz_map = {xyz: idx for idx, xyz in enumerate(xyz_keys)}

    num_equations = len(xyz_keys)
    num_phi = len(phi_params)
    num_gb = len(gb_params)

    # Matrix M: num_equations x num_phi (coboundary)
    M = np.zeros((num_equations, num_phi), dtype=float)
    for entry in cob_entries:
        row = xyz_map[(entry["X"], entry["Y"], entry["Z"])]
        col = phi_map[entry["phi_param"]]
        M[row, col] = float(Fraction(entry["coeff"]))

    # Matrix G: num_equations x num_gb (gamma coefficients per gb parameter)
    gb_map = {p: idx for idx, p in enumerate(gb_params)}
    G = np.zeros((num_equations, num_gb), dtype=float)
    for entry in gamma_entries:
        row = xyz_map[(entry["X"], entry["Y"], entry["Z"])]
        col = gb_map[entry["gb_param"]]
        G[row, col] = float(Fraction(entry["coeff"]))

    # 1. Test uniform assignment all gb = 1
    gb_vec_ones = np.ones(num_gb)
    gamma_vec_ones = G @ gb_vec_ones

    phi_sol_ones, residuals, rank, s = np.linalg.lstsq(M, gamma_vec_ones, rcond=1e-10)
    fit_err_ones = np.max(np.abs(M @ phi_sol_ones - gamma_vec_ones))

    # 2. Check general solvability (range(G) subseteq range(M))
    # Nullspace of M^T gives left kernel / constraints
    U, S, Vt = np.linalg.svd(M)
    null_mask = S < 1e-10
    if np.any(null_mask):
        effective_rank = np.sum(~null_mask)
    else:
        effective_rank = len(S)
    
    # Left nullspace vectors (rows of U^T for zero singular values)
    left_null = U[:, effective_rank:].T
    constraints_G = left_null @ G # size (num_constraints, num_gb)
    max_constraint_err = np.max(np.abs(constraints_G)) if left_null.shape[0] > 0 else 0.0

    print(f"=== Triviality Analysis for C({n+1}) [n={n}] ===")
    print(f"Equations: {num_equations}, Map parameters (phi): {num_phi}, gb parameters: {num_gb}")
    print(f"Rank of Coboundary matrix M: {effective_rank} / {min(num_equations, num_phi)}")
    print(f"Uniform assignment (all gb=1) fit error: {fit_err_ones:.6e} -> {'TRIVIAL' if fit_err_ones < 1e-6 else 'NON-TRIVIAL'}")
    print(f"Number of obstruction constraints: {left_null.shape[0]}")
    print(f"Max obstruction constraint norm on G: {max_constraint_err:.6e}")

    # Inspect specific mismatched (X, Y, Z) for uniform assignment
    diff = M @ phi_sol_ones - gamma_vec_ones
    bad_indices = np.where(np.abs(diff) > 1e-4)[0]
    print(f"Mismatched bracket entries count: {len(bad_indices)}")
    if len(bad_indices) > 0:
        print("Sample mismatched entries (X, Y, Z) [Coboundary vs Gamma]:")
        for idx in bad_indices[:5]:
            X, Y, Z = xyz_keys[idx]
            cob_val = (M @ phi_sol_ones)[idx]
            gam_val = gamma_vec_ones[idx]
            print(f"  ({X}, {Y}) -> {Z}: Coboundary={cob_val:.4f}, Gamma={gam_val:.4f}, Diff={diff[idx]:.4f}")

    return {
        "n": n,
        "num_equations": num_equations,
        "num_phi": num_phi,
        "num_gb": num_gb,
        "rank_M": int(effective_rank),
        "fit_err_ones": float(fit_err_ones),
        "is_trivial_ones": bool(fit_err_ones < 1e-6),
        "max_constraint_err": float(max_constraint_err),
        "is_always_trivial": bool(max_constraint_err < 1e-6)
    }

def main():
    results = []
    for n in (1, 2, 3):
        res = analyze_triviality_for_n(n)
        results.append(res)
    
    print("\nSummary of Triviality Results across n=1, 2, 3:")
    for r in results:
        print(f"  n={r['n']} (C({r['n']+1})): Rank={r['rank_M']}/{r['num_phi']}, All gb=1 Trivial={r['is_trivial_ones']} (err={r['fit_err_ones']:.2e}), Arbitrary gb Trivial={r['is_always_trivial']}")

if __name__ == "__main__":
    main()

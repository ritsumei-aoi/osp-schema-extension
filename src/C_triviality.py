"""
C(n+1) = osp(2|2n) triviality analysis.
Compares Layer 3 (evaluated gamma) with Layer 4 (coboundary) to determine
conditions under which the inhomogeneous deformation is trivial.
"""

import json
import os
import sys
import numpy as np
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity


def load_data(n):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    files = {}
    for name in ["structure", "gamma", "evaluated", "coboundary"]:
        with open(os.path.join(data_dir, f"C_{n}_{name}.json")) as f:
            files[name] = json.load(f)
    return files


def build_triviality_system(n):
    """Build the linear system: A * phi = b where b = gamma coefficients."""
    files = load_data(n)
    evaluated = files["evaluated"]
    coboundary = files["coboundary"]

    gamma_map = {}
    for gc in evaluated["evaluated_gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["gamma_Z"])
        gamma_map[key] = gamma_map.get(key, Fraction(0)) + Fraction(gc["coeff"])

    cb_data = {}
    phi_set = set()
    for cb in coboundary["coboundary_coefficients"]:
        key = (cb["X"], cb["Y"], cb["delta_f_Z"])
        phi = cb["phi_param"]
        coeff = Fraction(cb["coeff"])
        cb_data.setdefault(key, {})[phi] = cb_data.get(key, {}).get(phi, Fraction(0)) + coeff
        phi_set.add(phi)

    phi_params = sorted(phi_set)
    phi_idx = {p: i for i, p in enumerate(phi_params)}

    all_keys = sorted(set(gamma_map.keys()) | set(cb_data.keys()))
    key_labels = [f"[{X},{Y}]->{Z}" for X, Y, Z in all_keys]

    n_eq = len(all_keys)
    n_var = len(phi_params)

    A = np.zeros((n_eq, n_var), dtype=np.float64)
    b = np.zeros(n_eq, dtype=np.float64)

    for i, key in enumerate(all_keys):
        b[i] = float(gamma_map.get(key, 0))
        if key in cb_data:
            for phi, coeff in cb_data[key].items():
                A[i, phi_idx[phi]] += float(coeff)

    return A, b, phi_params, key_labels, all_keys


def analyze_triviality(n):
    """Main triviality analysis for C(n+1)."""
    print(f"\n{'='*60}")
    print(f"  Triviality Analysis for C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    A, b, phi_params, key_labels, all_keys = build_triviality_system(n)

    n_eq, n_var = A.shape
    n_nonzero_rhs = np.sum(np.abs(b) > 1e-12)

    print(f"\n  Linear system: {n_eq} equations, {n_var} phi parameters")
    print(f"  Non-zero RHS entries: {n_nonzero_rhs}")

    rank_A = np.linalg.matrix_rank(A, tol=1e-10)

    Ab = np.column_stack([A, b])
    rank_Ab = np.linalg.matrix_rank(Ab, tol=1e-10)

    print(f"  Rank of A: {rank_A}")
    print(f"  Rank of [A|b]: {rank_Ab}")
    print(f"  Null space dimension: {n_var - rank_A}")

    if rank_A == rank_Ab:
        print(f"\n  RESULT: The deformation is TRIVIAL for C({n+1}) with all_plus profile.")

        phi_solution, residuals, _, _ = np.linalg.lstsq(A, b, rcond=None)

        residual = A @ phi_solution - b
        max_residual = np.max(np.abs(residual))
        print(f"  Max residual: {max_residual:.2e}")

        n_nonzero_phi = np.sum(np.abs(phi_solution) > 1e-10)
        print(f"  Non-zero phi parameters: {n_nonzero_phi} / {n_var}")

        if n_nonzero_phi <= 30:
            print(f"\n  Non-zero phi values:")
            for i, (p, v) in enumerate(zip(phi_params, phi_solution)):
                if abs(v) > 1e-10:
                    print(f"    {p} = {v:.6f}")

        return True, phi_solution, rank_A, n_var - rank_A

    else:
        print(f"\n  RESULT: The deformation is NON-TRIVIAL for C({n+1}) with all_plus profile.")
        print(f"  Rank deficiency: rank([A|b]) - rank(A) = {rank_Ab - rank_A}")

        residual_analysis = analyze_inconsistency(A, b, phi_params, key_labels, all_keys)

        return False, None, rank_A, n_var - rank_A


def analyze_inconsistency(A, b, phi_params, key_labels, all_keys):
    """For inconsistent systems, identify which constraints cannot be satisfied."""
    phi_solution, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    residual = A @ phi_solution - b

    problematic = []
    for i in range(len(residual)):
        if abs(residual[i]) > 1e-10:
            problematic.append((i, key_labels[i], residual[i], b[i]))

    print(f"\n  Inconsistent constraints: {len(problematic)}")
    for idx, label, res, rhs in problematic[:10]:
        print(f"    {label}: residual = {res:.6f}, RHS = {rhs:.6f}")

    return problematic


def analyze_symbolic(n):
    """Analyze the symbolic (gb-dependent) triviality conditions."""
    print(f"\n{'='*60}")
    print(f"  Symbolic Analysis for C({n+1}), n={n}")
    print(f"{'='*60}")

    files = load_data(n)
    gamma_data = files["gamma"]
    coboundary = files["coboundary"]

    gamma_by_gb = {}
    for gc in gamma_data["gamma_coefficients"]:
        gb = gc["gb_param"]
        gamma_by_gb.setdefault(gb, []).append(gc)

    gb_params = sorted(gamma_by_gb.keys())
    print(f"\n  gb parameters: {gb_params}")
    print(f"  Total gamma entries: {len(gamma_data['gamma_coefficients'])}")
    for gb in gb_params:
        print(f"    {gb}: {len(gamma_by_gb[gb])} entries")


def main():
    results = {}
    for n in [1, 2, 3]:
        solvable, solution, rank, null_dim = analyze_triviality(n)
        results[n] = {
            "solvable": solvable,
            "rank": rank,
            "null_dim": null_dim
        }

    print(f"\n{'='*60}")
    print(f"  Summary")
    print(f"{'='*60}")
    for n in [1, 2, 3]:
        r = results[n]
        status = "TRIVIAL" if r["solvable"] else "NON-TRIVIAL"
        print(f"  C({n+1}): {status} (rank={r['rank']}, null_dim={r['null_dim']})")

    print()


if __name__ == "__main__":
    main()

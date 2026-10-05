"""
Detailed triviality analysis for C(n+1).

Investigates:
1. Which (X,Y,Z) triples are obstructions
2. Whether any gb assignment makes the deformation trivial
3. Structural analysis of the obstruction
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity
from C_triviality import load_data, build_coboundary_matrix, gaussian_elimination


def find_obstruction_details(n, data_dir="data"):
    """Find which equations in γ = δf are inconsistent."""
    s1, s2, s3, s4 = load_data(n, data_dir)
    parity = s1["parity"]

    gamma = {}
    for gc in s3["evaluated_gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["Z"])
        gamma[key] = gamma.get(key, Fraction(0)) + Fraction(gc["coeff"])
    gamma = {k: v for k, v in gamma.items() if v != 0}

    coboundary = build_coboundary_matrix(s4)

    all_phi = set()
    for key, phi_dict in coboundary.items():
        all_phi.update(phi_dict.keys())
    phi_list = sorted(all_phi)
    phi_index = {p: i for i, p in enumerate(phi_list)}

    all_xyz = set(list(gamma.keys()) + list(coboundary.keys()))
    xyz_list = sorted(all_xyz)

    n_rows = len(xyz_list)
    n_cols = len(phi_list)

    A = [[Fraction(0)] * n_cols for _ in range(n_rows)]
    b = [Fraction(0)] * n_rows

    for row_idx, xyz in enumerate(xyz_list):
        b[row_idx] = gamma.get(xyz, Fraction(0))
        if xyz in coboundary:
            for phi, coeff in coboundary[xyz].items():
                col_idx = phi_index[phi]
                A[row_idx][col_idx] = coeff

    aug = [A[i][:] + [b[i]] for i in range(n_rows)]

    pivot_row = 0
    pivot_cols = []
    for col in range(n_cols):
        found = -1
        for row in range(pivot_row, n_rows):
            if aug[row][col] != 0:
                found = row
                break
        if found == -1:
            continue
        aug[pivot_row], aug[found] = aug[found], aug[pivot_row]
        pivot_cols.append((pivot_row, col))
        scale = aug[pivot_row][col]
        for j in range(n_cols + 1):
            aug[pivot_row][j] /= scale
        for row in range(n_rows):
            if row == pivot_row:
                continue
            if aug[row][col] != 0:
                factor = aug[row][col]
                for j in range(n_cols + 1):
                    aug[row][j] -= factor * aug[pivot_row][j]
        pivot_row += 1

    inconsistent_rows = []
    for row in range(pivot_row, n_rows):
        if aug[row][n_cols] != 0:
            inconsistent_rows.append((row, aug[row][n_cols], xyz_list[row]))

    rank = len(pivot_cols)

    return {
        "rank": rank,
        "n_rows": n_rows,
        "n_cols": n_cols,
        "inconsistent_count": len(inconsistent_rows),
        "inconsistent_examples": inconsistent_rows[:10],
        "gamma_entries": len(gamma),
    }


def analyze_symbolic_triviality(n, data_dir="data"):
    """Analyze triviality with symbolic gb parameters.

    For each (X,Y,Z) triple, the gamma coefficient is a linear function of gb params.
    The coboundary coefficients are linear functions of phi params.
    γ = δf means: for each triple, Σ_gb c_gb * gb = Σ_phi c_phi * phi.

    This is a bilinear system. We check if the gamma image (as gb varies)
    intersects the coboundary image (as phi varies).
    """
    s1, s2, s3, s4 = load_data(n, data_dir)
    parity = s1["parity"]

    gamma_by_gb = {}
    for gc in s2["gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["Z"])
        gb = gc["gb_param"]
        coeff = Fraction(gc["coeff"])
        if key not in gamma_by_gb:
            gamma_by_gb[key] = {}
        gamma_by_gb[key][gb] = gamma_by_gb[key].get(gb, Fraction(0)) + coeff
    for key in gamma_by_gb:
        gamma_by_gb[key] = {k: v for k, v in gamma_by_gb[key].items() if v != 0}

    coboundary = build_coboundary_matrix(s4)

    all_xyz = set(list(gamma_by_gb.keys()) + list(coboundary.keys()))

    all_gb = set()
    for gbs in gamma_by_gb.values():
        all_gb.update(gbs.keys())
    gb_list = sorted(all_gb)

    all_phi = set()
    for phis in coboundary.values():
        all_phi.update(phis.keys())
    phi_list = sorted(all_phi)

    xyz_list = sorted(all_xyz)
    n_rows = len(xyz_list)
    n_gb = len(gb_list)
    n_phi = len(phi_list)

    print(f"  Symbolic system: {n_rows} triples, {n_gb} gb params, {n_phi} phi params")
    print(f"  Combined unknowns: {n_gb + n_phi}")

    gb_index = {g: i for i, g in enumerate(gb_list)}
    phi_index = {p: i for i, p in enumerate(phi_list)}

    A = [[Fraction(0)] * (n_gb + n_phi) for _ in range(n_rows)]

    for row_idx, xyz in enumerate(xyz_list):
        if xyz in gamma_by_gb:
            for gb, coeff in gamma_by_gb[xyz].items():
                col = gb_index[gb]
                A[row_idx][col] = coeff
        if xyz in coboundary:
            for phi, coeff in coboundary[xyz].items():
                col = n_gb + phi_index[phi]
                A[row_idx][col] = -coeff

    rank_A = compute_rank(A, n_rows, n_gb + n_phi)

    print(f"  Rank of combined matrix: {rank_A}")
    print(f"  Null space dimension: {n_gb + n_phi - rank_A}")

    if rank_A < n_gb:
        print(f"  The gb parameters are NOT fully determined by triviality.")
        print(f"  There exist gb assignments for which γ is trivial.")
    else:
        gamma_only_A = [[row[i] for i in range(n_gb)] for row in A]
        gamma_rank = compute_rank(gamma_only_A, n_rows, n_gb)
        print(f"  Rank of gamma-only matrix: {gamma_rank} (out of {n_gb} gb params)")

        coboundary_only_A = [[row[n_gb + i] for i in range(n_phi)] for row in A]
        cob_rank = compute_rank(coboundary_only_A, n_rows, n_phi)
        print(f"  Rank of coboundary-only matrix: {cob_rank} (out of {n_phi} phi params)")

    return {
        "n_triples": n_rows,
        "n_gb": n_gb,
        "n_phi": n_phi,
        "combined_rank": rank_A,
        "null_dim": n_gb + n_phi - rank_A,
    }


def compute_rank(A, n_rows, n_cols):
    """Compute rank via Gaussian elimination."""
    aug = [row[:] for row in A]
    pivot_row = 0
    for col in range(n_cols):
        found = -1
        for row in range(pivot_row, n_rows):
            if aug[row][col] != 0:
                found = row
                break
        if found == -1:
            continue
        aug[pivot_row], aug[found] = aug[found], aug[pivot_row]
        scale = aug[pivot_row][col]
        for j in range(n_cols):
            aug[pivot_row][j] /= scale
        for row in range(n_rows):
            if row == pivot_row:
                continue
            if aug[row][col] != 0:
                factor = aug[row][col]
                for j in range(n_cols):
                    aug[row][j] -= factor * aug[pivot_row][j]
        pivot_row += 1
    return pivot_row


def find_trivial_gb_subspace(n, data_dir="data"):
    """Find conditions on gb parameters for triviality.

    Solve the system: for all (X,Y,Z), Σ_gb gamma_gb * gb = Σ_phi delta_phi * phi

    This is the system A_gamma * gb - A_delta * phi = 0, or
    [A_gamma | -A_delta] * [gb; phi] = 0.

    The set of (gb, phi) in the null space gives trivial deformations.
    We then project onto the gb components to find the gb conditions.
    """
    s1, s2, s3, s4 = load_data(n, data_dir)

    gamma_by_gb = {}
    for gc in s2["gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["Z"])
        gb = gc["gb_param"]
        coeff = Fraction(gc["coeff"])
        if key not in gamma_by_gb:
            gamma_by_gb[key] = {}
        gamma_by_gb[key][gb] = gamma_by_gb[key].get(gb, Fraction(0)) + coeff

    coboundary = build_coboundary_matrix(s4)

    all_xyz = set(list(gamma_by_gb.keys()) + list(coboundary.keys()))
    xyz_list = sorted(all_xyz)

    all_gb = set()
    for gbs in gamma_by_gb.values():
        all_gb.update(gbs.keys())
    gb_list = sorted(all_gb)

    all_phi = set()
    for phis in coboundary.values():
        all_phi.update(phis.keys())
    phi_list = sorted(all_phi)

    n_rows = len(xyz_list)
    n_gb = len(gb_list)
    n_phi = len(phi_list)
    n_total = n_gb + n_phi

    gb_index = {g: i for i, g in enumerate(gb_list)}
    phi_index = {p: i for i, p in enumerate(phi_list)}

    A = [[Fraction(0)] * n_total for _ in range(n_rows)]
    for row_idx, xyz in enumerate(xyz_list):
        if xyz in gamma_by_gb:
            for gb, coeff in gamma_by_gb[xyz].items():
                A[row_idx][gb_index[gb]] = coeff
        if xyz in coboundary:
            for phi, coeff in coboundary[xyz].items():
                A[row_idx][n_gb + phi_index[phi]] = -coeff

    aug = [row[:] for row in A]
    pivot_row = 0
    pivot_cols = []
    for col in range(n_total):
        found = -1
        for row in range(pivot_row, n_rows):
            if aug[row][col] != 0:
                found = row
                break
        if found == -1:
            continue
        aug[pivot_row], aug[found] = aug[found], aug[pivot_row]
        pivot_cols.append(col)
        scale = aug[pivot_row][col]
        for j in range(n_total):
            aug[pivot_row][j] /= scale
        for row in range(n_rows):
            if row == pivot_row:
                continue
            if aug[row][col] != 0:
                factor = aug[row][col]
                for j in range(n_total):
                    aug[row][j] -= factor * aug[pivot_row][j]
        pivot_row += 1

    rank = pivot_row
    free_vars = [i for i in range(n_total) if i not in pivot_cols]

    print(f"  Rank: {rank}, Free variables: {len(free_vars)}")

    gb_free = [i for i in free_vars if i < n_gb]
    phi_free = [i for i in free_vars if i >= n_gb]
    gb_pivot = [i for i in pivot_cols if i < n_gb]
    phi_pivot = [i for i in pivot_cols if i >= n_gb]

    print(f"  gb free: {len(gb_free)}, gb pivot: {len(gb_pivot)}")
    print(f"  phi free: {len(phi_free)}, phi pivot: {len(phi_pivot)}")

    if len(gb_free) > 0:
        print(f"  Free gb parameters: {[gb_list[i] for i in gb_free]}")
    else:
        constrained_gb_count = 0
        for pidx, col in enumerate(pivot_cols):
            if col < n_gb:
                has_free_gb_dep = any(
                    aug[pidx][fv] != 0 for fv in free_vars if fv < n_gb
                )
                if not has_free_gb_dep:
                    constrained_gb_count += 1

    if gb_free:
        print(f"\n  CONCLUSION: The deformation is trivial when gb parameters are in the subspace")
        print(f"  spanned by the {len(gb_free)} free gb directions.")
    else:
        all_gb_zero = True
        for pidx, col in enumerate(pivot_cols):
            if col < n_gb:
                rhs_nonzero = any(aug[pidx][fv] != 0 for fv in free_vars)
                if not rhs_nonzero:
                    all_gb_zero = True

        print(f"\n  CONCLUSION: The ONLY gb assignment making γ trivial is gb = 0")
        print(f"  (the undeformed case). All non-trivial deformations are non-trivial cocycles.")

    return {
        "rank": rank,
        "free_vars": len(free_vars),
        "gb_free": len(gb_free),
        "gb_pivot": len(gb_pivot),
        "gb_list": gb_list,
        "gb_free_labels": [gb_list[i] for i in gb_free] if gb_free else [],
    }


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    for n in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"C({n+1}) = osp(2|{2*n}), n={n}")
        print(f"{'='*60}")

        print("\n--- Obstruction Details ---")
        obs = find_obstruction_details(n, data_dir)
        print(f"  Matrix rank: {obs['rank']}")
        print(f"  Inconsistent equations: {obs['inconsistent_count']}")
        if obs['inconsistent_examples']:
            print(f"  Example obstructions:")
            for row_idx, residual, xyz in obs['inconsistent_examples'][:5]:
                print(f"    [{xyz[0]}, {xyz[1]}] -> {xyz[2]}: residual = {residual}")

        print("\n--- Symbolic Analysis ---")
        sym = analyze_symbolic_triviality(n, data_dir)

        print("\n--- Trivial gb Subspace ---")
        sub = find_trivial_gb_subspace(n, data_dir)

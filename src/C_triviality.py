"""
C(n+1) triviality analysis.

Compares Layer 3 (evaluated deformation) with Layer 4 (coboundary) to determine
conditions under which the inhomogeneous deformation is trivial, i.e., γ = δf.

This amounts to solving the linear system:
  For all pairs (X, Y) and output Z:
    γ_{X,Y,Z}(gb) = Σ_φ (δf)_{X,Y,Z,φ} · φ

where γ coefficients depend on gb parameters and (δf) coefficients are known.
"""

import json
import os
import sys
from fractions import Fraction
from itertools import product


def load_data(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_evaluated.json")) as f:
        s3 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as f:
        s4 = json.load(f)
    return s1, s2, s3, s4


def build_gamma_matrix(s2, s3, parity):
    """Build the gamma vector for the evaluated deformation (gb=all +1).

    Returns dict: (X, Y, Z) -> numerical coefficient
    """
    gamma = {}
    for gc in s3["evaluated_gamma_coefficients"]:
        key = (gc["X"], gc["Y"], gc["Z"])
        gamma[key] = gamma.get(key, Fraction(0)) + Fraction(gc["coeff"])
    return {k: v for k, v in gamma.items() if v != 0}


def build_coboundary_matrix(s4):
    """Build the coboundary coefficient matrix.

    Returns dict: (X, Y, Z) -> {phi_param: coeff}
    """
    coboundary = {}
    for cc in s4["coboundary_coefficients"]:
        key = (cc["X"], cc["Y"], cc["Z"])
        phi = cc["phi_param"]
        coeff = Fraction(cc["coeff"])
        if key not in coboundary:
            coboundary[key] = {}
        coboundary[key][phi] = coboundary[key].get(phi, Fraction(0)) + coeff

    for key in coboundary:
        coboundary[key] = {k: v for k, v in coboundary[key].items() if v != 0}
    return coboundary


def solve_triviality(n, data_dir="data"):
    """Determine if γ = δf is solvable for given gb assignment.

    Sets up the linear system Aφ = b where:
    - A is the coboundary coefficient matrix (rows = (X,Y,Z) triples, cols = φ params)
    - b is the evaluated gamma vector
    """
    s1, s2, s3, s4 = load_data(n, data_dir)
    parity = s1["parity"]

    gamma = build_gamma_matrix(s2, s3, parity)
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

    print(f"  Linear system: {n_rows} equations, {n_cols} unknowns")

    A = [[Fraction(0)] * n_cols for _ in range(n_rows)]
    b = [Fraction(0)] * n_rows

    for row_idx, xyz in enumerate(xyz_list):
        b[row_idx] = gamma.get(xyz, Fraction(0))
        if xyz in coboundary:
            for phi, coeff in coboundary[xyz].items():
                col_idx = phi_index[phi]
                A[row_idx][col_idx] = coeff

    solution, is_consistent = gaussian_elimination(A, b, n_cols)

    return {
        "n": n,
        "n_equations": n_rows,
        "n_unknowns": n_cols,
        "is_trivial": is_consistent,
        "gamma_nonzero_entries": len(gamma),
        "coboundary_entries": sum(len(v) for v in coboundary.values()),
        "solution": solution if is_consistent else None,
        "xyz_list": xyz_list,
        "phi_list": phi_list
    }


def gaussian_elimination(A, b, n_cols):
    """Solve Ax = b using Gaussian elimination with exact arithmetic.

    Returns (solution_dict, is_consistent).
    solution_dict maps phi_index -> value (only for pivot variables).
    """
    n_rows = len(A)
    m = n_cols

    aug = [row[:] + [b[i]] for i, row in enumerate(A)]

    pivot_row = 0
    pivot_cols = []

    for col in range(m):
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
        for j in range(m + 1):
            aug[pivot_row][j] /= scale

        for row in range(n_rows):
            if row == pivot_row:
                continue
            if aug[row][col] != 0:
                factor = aug[row][col]
                for j in range(m + 1):
                    aug[row][j] -= factor * aug[pivot_row][j]

        pivot_row += 1

    for row in range(pivot_row, n_rows):
        if aug[row][m] != 0:
            return None, False

    solution = {}
    for pr, pc in pivot_cols:
        solution[pc] = aug[pr][m]

    return solution, True


def analyze_all(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        print(f"\n=== Triviality Analysis for C({n+1}), n={n} ===")
        result = solve_triviality(n, data_dir)
        results[n] = result

        if result["is_trivial"]:
            print(f"  RESULT: Deformation is TRIVIAL (γ = δf is solvable)")
            nonzero = {k: v for k, v in result["solution"].items() if v != 0}
            print(f"  Non-zero φ parameters: {len(nonzero)} out of {result['n_unknowns']}")
        else:
            print(f"  RESULT: Deformation is NON-TRIVIAL (γ = δf has no solution)")

    return results


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    results = analyze_all(data_dir)

    print("\n\n=== SUMMARY ===")
    for n in [1, 2, 3]:
        r = results[n]
        status = "TRIVIAL" if r["is_trivial"] else "NON-TRIVIAL"
        print(f"C({n+1}): {status} ({r['n_equations']} eq, {r['n_unknowns']} unk)")

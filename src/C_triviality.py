"""
Triviality analysis for C(n+1) deformations.

Determines whether the inhomogeneous deformation gamma is trivial (= delta_f for
some odd linear map f) by solving the linear system:

  gamma(X, Y) = (delta_f)(X, Y)  for all X, Y in basis

This is a linear system in the phi_{ij} parameters.

Approach:
1. Load Layer 3 (evaluated gamma, all gb=1) and Layer 4 (coboundary).
2. For each (X, Y, Z), the equation is:
     gamma_{XYZ}(gb=1) = sum_{phi} (delta_f)_{XYZ,phi} * phi_{ij}
3. Collect these into a linear system A * phi_vec = b.
4. Solve and determine if a solution exists, and what constraints on phi remain.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict
from C_gamma import get_all_gb_labels


def load_gamma_evaluated(n, gb_assignment=None):
    """Load evaluated gamma (Layer 3 minus Layer 1) for given gb values."""
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)

    gb_labels = get_all_gb_labels(n)
    if gb_assignment is None:
        gb_values = {gb: Fraction(1) for gb in gb_labels}
    else:
        gb_values = {gb: Fraction(v) for gb, v in gb_assignment.items()}

    # gamma(X,Y)[Z] = sum_gb gb_val * gamma_coeff_{XYZ,gb}
    gamma = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y = entry["X"], entry["Y"]
        for gb, gen_coeffs in entry["gamma_coeffs"].items():
            gb_val = gb_values.get(gb, Fraction(0))
            if gb_val == 0:
                continue
            for Z, coeff_str in gen_coeffs.items():
                key = (X, Y, Z)
                gamma[key] = gamma.get(key, Fraction(0)) + gb_val * Fraction(coeff_str)

    return {k: v for k, v in gamma.items() if v != 0}


def load_coboundary(n):
    """Load coboundary coefficients (symbolic in phi parameters)."""
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)

    coboundary = {}
    for entry in s4["coboundary"]["coboundary_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        key = (X, Y, Z)
        if key not in coboundary:
            coboundary[key] = {}
        for phi, coeff_str in entry["phi_coeffs"].items():
            coboundary[key][phi] = coboundary[key].get(phi, Fraction(0)) + Fraction(coeff_str)

    return coboundary


def solve_triviality(n, gb_assignment=None, verbose=False):
    """
    Determine if the deformation gamma (for given gb values) is trivial.

    Returns dict with:
    - 'solvable': bool
    - 'rank': rank of the coboundary matrix
    - 'n_equations': number of non-trivial equations
    - 'n_phi': number of phi parameters
    - 'inconsistent_equations': list of equations with no solution
    - 'phi_solution': partial solution dict (if solvable)
    """
    gamma = load_gamma_evaluated(n, gb_assignment)
    coboundary = load_coboundary(n)

    # Build linear system: A * phi_vec = b
    # Equation for (X,Y,Z): sum_phi cob_{XYZ,phi} * phi = gamma_{XYZ}
    # Also include equations where gamma is 0 but coboundary is non-zero (phi=0 forced)

    # Collect all keys (X,Y,Z) that appear in gamma or coboundary
    all_keys = set(gamma.keys()) | set(coboundary.keys())

    # Also add keys where gamma != 0 but coboundary = 0 (these give 0 = non-zero, inconsistent)
    # They will naturally appear since gamma has them in all_keys

    # Collect all phi labels
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)
    phi_labels = s4["coboundary"]["phi_labels"]
    phi_idx = {phi: i for i, phi in enumerate(phi_labels)}
    n_phi = len(phi_labels)

    # Build augmented matrix [A | b], one row per (X,Y,Z) equation
    equations = []
    for key in sorted(all_keys, key=str):
        cob_row = coboundary.get(key, {})
        rhs = gamma.get(key, Fraction(0))

        row = [Fraction(0)] * n_phi
        for phi, c in cob_row.items():
            if phi in phi_idx:
                row[phi_idx[phi]] = c
        equations.append((row, rhs))

    if not equations:
        return {"solvable": True, "rank": 0, "n_equations": 0,
                "n_phi": n_phi, "phi_solution": {}, "inconsistent_equations": []}

    nrow = len(equations)
    ncol = n_phi

    # Build augmented matrix
    mat = [list(row) + [rhs] for row, rhs in equations]

    # Gaussian elimination
    pivot_map = {}  # row -> col
    row_used = 0
    for col in range(ncol):
        pivot_row = None
        for r in range(row_used, nrow):
            if mat[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        mat[row_used], mat[pivot_row] = mat[pivot_row], mat[row_used]
        pivot_map[row_used] = col
        pv = mat[row_used][col]
        mat[row_used] = [x / pv for x in mat[row_used]]
        for r in range(nrow):
            if r != row_used and mat[r][col] != 0:
                factor = mat[r][col]
                mat[r] = [mat[r][k] - factor * mat[row_used][k] for k in range(ncol + 1)]
        row_used += 1

    rank = row_used

    # Check inconsistency: rows after pivot rows should have zero LHS and possibly nonzero RHS
    inconsistent = []
    for r in range(rank, nrow):
        if mat[r][ncol] != 0:
            # Inconsistent equation: 0 * phi = c (nonzero)
            inconsistent.append({
                "equation_index": r,
                "residual": str(mat[r][ncol]),
                "original_keys": list(sorted(all_keys, key=str))[r] if r < len(all_keys) else None
            })

    solvable = len(inconsistent) == 0

    # Extract particular solution (free vars = 0)
    phi_solution = {}
    for r, col in pivot_map.items():
        phi = phi_labels[col]
        phi_solution[phi] = mat[r][ncol]

    if verbose:
        print(f"  n={n}: rank={rank}, n_phi={n_phi}, n_equations={nrow}")
        print(f"  Inconsistent equations: {len(inconsistent)}")
        if inconsistent:
            for eq in inconsistent[:3]:
                key = eq.get("original_keys")
                print(f"    At {key}: 0 = {eq['residual']}")

    return {
        "solvable": solvable,
        "rank": rank,
        "n_equations": nrow,
        "n_phi": n_phi,
        "inconsistent_equations": inconsistent,
        "phi_solution": {k: str(v) for k, v in phi_solution.items() if v != 0}
    }


def main():
    print("=== Triviality Analysis for C(n+1) deformations ===\n")

    for n in [1, 2, 3]:
        print(f"--- n={n} (C({n+1}) = osp(2|{2*n})), all gb=1 ---")
        result = solve_triviality(n, verbose=True)
        print(f"  Solvable (trivial): {result['solvable']}")
        if result['solvable']:
            print(f"  Found phi solution with {len(result['phi_solution'])} non-zero components")
        else:
            print(f"  NOT TRIVIAL: {len(result['inconsistent_equations'])} inconsistent equations")
            for eq in result["inconsistent_equations"][:5]:
                print(f"    At {eq['original_keys']}: 0 ≠ {eq['residual']}")
        print()

    # Also test gb=0 (should always be trivial, since gamma=0)
    print("--- Verification: gb=0 (undeformed, always trivial) ---")
    for n in [1, 2, 3]:
        gb_assignment = {gb: 0 for gb in get_all_gb_labels(n)}
        result = solve_triviality(n, gb_assignment=gb_assignment)
        print(f"  n={n}: solvable={result['solvable']} (expected True)")


if __name__ == "__main__":
    main()

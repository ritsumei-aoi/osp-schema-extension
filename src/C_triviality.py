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


def build_coboundary_system(n):
    """
    Pre-reduce the coboundary matrix A (independent of gb) via Gaussian elimination,
    recording the row operations so that any RHS can be transformed quickly.

    Returns a dict with:
    - 'sorted_keys': list of (X,Y,Z) keys in row order
    - 'phi_labels': list of phi parameter labels (column order)
    - 'rank': rank of the coboundary matrix
    - 'nrow', 'ncol': matrix dimensions
    - 'ops': list of row operations (for applying to any RHS vector)
    - 'free_rows': row indices after elimination with zero LHS
    """
    coboundary = load_coboundary(n)
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)
    phi_labels = s4["coboundary"]["phi_labels"]
    phi_idx = {phi: i for i, phi in enumerate(phi_labels)}
    n_phi = len(phi_labels)

    sorted_keys = sorted(coboundary.keys(), key=str)
    nrow = len(sorted_keys)
    ncol = n_phi

    # Build A as a list of dicts (sparse) for efficiency
    A = []
    for key in sorted_keys:
        row = {}
        for phi, c in coboundary.get(key, {}).items():
            if phi in phi_idx and c != 0:
                row[phi_idx[phi]] = c
        A.append(row)

    # Gaussian elimination on A, recording operations as they apply to a RHS vector
    # ops is a list of ('swap', r1, r2), ('scale', r, factor), ('elim', r, pivot_r, factor)
    ops = []
    row_used = 0

    for col in range(ncol):
        # Find pivot
        pivot_row = None
        for r in range(row_used, nrow):
            if col in A[r] and A[r][col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue

        # Swap rows
        if pivot_row != row_used:
            A[row_used], A[pivot_row] = A[pivot_row], A[row_used]
            sorted_keys[row_used], sorted_keys[pivot_row] = \
                sorted_keys[pivot_row], sorted_keys[row_used]
            ops.append(('swap', row_used, pivot_row))

        # Scale pivot row
        pv = A[row_used][col]
        if pv != 1:
            inv_pv = Fraction(1, 1) / pv
            A[row_used] = {k: v * inv_pv for k, v in A[row_used].items()}
            ops.append(('scale', row_used, inv_pv))

        # Eliminate
        for r in range(nrow):
            if r != row_used and col in A[r] and A[r][col] != 0:
                factor = A[r][col]
                for k, v in A[row_used].items():
                    A[r][k] = A[r].get(k, Fraction(0)) - factor * v
                A[r] = {k: v for k, v in A[r].items() if v != 0}
                ops.append(('elim', r, row_used, factor))

        row_used += 1

    rank = row_used
    free_rows = list(range(rank, nrow))

    return {
        "sorted_keys": sorted_keys,
        "phi_labels": phi_labels,
        "rank": rank,
        "nrow": nrow,
        "ncol": ncol,
        "ops": ops,
        "free_rows": free_rows,
    }


def check_rhs_consistency(system, gamma):
    """
    Check whether the gamma RHS is consistent with the pre-reduced coboundary system.

    Applies the recorded row operations to the gamma RHS vector, then checks
    whether any zero-LHS row (free_rows) has a non-zero transformed RHS.
    Also flags any gamma entry whose (X,Y,Z) key has NO coboundary entry at all
    (zero coboundary row), since those are immediately inconsistent if gamma != 0.

    Returns (solvable, inconsistent_list).
    """
    sorted_keys = system["sorted_keys"]
    ops = system["ops"]
    free_rows = system["free_rows"]
    nrow = system["nrow"]
    keys_in_system = set(sorted_keys)

    inconsistent = []

    # Gamma entries not in coboundary system: (delta f)(X,Y)[Z] = 0 for all f
    # If gamma(X,Y)[Z] != 0, it's immediately inconsistent.
    for k, v in gamma.items():
        if k not in keys_in_system and v != 0:
            inconsistent.append({
                "original_keys": k,
                "residual": str(v),
            })

    # Build the gamma RHS vector aligned with (possibly reordered) sorted_keys
    b = [gamma.get(k, Fraction(0)) for k in sorted_keys]

    # Apply row operations to b
    for op in ops:
        if op[0] == 'swap':
            _, r1, r2 = op
            b[r1], b[r2] = b[r2], b[r1]
        elif op[0] == 'scale':
            _, r, factor = op
            if b[r] != 0:
                b[r] = b[r] * factor
        elif op[0] == 'elim':
            _, r, pivot_r, factor = op
            if b[pivot_r] != 0:
                b[r] = b[r] - factor * b[pivot_r]

    # Check free rows for non-zero residuals
    for r in free_rows:
        if b[r] != 0:
            inconsistent.append({
                "original_keys": sorted_keys[r],
                "residual": str(b[r]),
            })

    return len(inconsistent) == 0, inconsistent


def solve_triviality_with_system(system, n, gb_assignment=None, verbose=False):
    """Solve triviality using a pre-built coboundary system."""
    gamma = load_gamma_evaluated(n, gb_assignment)
    solvable, inconsistent = check_rhs_consistency(system, gamma)

    if verbose:
        print(f"  n={n}: rank={system['rank']}, n_phi={len(system['phi_labels'])}, "
              f"n_equations={system['nrow']}")
        print(f"  Inconsistent equations: {len(inconsistent)}")
        if inconsistent:
            for eq in inconsistent[:3]:
                print(f"    At {eq['original_keys']}: 0 = {eq['residual']}")

    return {
        "solvable": solvable,
        "rank": system["rank"],
        "n_equations": system["nrow"],
        "n_phi": len(system["phi_labels"]),
        "inconsistent_equations": inconsistent,
    }


def main():
    print("=== Triviality Analysis for C(n+1) deformations ===\n")

    # Pre-build the coboundary systems (done once per n)
    systems = {}
    for n in [1, 2, 3]:
        print(f"Building coboundary system for n={n}...")
        systems[n] = build_coboundary_system(n)
        print(f"  rank={systems[n]['rank']}, n_eq={systems[n]['nrow']}, "
              f"n_phi={len(systems[n]['phi_labels'])}")
    print()

    # --- All-gb=1 test ---
    print("=== All-gb=1 tests ===\n")
    for n in [1, 2, 3]:
        print(f"--- n={n} (C({n+1}) = osp(2|{2*n})), all gb=1 ---")
        result = solve_triviality_with_system(systems[n], n, verbose=True)
        print(f"  Solvable (trivial): {result['solvable']}")
        if not result["solvable"]:
            print(f"  NOT TRIVIAL: {len(result['inconsistent_equations'])} inconsistent equations")
            for eq in result["inconsistent_equations"][:5]:
                print(f"    At {eq['original_keys']}: 0 ≠ {eq['residual']}")
        print()

    # --- Individual gb tests: one gb=1, rest=0 ---
    print("=== Individual gb tests (one gb=1, rest=0) ===\n")
    for n in [1, 2, 3]:
        gb_labels = get_all_gb_labels(n)
        print(f"--- n={n} ---")
        for active_gb in gb_labels:
            gb_assignment = {gb: (1 if gb == active_gb else 0) for gb in gb_labels}
            result = solve_triviality_with_system(systems[n], n,
                                                   gb_assignment=gb_assignment)
            n_incon = len(result["inconsistent_equations"])
            trivial_str = ("TRIVIAL" if result["solvable"]
                           else f"NON-TRIVIAL ({n_incon} inconsistent)")
            if not result["solvable"] and result["inconsistent_equations"]:
                w = result["inconsistent_equations"][0]["original_keys"]
                print(f"  {active_gb}=1: {trivial_str}; first witness {w}")
            else:
                print(f"  {active_gb}=1: {trivial_str}")
        print()

    # --- Verification: gb=0 (undeformed, always trivial) ---
    print("--- Verification: gb=0 (undeformed, always trivial) ---")
    for n in [1, 2, 3]:
        gb_assignment = {gb: 0 for gb in get_all_gb_labels(n)}
        result = solve_triviality_with_system(systems[n], n, gb_assignment=gb_assignment)
        print(f"  n={n}: solvable={result['solvable']} (expected True)")


if __name__ == "__main__":
    main()

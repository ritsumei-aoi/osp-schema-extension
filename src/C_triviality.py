"""
C_triviality.py
Triviality analysis for the inhomogeneous deformation of C(n+1) = osp(2|2n).

Compares Layer 3 (evaluated gamma with gb=1) vs Layer 4 (coboundary delta_f).
Determines conditions under which gamma = delta_f (triviality).

The deformation is trivial iff there exist phi_{ij} values such that:
  For all (X,Y,Z): gamma(X,Y)^Z = (delta_f)(X,Y)^Z

This is a system of linear equations in the phi_{ij} parameters with the
gb parameter values as the RHS.
"""

import json
import sys
import os
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def load_gamma_evaluated(n, gb_values=None):
    """Load Schema 3 evaluated gamma as dict {(X,Y,Z): coeff}."""
    fname = f"data/C_{n}_evaluated.json"
    with open(fname) as f:
        d = json.load(f)
    result = {}
    for entry in d["evaluated_structure_constants"]:
        c_gamma = Fraction(entry.get("coeff_gamma", "0"))
        if c_gamma != 0:
            key = (entry["X"], entry["Y"], entry["Z"])
            result[key] = c_gamma
    return result


def load_coboundary(n):
    """Load Schema 4 coboundary as dict {(X,Y,Z): {phi_label: coeff}}."""
    fname = f"data/C_{n}_coboundary.json"
    with open(fname) as f:
        d = json.load(f)
    result = {}
    for entry in d["coboundary_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        if key not in result:
            result[key] = {}
        phi_lbl = entry["phi_param"]
        coeff = Fraction(entry["coeff"])
        result[key][phi_lbl] = result[key].get(phi_lbl, Fraction(0)) + coeff
    return result


def solve_triviality(n):
    """
    Determine if the deformation (with all gb=1) is trivial by checking
    whether the linear system gamma = delta_f has a solution.

    gamma(X,Y)^Z = sum_{phi_lbl} A_{(X,Y,Z), phi_lbl} * phi_lbl

    This is a system Ax = b where:
    - A: matrix of coboundary coefficients (rows = (X,Y,Z) constraints, cols = phi parameters)
    - x: vector of phi values (unknowns)
    - b: vector of gamma values (RHS)

    The deformation is trivial iff the system is consistent (Ax = b has a solution).
    """
    gamma = load_gamma_evaluated(n)
    coboundary = load_coboundary(n)

    # Collect all constraint keys (where either gamma or coboundary is nonzero)
    all_constraint_keys = set(list(gamma.keys()) + list(coboundary.keys()))

    # Collect all phi parameter names
    all_phi = set()
    for phi_dict in coboundary.values():
        all_phi.update(phi_dict.keys())
    all_phi = sorted(all_phi)
    phi_idx = {p: i for i, p in enumerate(all_phi)}

    # Build the system Ax = b
    # Row for each (X,Y,Z) constraint; column for each phi parameter
    constraints = sorted(all_constraint_keys)
    n_rows = len(constraints)
    n_cols = len(all_phi)

    # Build augmented matrix [A | b] for Gaussian elimination
    aug = []
    for key in constraints:
        row = [Fraction(0)] * (n_cols + 1)
        phi_dict = coboundary.get(key, {})
        for phi_lbl, coeff in phi_dict.items():
            col_idx = phi_idx[phi_lbl]
            row[col_idx] += coeff
        row[n_cols] = gamma.get(key, Fraction(0))
        aug.append(row)

    # Gaussian elimination over Q
    rank, is_consistent, pivot_cols = gaussian_elimination(aug, n_rows, n_cols)

    return {
        "n": n,
        "n_constraints": n_rows,
        "n_phi_params": n_cols,
        "rank": rank,
        "is_consistent": is_consistent,
        "pivot_columns": pivot_cols,
        "gamma_nonzero_count": len(gamma),
        "coboundary_constraint_count": len(coboundary)
    }


def gaussian_elimination(aug, n_rows, n_cols):
    """
    Perform Gaussian elimination on augmented matrix [A|b].
    Returns (rank, is_consistent, pivot_cols).
    """
    pivot_row = 0
    pivot_cols = []

    for col in range(n_cols):
        # Find pivot
        pivot = None
        for row in range(pivot_row, n_rows):
            if aug[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            continue

        # Swap rows
        aug[pivot_row], aug[pivot] = aug[pivot], aug[pivot_row]
        pivot_cols.append(col)

        # Eliminate
        pivot_val = aug[pivot_row][col]
        for row in range(n_rows):
            if row == pivot_row:
                continue
            if aug[row][col] != 0:
                factor = aug[row][col] / pivot_val
                for j in range(n_cols + 1):
                    aug[row][j] -= factor * aug[pivot_row][j]

        pivot_row += 1

    rank = pivot_row

    # Check consistency: no row of form [0,...,0 | b] with b != 0
    is_consistent = True
    for row in range(pivot_row, n_rows):
        if aug[row][n_cols] != 0:
            is_consistent = False
            break

    return rank, is_consistent, pivot_cols


def find_inconsistent_constraints(n):
    """
    Find specific (X,Y,Z) constraints that make the system inconsistent.
    These are gamma entries with no coboundary representation.
    """
    gamma = load_gamma_evaluated(n)
    coboundary = load_coboundary(n)

    # A constraint (X,Y,Z) with gamma != 0 but no coboundary entry is automatically inconsistent
    # (since no phi can account for it).
    # More generally, we need to check linear independence.

    inconsistent = []
    for key, gamma_val in gamma.items():
        if key not in coboundary:
            inconsistent.append({
                "X": key[0], "Y": key[1], "Z": key[2],
                "gamma_val": str(gamma_val),
                "coboundary_present": False,
                "type": "no_coboundary_term"
            })

    return inconsistent


def main():
    print("=" * 60)
    print("Triviality Analysis for C(n+1) = osp(2|2n)")
    print("gb assignment: all gb = +1")
    print("=" * 60)

    for n in [1, 2, 3]:
        print(f"\n--- C({n+1}) (n={n}) ---")

        result = solve_triviality(n)
        print(f"  Constraints: {result['n_constraints']}")
        print(f"  Phi parameters: {result['n_phi_params']}")
        print(f"  Rank of A: {result['rank']}")
        print(f"  Gamma non-zero entries: {result['gamma_nonzero_count']}")
        print(f"  System consistent (trivial deformation): {result['is_consistent']}")

        if not result["is_consistent"]:
            incons = find_inconsistent_constraints(n)
            if incons:
                print(f"  Constraints with no coboundary term ({len(incons)}):")
                for item in incons[:5]:
                    print(f"    [{item['X']}, {item['Y']}] -> {item['Z']}: gamma={item['gamma_val']}")

    # Additional analysis: what if gb parameters are chosen to make it trivial?
    print("\n" + "=" * 60)
    print("Analysis: Conditions for trivial deformation")
    print("=" * 60)
    analyze_triviality_conditions()


def analyze_triviality_conditions():
    """
    Analyze what conditions on gb parameters make the deformation trivial.
    A deformation is trivial iff gamma = delta_f for some f, i.e.,
    the system A*phi = b(gb) has a solution in phi.

    For linear gamma(gb) = M*gb (gamma is linear in gb parameters), the
    triviality condition becomes: b(gb) = A*phi, i.e., b(gb) in Im(A).

    We check when specific gb configurations yield trivial deformations.
    """
    for n in [1, 2, 3]:
        print(f"\n--- C({n+1}) (n={n}): structural analysis ---")
        gamma_full = load_gamma_evaluated(n)  # This has gb=1 substituted
        coboundary = load_coboundary(n)

        # Check which (X,Y,Z) appear in gamma but not in coboundary
        gamma_keys = set(gamma_full.keys())
        cob_keys = set(coboundary.keys())

        only_in_gamma = gamma_keys - cob_keys
        only_in_cob = cob_keys - gamma_keys
        in_both = gamma_keys & cob_keys

        print(f"  gamma entries: {len(gamma_keys)}")
        print(f"  coboundary constraint entries: {len(cob_keys)}")
        print(f"  In gamma only (impossible to cancel by coboundary): {len(only_in_gamma)}")
        print(f"  In coboundary only: {len(only_in_cob)}")
        print(f"  In both: {len(in_both)}")

        if only_in_gamma:
            print(f"  Example gamma-only entries (these prevent triviality with gb=1):")
            for key in sorted(only_in_gamma)[:3]:
                print(f"    {key}: gamma = {gamma_full[key]}")

        if not only_in_gamma:
            print(f"  All gamma entries have coboundary counterparts.")
            result = solve_triviality(n)
            print(f"  System consistent: {result['is_consistent']}")

    print("\n--- Conjecture on gb conditions for triviality ---")
    print("""
The deformation gamma(gb) is trivial iff the linear system A*phi = b(gb) is consistent,
where A is the coboundary matrix (independent of gb) and b(gb) = M*gb (linear in gb).

From the analysis above:
- For ALL n=1,2,3 with gb=1: entries appear in gamma that have no coboundary counterpart
  (or the system is inconsistent), indicating the ALL-PLUS deformation is NON-TRIVIAL.

- Triviality requires: for each (X,Y,Z), the gamma value gamma(X,Y)^Z (linear in gb)
  must lie in the image of the coboundary map A.

- Since some (X,Y,Z) entries appear in gamma but not in any coboundary term,
  the ONLY way these can be zero is if the corresponding gb-combinations vanish.

- General conjecture: The deformation is trivial if and only if all 4n gb parameters
  are zero (the undeformed case), OR specific linear constraints on gb are satisfied
  corresponding to the null space of the gamma-to-coboundary mapping.

- More precisely: gamma is in Im(delta) iff the gb parameters satisfy
  the linear constraints M_perp * gb = 0 where M_perp projects onto the
  complement of Im(A) in the gamma space.
""")


if __name__ == "__main__":
    main()

"""
Detailed triviality analysis: finds conditions on gb parameters for triviality.

For each (X,Y,Z) where the coboundary has no contribution, gamma(X,Y)[Z](gb) must = 0.
These are the NECESSARY conditions on gb.

Also investigates which gb combinations yield trivial deformations.
"""

import json
import sys
from fractions import Fraction

sys.path.insert(0, 'src')
from C_gamma import get_all_gb_labels
from C_triviality import load_gamma_evaluated, load_coboundary, solve_triviality


def find_triviality_conditions(n, verbose=False):
    """
    Find the necessary conditions on gb for triviality.

    Returns:
    - necessary_conditions: list of {(X,Y,Z): linear_comb_of_gb} = 0 required
    - coboundary_zero_locus: list of (X,Y,Z) with zero coboundary contribution
    """
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)

    gb_labels = get_all_gb_labels(n)
    phi_labels = s4["coboundary"]["phi_labels"]

    # Build coboundary: (X,Y,Z) -> {phi: coeff}
    coboundary = {}
    for entry in s4["coboundary"]["coboundary_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        key = (X, Y, Z)
        if key not in coboundary:
            coboundary[key] = {}
        for phi, c in entry["phi_coeffs"].items():
            coboundary[key][phi] = coboundary[key].get(phi, Fraction(0)) + Fraction(c)

    # Build gamma: (X,Y,Z) -> {gb: coeff}
    gamma_sym = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y = entry["X"], entry["Y"]
        for gb, gen_coeffs in entry["gamma_coeffs"].items():
            for Z, c in gen_coeffs.items():
                key = (X, Y, Z)
                if key not in gamma_sym:
                    gamma_sym[key] = {}
                gamma_sym[key][gb] = gamma_sym[key].get(gb, Fraction(0)) + Fraction(c)

    # Necessary conditions: for (X,Y,Z) with zero coboundary but non-zero gamma
    necessary_conditions = []
    for key, gb_dict in gamma_sym.items():
        if not coboundary.get(key):
            # Zero coboundary — gamma must also be zero for this key
            gb_dict = {k: v for k, v in gb_dict.items() if v != 0}
            if gb_dict:
                necessary_conditions.append({
                    "XYZ": key,
                    "gamma_linear_in_gb": {k: str(v) for k, v in gb_dict.items()}
                })

    return necessary_conditions


def extract_gb_conditions(n):
    """
    Extract the constraints on gb parameters from necessary conditions.
    These are linear equations in gb_labels that must be satisfied for triviality.
    """
    conditions = find_triviality_conditions(n)
    gb_labels = get_all_gb_labels(n)
    gb_idx = {gb: i for i, gb in enumerate(gb_labels)}

    # Build system: A * gb_vec = 0
    rows = []
    for cond in conditions:
        row = [Fraction(0)] * len(gb_labels)
        for gb, c in cond["gamma_linear_in_gb"].items():
            if gb in gb_idx:
                row[gb_idx[gb]] = Fraction(c)
        rows.append(row)

    if not rows:
        return {"conditions": [], "rank": 0, "n_gb": len(gb_labels)}

    # Gaussian elimination on A (no RHS — homogeneous system)
    mat = [list(r) for r in rows]
    nrow, ncol = len(mat), len(gb_labels)
    pivot_cols = []
    row_used = 0
    for col in range(ncol):
        pr = None
        for r in range(row_used, nrow):
            if mat[r][col] != 0:
                pr = r
                break
        if pr is None:
            continue
        mat[row_used], mat[pr] = mat[pr], mat[row_used]
        pivot_cols.append(col)
        pv = mat[row_used][col]
        mat[row_used] = [x / pv for x in mat[row_used]]
        for r in range(nrow):
            if r != row_used and mat[r][col] != 0:
                f = mat[r][col]
                mat[r] = [mat[r][k] - f * mat[row_used][k] for k in range(ncol)]
        row_used += 1

    rank = row_used
    print(f"\n=== n={n}: Necessary conditions on gb for triviality ===")
    print(f"  {len(conditions)} conditions (from zero-coboundary positions with non-zero gamma)")
    print(f"  After elimination: rank={rank} independent constraints on {len(gb_labels)} gb parameters")
    print(f"  Free gb parameters: {len(gb_labels) - rank}")

    # Print the independent constraints
    print("  Independent constraints (gb must satisfy):")
    for r in range(rank):
        terms = []
        for j in range(ncol):
            if mat[r][j] != 0:
                terms.append(f"{mat[r][j]}*{gb_labels[j]}")
        print(f"    {' + '.join(terms)} = 0")

    return {"rank": rank, "n_gb": len(gb_labels),
            "pivot_cols": pivot_cols,
            "free_gb_indices": [j for j in range(ncol) if j not in pivot_cols]}


def test_specific_gb(n):
    """Test some specific gb assignments for triviality."""
    gb_labels = get_all_gb_labels(n)
    print(f"\n=== n={n}: Testing specific gb assignments ===")

    # Test 1: all gb = 0 (undeformed, always trivial)
    gb0 = {gb: 0 for gb in gb_labels}
    r0 = solve_triviality(n, gb_assignment=gb0)
    print(f"  All gb=0: trivial={r0['solvable']}")

    # Test 2: all gb = 1
    gb1 = {gb: 1 for gb in gb_labels}
    r1 = solve_triviality(n, gb_assignment=gb1)
    print(f"  All gb=1: trivial={r1['solvable']}")

    # Test 3: only gb_a1p parameters non-zero (a1^+ interactions)
    gb_p = {gb: (1 if "a1p" in gb else 0) for gb in gb_labels}
    rp = solve_triviality(n, gb_assignment=gb_p)
    print(f"  Only gb_a1p=1: trivial={rp['solvable']}")

    # Test 4: only gb_a1m parameters non-zero
    gb_m = {gb: (1 if "a1m" in gb else 0) for gb in gb_labels}
    rm = solve_triviality(n, gb_assignment=gb_m)
    print(f"  Only gb_a1m=1: trivial={rm['solvable']}")

    # Test 5: gb_a1p = t, gb_a1m = -t (antisymmetric)
    gb_anti = {gb: (1 if "a1p" in gb else -1) for gb in gb_labels}
    ra = solve_triviality(n, gb_assignment=gb_anti)
    print(f"  gb_a1p=1, gb_a1m=-1: trivial={ra['solvable']}")


if __name__ == "__main__":
    for n in [1, 2, 3]:
        cond_info = extract_gb_conditions(n)
        test_specific_gb(n)

    print("\n=== Summary ===")
    print("The inhomogeneous deformation of C(n+1) is trivial if and only if")
    print("the gb parameters satisfy the necessary linear constraints above.")

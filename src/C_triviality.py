"""
C_triviality.py: Determine when the C(n+1) deformation gamma is trivial (= delta f).

For each n, set up the linear system:
  sum_{phi_param} coboundary_coeff(X,Y,Z,phi) * phi_val = gamma_eval(X,Y,Z)

If this system has a solution, the deformation is trivial (exact coboundary).
We report rank, null space dimension, and whether the all-gb=+1 evaluated gamma
lies in the image of the coboundary map.
"""

import json
import sys
import os
from fractions import Fraction

def load_layer3(n):
    """Load evaluated gamma (all gb=+1): {(X,Y,Z): coeff}."""
    with open(f"data/C_{n}_evaluated.json") as f:
        data = json.load(f)
    gamma = {}
    for entry in data["evaluated_gamma"]["entries"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gamma[key] = gamma.get(key, Fraction(0)) + Fraction(entry["coeff"])
    return {k: v for k, v in gamma.items() if v != 0}


def load_layer4(n):
    """Load coboundary (symbolic in phi): {(X,Y,Z,phi): coeff}."""
    with open(f"data/C_{n}_coboundary.json") as f:
        data = json.load(f)
    cb = {}
    for entry in data["coboundary_delta_f"]["entries"]:
        key = (entry["X"], entry["Y"], entry["Z"], entry["phi_param"])
        cb[key] = cb.get(key, Fraction(0)) + Fraction(entry["coeff"])
    return {k: v for k, v in cb.items() if v != 0}


def build_linear_system(n, gamma, coboundary):
    """
    Build Ax = b where:
    - columns = phi parameter indices
    - rows = (X,Y,Z) triples
    - A[row, col] = coboundary coefficient for that (X,Y,Z,phi)
    - b[row] = gamma evaluated at (X,Y,Z) (0 if not in gamma)
    """
    # Collect all (X,Y,Z) from both sources
    xyz_set = set(k[:3] for k in coboundary.keys()) | set(gamma.keys())
    xyz_list = sorted(xyz_set)

    # Collect all phi parameters
    phi_set = set(k[3] for k in coboundary.keys())
    phi_list = sorted(phi_set)

    row_idx = {xyz: i for i, xyz in enumerate(xyz_list)}
    col_idx = {phi: j for j, phi in enumerate(phi_list)}

    nrows = len(xyz_list)
    ncols = len(phi_list)

    # Build augmented matrix [A | b] using dict-of-dict for sparse representation
    A = [[Fraction(0)] * ncols for _ in range(nrows)]
    b = [Fraction(0)] * nrows

    for key, coeff in coboundary.items():
        X, Y, Z, phi = key
        r = row_idx[(X, Y, Z)]
        c = col_idx[phi]
        A[r][c] += coeff

    for xyz, coeff in gamma.items():
        r = row_idx[xyz]
        b[r] += coeff

    return A, b, xyz_list, phi_list


def gaussian_elimination(A, b):
    """
    Gaussian elimination over Q on augmented matrix [A|b].
    Returns (rank, is_consistent, pivot_cols, solution_space_dim).
    """
    nrows = len(A)
    ncols = len(A[0]) if nrows > 0 else 0
    # Augment
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    pivot_row = 0
    pivot_cols = []
    for col in range(ncols):
        # Find pivot
        found = -1
        for row in range(pivot_row, nrows):
            if M[row][col] != 0:
                found = row
                break
        if found == -1:
            continue
        # Swap
        M[pivot_row], M[found] = M[found], M[pivot_row]
        pivot_cols.append(col)
        # Scale
        scale = M[pivot_row][col]
        M[pivot_row] = [x / scale for x in M[pivot_row]]
        # Eliminate
        for row in range(nrows):
            if row != pivot_row and M[row][col] != 0:
                factor = M[row][col]
                M[row] = [M[row][j] - factor * M[pivot_row][j] for j in range(ncols + 1)]
        pivot_row += 1

    rank = len(pivot_cols)

    # Check consistency: any row with all-zero A-part but nonzero b
    is_consistent = True
    for row in range(rank, nrows):
        if any(M[row][j] != 0 for j in range(ncols)):
            break  # still has nonzero A part somehow
        if M[row][ncols] != 0:
            is_consistent = False
            break

    return rank, is_consistent, pivot_cols, ncols - rank


def analyze_triviality(n):
    print(f"\n{'='*60}")
    print(f"C_{n} (n={n}, C({n+1}) = osp(2|{2*n}))")
    print(f"{'='*60}")

    gamma = load_layer3(n)
    coboundary = load_layer4(n)

    print(f"Layer 3 entries (all gb=+1): {len(gamma)}")
    print(f"Layer 4 coboundary entries: {len(coboundary)}")

    A, b, xyz_list, phi_list = build_linear_system(n, gamma, coboundary)
    nrows = len(xyz_list)
    ncols = len(phi_list)

    print(f"Linear system: {nrows} equations, {ncols} phi unknowns")

    # For large systems, only do rank analysis on small n=1
    if n <= 2:
        rank, is_consistent, pivot_cols, null_dim = gaussian_elimination(A, b)
        print(f"Rank of coboundary map: {rank}")
        print(f"Null space dimension: {null_dim}")
        print(f"Is gamma(gb=+1) in image of delta? {is_consistent}")
        if is_consistent:
            print("  => TRIVIAL: deformation (all gb=+1) is a coboundary")
        else:
            print("  => NON-TRIVIAL: deformation not in image of delta")
            # Show first inconsistency
            for i, xyz in enumerate(xyz_list):
                is_zero_row = all(A[i][j] == 0 for j in range(ncols))
                if is_zero_row and b[i] != 0:
                    print(f"  Obstruction at (X,Y,Z)={xyz}: gamma={b[i]}, coboundary=0")
                    break
    else:
        print(f"  (Skipping full Gaussian elimination for n={n} — system too large)")
        # Quick check: any (X,Y,Z) in gamma but not reachable by any coboundary entry?
        cb_xyz = set(k[:3] for k in coboundary.keys())
        unreachable = [(k, v) for k, v in gamma.items() if k not in cb_xyz]
        if unreachable:
            print(f"  {len(unreachable)} gamma entries have no coboundary contribution at (X,Y,Z)")
            print(f"  => Evidence of NON-TRIVIALITY (coboundary map cannot reach these)")
            for k, v in unreachable[:3]:
                print(f"    (X,Y,Z)={k}, gamma={v}")
        else:
            print(f"  All gamma (X,Y,Z) triples reachable by coboundary (necessary but not sufficient)")

    return gamma, coboundary, xyz_list, phi_list


def check_zero_gamma_pairs(n, gamma):
    """Check which (X,Y) pairs contribute zero to gamma (no deformation)."""
    pairs = {}
    for (X, Y, Z), c in gamma.items():
        pairs.setdefault((X, Y), []).append(c)
    zero_pairs = [(X, Y) for (X, Y), coeffs in pairs.items() if all(c == 0 for c in coeffs)]
    return zero_pairs


def main():
    print("Triviality Analysis: C(n+1) inhomogeneous deformation vs coboundary")
    print("All-gb=+1 evaluation of Layer 3 compared to Layer 4 coboundary map")

    results = {}
    for n in [1, 2]:
        gamma, coboundary, xyz_list, phi_list = analyze_triviality(n)
        results[n] = {"gamma": gamma, "coboundary": coboundary,
                      "xyz": xyz_list, "phi": phi_list}

    # Additional structural analysis for n=1
    print("\n" + "="*60)
    print("Structural Analysis (n=1)")
    print("="*60)
    gamma1 = results[1]["gamma"]

    # Identify which (X,Y) sectors have gamma contributions
    sectors = {}
    with open("data/C_1_structure.json") as f:
        sc1 = json.load(f)
    parity = sc1["parity"]
    for (X, Y, Z), c in gamma1.items():
        px = parity.get(X, 0)
        py = parity.get(Y, 0)
        sector = (px, py)
        sectors.setdefault(sector, []).append((X, Y, Z, c))
    for sector, entries in sorted(sectors.items()):
        names = {(0,0): "even-even", (0,1): "even-odd", (1,0): "odd-even", (1,1): "odd-odd"}
        print(f"  {names.get(sector, str(sector))}: {len(entries)} gamma entries")


if __name__ == "__main__":
    main()

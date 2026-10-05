"""
search_triviality.py - Analytical investigation of triviality conditions for C(n+1) = osp(2|2n).

Solves the linear system delta(f) = gamma(gb) to determine whether the inhomogeneous deformation
is trivial (a coboundary), and finds the exact algebraic conditions on the gb parameters.
"""

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any, Set


def solve_triviality_symbolic(n: int) -> Dict[str, Any]:
    # Load Schema 2 and Schema 4
    with open(f"data/C_{n}_gamma.json", "r", encoding="utf-8") as f:
        s2_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r", encoding="utf-8") as f:
        s4_data = json.load(f)

    basis_odd = s2_data["basis"]["odd"]
    basis_even = s2_data["basis"]["even"]
    full_basis = basis_odd + basis_even
    parity = s2_data["parity"]
    gb_params = s2_data["gb_parameters"]
    f_params = s4_data["f_map_parameters"]["parameters"]

    # Identify independent generator pairs (X, Y) with X <= Y in PBW ordering
    # Because of super-antisymmetry, (X, Y) determines (Y, X).
    pairs = []
    for i, x in enumerate(full_basis):
        for j in range(i, len(full_basis)):
            y = full_basis[j]
            pairs.append((x, y))

    # Identify all possible equations: (X, Y, Z) where Z has parity (p(X)+p(Y)+1) mod 2
    eq_keys = []
    for x, y in pairs:
        px, py = parity[x], parity[y]
        expected_pz = (px + py + 1) % 2
        target_basis = basis_odd if expected_pz == 1 else basis_even
        for z in target_basis:
            eq_keys.append((x, y, z))

    eq_to_idx = {eq: i for i, eq in enumerate(eq_keys)}
    n_eqs = len(eq_keys)
    n_f = len(f_params)
    n_gb = len(gb_params)

    f_to_idx = {fp: j for j, fp in enumerate(f_params)}
    gb_to_idx = {gp: k for k, gp in enumerate(gb_params)}

    # Build Matrix M (coboundary) of size (n_eqs x n_f)
    # and Matrix B (gamma) of size (n_eqs x n_gb)
    M = [[Fraction(0) for _ in range(n_f)] for _ in range(n_eqs)]
    B = [[Fraction(0) for _ in range(n_gb)] for _ in range(n_eqs)]

    # Populate M from Schema 4
    for entry in s4_data["coboundary_operator"]["coboundary_structure"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        fp = entry["f_param"]
        coeff = Fraction(entry["coeff"])

        if (x, y, z) in eq_to_idx:
            eq_idx = eq_to_idx[(x, y, z)]
            M[eq_idx][f_to_idx[fp]] += coeff
        # If (x, y) was in reverse order
        elif (y, x, z) in eq_to_idx:
            # Need to relate (y, x) to (x, y) by -(-1)^{px py}
            px, py = parity[x], parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            eq_idx = eq_to_idx[(y, x, z)]
            # delta(f)(y, x) = -sign * delta(f)(x, y) => coeff on (x, y) is -sign * coeff
            # But the table stored entry for (x, y). So (y, x) equation gets -sign * coeff?
            # Wait: entry is (x, y, z). If we want the equation for (y, x, z):
            # delta(f)(y, x) has coeff -sign * (entry coeff).
            # But we already have the entry for (y, x) directly in coboundary table!
            pass

    # Populate B from Schema 2
    for entry in s2_data["inhomogeneous_deformation"]["gamma_structure"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        gp = entry["param"]
        coeff = Fraction(entry["coeff"])

        if (x, y, z) in eq_to_idx:
            eq_idx = eq_to_idx[(x, y, z)]
            B[eq_idx][gb_to_idx[gp]] += coeff

    # Filter out all zero equations (rows of M and B that are identically zero)
    non_zero_eqs = []
    for i in range(n_eqs):
        if any(M[i][j] != 0 for j in range(n_f)) or any(B[i][k] != 0 for k in range(n_gb)):
            non_zero_eqs.append(i)

    print(f"n={n} (C({n+1})): Total equations = {n_eqs}, Non-zero equations = {len(non_zero_eqs)}, f_vars = {n_f}, gb_vars = {n_gb}")

    # Build augmented matrix [M | B] for Gaussian elimination
    # Size: len(non_zero_eqs) rows x (n_f + n_gb) columns
    A = []
    for eq_idx in non_zero_eqs:
        row = [M[eq_idx][j] for j in range(n_f)] + [B[eq_idx][k] for k in range(n_gb)]
        A.append(row)

    n_rows = len(A)
    n_cols = n_f + n_gb

    # Row reduce M part (columns 0 .. n_f - 1)
    pivot_row = 0
    pivot_cols = []
    for col in range(n_f):
        found = -1
        for r in range(pivot_row, n_rows):
            if A[r][col] != 0:
                found = r
                break
        if found == -1:
            continue
        A[pivot_row], A[found] = A[found], A[pivot_row]
        pivot_val = A[pivot_row][col]
        for c in range(col, n_cols):
            A[pivot_row][c] /= pivot_val
        for r in range(n_rows):
            if r != pivot_row and A[r][col] != 0:
                factor = A[r][col]
                for c in range(col, n_cols):
                    A[r][c] -= factor * A[pivot_row][c]
        pivot_cols.append((pivot_row, col))
        pivot_row += 1

    rank_M = pivot_row
    print(f"n={n}: Rank of coboundary operator M = {rank_M} / {n_f}")

    # Check constraint rows (rows from rank_M to n_rows - 1 where M part is all 0)
    # Each such row gives a linear constraint on gb: sum_k A[r][n_f + k] * gb_k = 0
    gb_constraints = []
    for r in range(rank_M, n_rows):
        gb_coeffs = [A[r][n_f + k] for k in range(n_gb)]
        if any(c != 0 for c in gb_coeffs):
            gb_constraints.append(gb_coeffs)

    print(f"n={n}: Number of non-trivial constraints on gb = {len(gb_constraints)}")

    # Reduce the gb_constraints
    if gb_constraints:
        # Row reduce gb_constraints
        C = [row[:] for row in gb_constraints]
        cr_pivot = 0
        for col in range(n_gb):
            found = -1
            for r in range(cr_pivot, len(C)):
                if C[r][col] != 0:
                    found = r
                    break
            if found == -1:
                continue
            C[cr_pivot], C[found] = C[found], C[cr_pivot]
            pval = C[cr_pivot][col]
            for c in range(col, n_gb):
                C[cr_pivot][c] /= pval
            for r in range(len(C)):
                if r != cr_pivot and C[r][col] != 0:
                    fac = C[r][col]
                    for c in range(col, n_gb):
                        C[r][c] -= fac * C[cr_pivot][c]
            cr_pivot += 1
        independent_constraints = [row for row in C[:cr_pivot] if any(x != 0 for x in row)]
        print(f"n={n}: Number of independent constraints on gb = {len(independent_constraints)}")
        for idx, con in enumerate(independent_constraints):
            terms = [f"{con[k]} * {gb_params[k]}" for k in range(n_gb) if con[k] != 0]
            print(f"  Constraint {idx+1}: " + " + ".join(terms) + " = 0")
    else:
        independent_constraints = []
        print(f"n={n}: ZERO constraints on gb! Every inhomogeneous deformation is unconditionally trivial!")

    # Test concrete assignment: all gb = 1
    all_ones = [Fraction(1)] * n_gb
    all_ones_consistent = True
    discrepant_equations = []
    for r in range(rank_M, n_rows):
        val = sum(A[r][n_f + k] * all_ones[k] for k in range(n_gb))
        if val != 0:
            all_ones_consistent = False
            # Map back to equation key
            orig_eq_idx = non_zero_eqs[r]
            eq_key = eq_keys[orig_eq_idx]
            discrepant_equations.append((eq_key, val))

    print(f"n={n}: All-ones profile triviality: {all_ones_consistent}")
    if not all_ones_consistent:
        print(f"  Found {len(discrepant_equations)} discrepant equation(s). Sample discrepancies:")
        for eq, val in discrepant_equations[:5]:
            print(f"    Eq {eq}: discrepancy = {val}")

    return {
        "n": n,
        "n_f": n_f,
        "n_gb": n_gb,
        "rank_M": rank_M,
        "independent_constraints_count": len(independent_constraints),
        "constraints": independent_constraints,
        "all_ones_trivial": all_ones_consistent,
        "sample_discrepancies": discrepant_equations[:5]
    }


def main():
    print("=== Triviality Condition Search for C(n+1) ===\n")
    results = {}
    for n in [1, 2, 3]:
        results[n] = solve_triviality_symbolic(n)
        print("-" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
C_triviality.py: Compare gamma (Schema 3) with coboundary (Schema 4) to
determine triviality conditions for the inhomogeneous deformation of C(n+1).

A deformation gamma is trivial iff there exists an odd linear map f such that
gamma(X,Y) = (delta_f)(X,Y) for all X, Y in g.

This amounts to solving the linear system:
  [coboundary matrix] * phi_vector = gamma_vector

We solve this for each n and report:
  - Whether a solution exists (is the system consistent?)
  - The general solution space (null space of coboundary matrix)
  - The conditions on gb parameters for triviality
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from C_generators import CnPlusOne


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_linear_system(n, data_dir='data'):
    """
    Build the linear system [M * phi = v] where:
      M: coboundary matrix  (rows = (X,Y,Z) entries, cols = phi parameters)
      v: gamma_evaluated vector (same indexing)

    Returns (M_dict, v_dict, keys, phi_labels) where:
      M_dict: {(X,Y,Z): {phi_label: Fraction}}
      v_dict: {(X,Y,Z): Fraction}
      keys: sorted list of (X,Y,Z) triples that appear
      phi_labels: list of phi parameter labels
    """
    # Load Schema 3 (evaluated gamma, all gb=1)
    ev = load_json(os.path.join(data_dir, f'C_{n}_evaluated.json'))
    gamma_entries = ev['gamma_evaluated']

    # Load Schema 4 (coboundary)
    cb = load_json(os.path.join(data_dir, f'C_{n}_coboundary.json'))
    coboundary_entries = cb['coboundary']
    phi_labels = cb['f_map_parameters']['labels']

    # Build v_dict from gamma
    v_dict = defaultdict(Fraction)
    for e in gamma_entries:
        key = (e['X'], e['Y'], e['Z'])
        v_dict[key] += Fraction(e['coeff'])

    # Build M_dict from coboundary
    M_dict = {}
    for e in coboundary_entries:
        key = (e['X'], e['Y'], e['Z'])
        M_dict[key] = {phi: Fraction(v) for phi, v in e['phi_coefficients'].items()}

    # Union of all keys
    all_keys = sorted(set(v_dict.keys()) | set(M_dict.keys()))

    return M_dict, dict(v_dict), all_keys, phi_labels


def solve_system_fraction(M_dict, v_dict, all_keys, phi_labels):
    """
    Solve M * phi = v using Gaussian elimination over fractions.

    Returns:
      consistent: bool
      solution: dict {phi_label: Fraction} (particular solution, if consistent)
      null_basis: list of dicts (null space basis vectors)
      rank: int
    """
    nrows = len(all_keys)
    ncols = len(phi_labels)
    phi_idx = {phi: j for j, phi in enumerate(phi_labels)}

    # Build augmented matrix [M | v]
    aug = [[Fraction(0)] * (ncols + 1) for _ in range(nrows)]
    for i, key in enumerate(all_keys):
        # RHS
        aug[i][ncols] = v_dict.get(key, Fraction(0))
        # LHS
        if key in M_dict:
            for phi, c in M_dict[key].items():
                j = phi_idx[phi]
                aug[i][j] = c

    # Gaussian elimination
    pivot_col_for_row = {}
    row = 0
    for col in range(ncols):
        pivot = next((r for r in range(row, nrows) if aug[r][col]), None)
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        pv = aug[row][col]
        aug[row] = [x / pv for x in aug[row]]
        for r in range(nrows):
            if r != row and aug[r][col]:
                f = aug[r][col]
                aug[r] = [aug[r][c] - f * aug[row][c] for c in range(ncols + 1)]
        pivot_col_for_row[row] = col
        row += 1

    rank = row

    # Check consistency: any row of form [0 ... 0 | v] with v != 0?
    inconsistent_rows = []
    for r in range(rank, nrows):
        if aug[r][ncols]:
            inconsistent_rows.append(r)

    consistent = len(inconsistent_rows) == 0

    if not consistent:
        return False, {}, [], rank, inconsistent_rows

    # Extract particular solution
    sol = [Fraction(0)] * ncols
    pivot_cols = list(pivot_col_for_row.values())
    for r, col in pivot_col_for_row.items():
        sol[col] = aug[r][ncols]

    # Null space basis: for each free variable j, set it to 1 and others to 0
    free_cols = [j for j in range(ncols) if j not in pivot_cols]
    null_basis = []
    for fc in free_cols:
        null_vec = [Fraction(0)] * ncols
        null_vec[fc] = Fraction(1)
        for r, pc in pivot_col_for_row.items():
            null_vec[pc] = -aug[r][fc]
        null_basis.append(null_vec)

    solution = {phi_labels[j]: sol[j] for j in range(ncols) if sol[j]}
    null_vecs = [
        {phi_labels[j]: v for j, v in enumerate(nv) if v}
        for nv in null_basis
    ]

    return True, solution, null_vecs, rank, []


def analyze_triviality(n, data_dir='data'):
    """Full triviality analysis for C(n+1)."""
    print(f"\n{'='*60}")
    print(f"Triviality Analysis: C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    M_dict, v_dict, all_keys, phi_labels = build_linear_system(n, data_dir)
    print(f"Linear system: {len(all_keys)} equations, {len(phi_labels)} unknowns (phi params)")
    print(f"Non-zero gamma entries: {sum(1 for v in v_dict.values() if v)}")
    print(f"Non-zero coboundary entries: {len(M_dict)}")

    result = solve_system_fraction(M_dict, v_dict, all_keys, phi_labels)
    consistent, solution, null_vecs, rank, bad_rows = result

    print(f"Coboundary matrix rank: {rank}")
    print(f"Null space dimension (free parameters in f): {len(null_vecs)}")

    if consistent:
        print(f"\nResult: TRIVIAL (a solution f exists)")
        print(f"A particular solution f has {len(solution)} non-zero phi parameters.")
        if solution:
            for phi, val in list(solution.items())[:5]:
                print(f"  {phi} = {val}")
            if len(solution) > 5:
                print(f"  ... ({len(solution)} total non-zero)")
    else:
        print(f"\nResult: NON-TRIVIAL (no solution f exists)")
        print(f"Number of inconsistent equations: {len(bad_rows)}")
        print("Inconsistent equations arise from (X,Y,Z) triples where")
        print("gamma(X,Y)_Z cannot be matched by any coboundary (delta_f)(X,Y)_Z.")
        print("\nSample inconsistent triples:")
        for idx in bad_rows[:5]:
            key = all_keys[idx]
            gval = v_dict.get(key, Fraction(0))
            print(f"  gamma({key[0]}, {key[1]})_{key[2]} = {gval}")

    return consistent, solution, null_vecs, rank, M_dict, v_dict, all_keys, phi_labels


def investigate_general_gb(n, data_dir='data'):
    """
    Investigate which gb conditions make the deformation trivial (general symbolic case).
    We solve M * phi = gamma(gb) where gamma is symbolic in gb.
    This requires loading the symbolic gamma (Schema 2) and checking
    consistency conditions on gb.
    """
    print(f"\n--- General GB Analysis for C({n+1}) ---")

    # Load symbolic gamma
    gamma2 = load_json(os.path.join(data_dir, f'C_{n}_gamma.json'))
    gb_labels = gamma2['deformation_parameters']['labels']
    gamma_entries = gamma2['gamma_structure']

    # Load coboundary
    cb = load_json(os.path.join(data_dir, f'C_{n}_coboundary.json'))
    coboundary_entries = cb['coboundary']
    phi_labels = cb['f_map_parameters']['labels']

    # Build symbolic gamma: {(X,Y,Z): {gb_label: Fraction}}
    gamma_sym = defaultdict(lambda: defaultdict(Fraction))
    for e in gamma_entries:
        key = (e['X'], e['Y'], e['Z'])
        for gb, c in e['coeff_expr'].items():
            gamma_sym[key][gb] += Fraction(c)

    # Build coboundary: {(X,Y,Z): {phi_label: Fraction}}
    cob_sym = {}
    for e in coboundary_entries:
        key = (e['X'], e['Y'], e['Z'])
        cob_sym[key] = {phi: Fraction(v) for phi, v in e['phi_coefficients'].items()}

    all_keys = sorted(set(gamma_sym.keys()) | set(cob_sym.keys()))
    nrows = len(all_keys)
    ncols = len(phi_labels)
    ngb = len(gb_labels)
    phi_idx = {phi: j for j, phi in enumerate(phi_labels)}
    gb_idx = {gb: j for j, gb in enumerate(gb_labels)}

    # Augmented matrix [M | Gamma_sym] where Gamma_sym has columns indexed by gb_labels
    # Shape: nrows x (ncols + ngb)
    # Each row i: sum_j M[i][j] phi_j = sum_k Gamma[i][k] gb_k
    # Rearranged: [M | Gamma] * [phi; -gb] = 0, or M*phi = Gamma*gb

    # We want to find when the system M*phi = gamma*gb (parametric RHS) is consistent.
    # Consistency condition: Gamma*gb must lie in the column space of M for all relevant gb.

    # Approach: Do Gaussian elimination on [M | Gamma] (treating gb as RHS).
    # After elimination, rows with zero M-part give conditions: Gamma_row * gb = 0 (or non-zero).

    # Build [M | Gamma] with rational entries
    # M: nrows x ncols, Gamma: nrows x ngb
    total_cols = ncols + ngb
    aug = [[Fraction(0)] * total_cols for _ in range(nrows)]
    for i, key in enumerate(all_keys):
        if key in cob_sym:
            for phi, c in cob_sym[key].items():
                aug[i][phi_idx[phi]] = c
        if key in gamma_sym:
            for gb, c in gamma_sym[key].items():
                aug[i][ncols + gb_idx[gb]] = c

    # Gaussian elimination on first ncols columns
    pivot_col_for_row = {}
    row = 0
    for col in range(ncols):
        pivot = next((r for r in range(row, nrows) if aug[r][col]), None)
        if pivot is None:
            continue
        aug[row], aug[pivot] = aug[pivot], aug[row]
        pv = aug[row][col]
        aug[row] = [x / pv for x in aug[row]]
        for r in range(nrows):
            if r != row and aug[r][col]:
                f = aug[r][col]
                aug[r] = [aug[r][c] - f * aug[row][c] for c in range(total_cols)]
        pivot_col_for_row[row] = col
        row += 1

    rank = row
    # Rows after pivot rows: represent conditions on gb for consistency
    conditions = []
    for r in range(rank, nrows):
        gb_row = {gb_labels[j]: aug[r][ncols + j] for j in range(ngb) if aug[r][ncols + j]}
        if gb_row:
            conditions.append(gb_row)

    print(f"Coboundary rank: {rank}, free phi dims: {ncols - rank}")
    print(f"Number of gb-conditions for triviality: {len(conditions)}")

    if not conditions:
        print("Conclusion: The deformation is TRIVIAL for ALL gb values.")
        print("(The coboundary can match any gamma for any choice of gb.)")
    else:
        print("Conclusion: The deformation is NON-TRIVIAL for GENERIC gb values.")
        print("Necessary and sufficient conditions on gb for triviality:")
        for i, cond in enumerate(conditions[:10]):
            terms = ' + '.join(f'({v})*{gb}' for gb, v in sorted(cond.items()))
            print(f"  Condition {i+1}: {terms} = 0")
        if len(conditions) > 10:
            print(f"  ... ({len(conditions)} total conditions)")

    return conditions


if __name__ == '__main__':
    results = {}
    for n in [1, 2, 3]:
        consistent, sol, null_vecs, rank, M_dict, v_dict, all_keys, phi_labels = \
            analyze_triviality(n)
        results[n] = consistent
        investigate_general_gb(n)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for n, is_trivial in results.items():
        status = 'TRIVIAL' if is_trivial else 'NON-TRIVIAL'
        print(f"  C({n+1}) (n={n}): {status} for gb_assignment = all_1")

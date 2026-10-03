"""
C_triviality.py — Triviality condition analysis for C(n+1) deformation.

Determines conditions on gb parameters under which the inhomogeneous
deformation gamma is a coboundary (i.e., trivial).

gamma is trivial iff there exists an odd linear map f (phi matrix) such that:
  gamma(X,Y) = (delta f)(X,Y) for all X, Y.

This requires solving the linear system:
  sum_{i,j} phi_{ij} * (coboundary_coefficient_{XYZ}^{ij}) = gamma_evaluated_{XYZ}
  for all (X,Y,Z) triples.

We set up this as a matrix equation A * phi_vec = gamma_vec
and check solvability for the representative gb=+1 assignment, then
generalize to symbolic gb conditions.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_json(path):
    with open(path) as f:
        return json.load(f)


def build_gamma_vector(evaluated_gamma, triple_index):
    """gamma vector indexed by (X,Y,Z) triples."""
    vec = {}
    for entry in evaluated_gamma:
        key = (entry['X'], entry['Y'], entry['Z'])
        if key in triple_index:
            idx = triple_index[key]
            vec[idx] = vec.get(idx, Fraction(0)) + Fraction(entry['coeff'])
    return vec


def build_coboundary_matrix(coboundary_coeffs, triple_index, phi_index):
    """
    Build matrix A where A[triple_idx][phi_idx] = coboundary contribution.
    A * phi_vec = delta_f vector.
    """
    A = {}
    for entry in coboundary_coeffs:
        key = (entry['X'], entry['Y'], entry['Z'])
        if key not in triple_index:
            continue
        row = triple_index[key]
        phi_lbl = entry['phi_label']
        if phi_lbl not in phi_index:
            continue
        col = phi_index[phi_lbl]
        val = Fraction(entry['coeff'])
        A[(row, col)] = A.get((row, col), Fraction(0)) + val
    return A


def solve_linear_system(A, b, n_rows, n_cols):
    """
    Solve A * x = b over rationals using Gaussian elimination.
    Returns (solution_exists, rank_A, rank_augmented, free_variables, particular_solution).
    """
    # Build augmented matrix [A | b] as list of lists
    mat = [[Fraction(0)] * (n_cols + 1) for _ in range(n_rows)]
    for (r, c), v in A.items():
        mat[r][c] = v
    for r, v in b.items():
        mat[r][n_cols] = v

    # Gaussian elimination
    pivot_cols = []
    r = 0
    for c in range(n_cols):
        # Find pivot row
        pivot = None
        for rr in range(r, n_rows):
            if mat[rr][c] != 0:
                pivot = rr
                break
        if pivot is None:
            continue
        # Swap
        mat[r], mat[pivot] = mat[pivot], mat[r]
        pivot_cols.append(c)
        # Scale
        scale = mat[r][c]
        mat[r] = [x / scale for x in mat[r]]
        # Eliminate
        for rr in range(n_rows):
            if rr != r and mat[rr][c] != 0:
                factor = mat[rr][c]
                mat[rr] = [mat[rr][cc] - factor * mat[r][cc] for cc in range(n_cols + 1)]
        r += 1

    rank_A = r
    # Check consistency: find rows where all A-coefficients are zero but b != 0
    consistent = True
    for rr in range(n_rows):
        if all(mat[rr][c] == 0 for c in range(n_cols)) and mat[rr][n_cols] != 0:
            consistent = False
            break

    free_vars = [c for c in range(n_cols) if c not in pivot_cols]

    # Extract particular solution (free vars = 0)
    particular = [Fraction(0)] * n_cols
    for idx, c in enumerate(pivot_cols):
        particular[c] = mat[idx][n_cols]

    return consistent, rank_A, rank_A + (0 if consistent else 1), free_vars, particular


def analyze_triviality(n):
    s1 = load_json(os.path.join(DATA_DIR, f'C_{n}_structure.json'))
    s3 = load_json(os.path.join(DATA_DIR, f'C_{n}_evaluated.json'))
    s4 = load_json(os.path.join(DATA_DIR, f'C_{n}_coboundary.json'))

    basis = s1['basis']['odd'] + s1['basis']['even']

    # Build triple index from (X,Y,Z) appearing in either gamma or coboundary
    all_triples = set()
    for entry in s3['evaluated_gamma']:
        all_triples.add((entry['X'], entry['Y'], entry['Z']))
    for entry in s4['coboundary_coefficients']:
        all_triples.add((entry['X'], entry['Y'], entry['Z']))

    triple_index = {t: i for i, t in enumerate(sorted(all_triples))}
    n_rows = len(triple_index)

    # Build phi index
    phi_labels = list(s4['phi_matrix']['parameters'].keys())
    phi_index = {lbl: i for i, lbl in enumerate(phi_labels)}
    n_cols = len(phi_labels)

    # Build gamma vector
    gamma_vec = build_gamma_vector(s3['evaluated_gamma'], triple_index)

    # Build coboundary matrix
    A = build_coboundary_matrix(s4['coboundary_coefficients'], triple_index, phi_index)

    # Solve
    consistent, rank_A, rank_aug, free_vars, particular = solve_linear_system(
        A, gamma_vec, n_rows, n_cols)

    return {
        "n": n,
        "triple_count": n_rows,
        "phi_param_count": n_cols,
        "rank_A": rank_A,
        "gb_assignment": "all_plus_1",
        "trivial": consistent,
        "free_variables": len(free_vars),
        "note": (
            "Deformation is trivial (coboundary) for gb=+1" if consistent
            else "Deformation is NOT trivial (not a coboundary) for gb=+1"
        )
    }


def analyze_general_gb(n):
    """
    Analyze triviality for symbolic gb parameters.
    For each (X,Y,Z), gamma(X,Y)^Z = sum_{gb} c_{gb} * gb_{...}.
    Triviality requires: for each (X,Y,Z) and each gb label,
      sum_{i,j} phi_{ij} * cob_coeff_{XYZ}^{ij} = c_{gb} * gb_{...}

    Since coboundary is independent of gb parameters, the equation
    A * phi = gamma(gb) must be solvable for each gb assignment.

    Key structural observation: gamma(X,Y)^Z is linear in gb parameters.
    The deformation is trivial for gb iff:
      gamma(gb) lies in the image of A (the coboundary operator).

    For symbolic gb, we analyze which gb vectors are in Image(A).
    """
    s1 = load_json(os.path.join(DATA_DIR, f'C_{n}_structure.json'))
    s2 = load_json(os.path.join(DATA_DIR, f'C_{n}_gamma.json'))
    s4 = load_json(os.path.join(DATA_DIR, f'C_{n}_coboundary.json'))

    basis = s1['basis']['odd'] + s1['basis']['even']

    # Build triple index
    all_triples = set()
    for entry in s2['gamma_coefficients']:
        all_triples.add((entry['X'], entry['Y'], entry['Z']))
    for entry in s4['coboundary_coefficients']:
        all_triples.add((entry['X'], entry['Y'], entry['Z']))

    triple_index = {t: i for i, t in enumerate(sorted(all_triples))}
    n_rows = len(triple_index)

    phi_labels = list(s4['phi_matrix']['parameters'].keys())
    phi_index = {lbl: i for i, lbl in enumerate(phi_labels)}
    n_cols = len(phi_labels)

    # Build coboundary matrix (independent of gb)
    A = build_coboundary_matrix(s4['coboundary_coefficients'], triple_index, phi_index)

    # Build gamma matrix (gamma[triple_idx][gb_idx] = coefficient)
    gb_params = list(s2['gb_matrix']['parameters'].keys())
    gb_index = {lbl: i for i, lbl in enumerate(gb_params)}

    gamma_matrix = {}  # (triple_idx, gb_idx) -> Fraction
    for entry in s2['gamma_coefficients']:
        key = (entry['X'], entry['Y'], entry['Z'])
        if key in triple_index:
            row = triple_index[key]
            col = gb_index.get(entry['gb_label'])
            if col is not None:
                c = Fraction(entry['coeff'])
                gamma_matrix[(row, col)] = gamma_matrix.get((row, col), Fraction(0)) + c

    # Compute rank of A (coboundary image dimension)
    zero_b = {}
    consistent0, rank_A, _, free_vars_A, _ = solve_linear_system(
        A, zero_b, n_rows, n_cols)

    # For each gb_k direction, check if gamma(., ., .)^gb_k is in Image(A)
    gb_triviality = {}
    for gb_lbl, gb_idx in gb_index.items():
        gb_vec = {row: gamma_matrix.get((row, gb_idx), Fraction(0))
                  for row in range(n_rows)
                  if gamma_matrix.get((row, gb_idx), 0) != 0}

        consistent_k, rank_k, rank_aug_k, _, _ = solve_linear_system(
            A, gb_vec, n_rows, n_cols)
        gb_triviality[gb_lbl] = consistent_k

    return {
        "n": n,
        "rank_coboundary_A": rank_A,
        "triple_count": n_rows,
        "phi_param_count": n_cols,
        "gb_param_count": len(gb_params),
        "gb_triviality_by_direction": gb_triviality,
        "all_trivial": all(gb_triviality.values()),
        "trivial_directions": [k for k, v in gb_triviality.items() if v],
        "nontrivial_directions": [k for k, v in gb_triviality.items() if not v]
    }


def main():
    print("=" * 60)
    print("TRIVIALITY ANALYSIS FOR C(n+1) INHOMOGENEOUS DEFORMATION")
    print("=" * 60)

    results_concrete = {}
    results_general = {}

    for n in [1, 2, 3]:
        print(f"\n--- n={n}: C({n+1}) = osp(2|{2*n}) ---")

        # Concrete analysis (gb=+1)
        res = analyze_triviality(n)
        results_concrete[n] = res
        print(f"Concrete (gb=+1): trivial={res['trivial']}, "
              f"rank_A={res['rank_A']}, triples={res['triple_count']}, "
              f"phi_params={res['phi_param_count']}")
        print(f"  {res['note']}")

        # General analysis
        gen = analyze_general_gb(n)
        results_general[n] = gen
        print(f"Symbolic analysis: rank(coboundary A)={gen['rank_coboundary_A']}")
        print(f"  Trivial gb directions ({len(gen['trivial_directions'])}): "
              f"{gen['trivial_directions']}")
        print(f"  Non-trivial gb directions ({len(gen['nontrivial_directions'])}): "
              f"{gen['nontrivial_directions']}")
        print(f"  All gb directions trivial: {gen['all_trivial']}")

    # Save report
    report = {
        "generated_by": "src/C_triviality.py",
        "generation_date": str(date.today()),
        "concrete_analysis_gb_plus1": {str(n): v for n, v in results_concrete.items()},
        "general_gb_analysis": {str(n): v for n, v in results_general.items()}
    }
    path = os.path.join(DATA_DIR, 'C_triviality_report.json')
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nFull report saved to {path}")
    return report


if __name__ == "__main__":
    main()

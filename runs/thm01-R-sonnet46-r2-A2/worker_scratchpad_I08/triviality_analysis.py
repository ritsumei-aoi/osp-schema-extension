"""
Triviality analysis for C(n+1) deformations.

For each n in {1, 2, 3}:
  - Load Layer 2 gamma structure (symbolic, linear in gb)
  - Load Layer 4 coboundary structure (linear in phi)
  - Set up linear system: A * phi = b(gb)
  - Determine the conditions on gb for the system to have a solution (trivial deformation)

Triviality condition: gamma = delta_f
For fixed (X, Y, Z): sum_{phi} A_{(X,Y,Z), phi} * phi = gamma_{(X,Y,Z)}(gb)

The system is Ax = b(gb). It has a solution iff b(gb) in col(A),
i.e., for all v in left_null(A): v^T * b(gb) = 0.

Since b(gb) = M * gb (linear in gb):
  constraint on gb: (left_null(A)^T * M) * gb = 0

If left_null(A)^T * M = 0, the system always has a solution (trivial for all gb).
Otherwise, the condition is: M^T * left_null(A) * alpha = 0 for specific directions.
"""

import json
import numpy as np
from pathlib import Path
import sys

DATA_DIR = Path("<home>/notebook/git/thm01-R/thm01-R-sonnet46-r2-A2/data")

def load_json(path):
    with open(path) as f:
        return json.load(f)

def analyze_n(n):
    print(f"\n{'='*60}")
    print(f"  C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    gamma_data = load_json(DATA_DIR / f"C_{n}_gamma.json")
    coboundary_data = load_json(DATA_DIR / f"C_{n}_coboundary.json")
    evaluated_data = load_json(DATA_DIR / f"C_{n}_evaluated_allplus.json")

    # Extract all gb labels and phi labels from the data
    gb_labels = []
    for entry in gamma_data["gamma_structure"]:
        for term in entry["gamma_terms"]:
            lbl = term["gb_label"]
            if lbl not in gb_labels:
                gb_labels.append(lbl)
    gb_labels.sort()

    phi_labels = coboundary_data["map_f"]["phi_parameters"]["labels"] \
        if "labels" in coboundary_data["map_f"]["phi_parameters"] else \
        (coboundary_data["map_f"]["phi_parameters"]["odd_to_even"]["labels"] +
         coboundary_data["map_f"]["phi_parameters"]["even_to_odd"]["labels"])

    print(f"  gb parameters ({len(gb_labels)}): {gb_labels}")
    print(f"  phi parameters ({len(phi_labels)}): {len(phi_labels)} total")

    # Collect all (X, Y, Z) equation triples from coboundary + gamma
    # Coboundary gives: (delta_f)(X,Y)[Z] = sum phi_i * A_i
    # Gamma gives: gamma(X,Y)[Z] = sum gb_j * M_j

    # Index all (X,Y,Z) triples
    triples = set()

    # From coboundary: all (X,Y,Z) where delta_f has a non-zero term
    cob_map = {}  # (X,Y,Z) -> {phi_label: coeff}
    for entry in coboundary_data["coboundary_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["delta_f_terms"]:
            Z = term["Z"]
            phi = term["phi_label"]
            c = float(term["coeff"])
            key = (X, Y, Z)
            triples.add(key)
            cob_map.setdefault(key, {})[phi] = cob_map.get(key, {}).get(phi, 0.0) + c

    # From gamma: all (X,Y,Z) where gamma has a non-zero term
    gamma_map = {}  # (X,Y,Z) -> {gb_label: coeff}
    for entry in gamma_data["gamma_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["gamma_terms"]:
            Z = term["Z"]
            gb = term["gb_label"]
            c = float(term["coeff"])
            key = (X, Y, Z)
            triples.add(key)
            gamma_map.setdefault(key, {})[gb] = gamma_map.get(key, {}).get(gb, 0.0) + c

    triples = sorted(triples)
    print(f"  Total (X,Y,Z) constraint triples: {len(triples)}")

    # Build matrices A (coboundary) and M (gamma)
    # A[row, col] = coefficient of phi_labels[col] in (delta_f) for triples[row]
    # M[row, col] = coefficient of gb_labels[col] in gamma for triples[row]

    phi_idx = {p: i for i, p in enumerate(phi_labels)}
    gb_idx = {g: i for i, g in enumerate(gb_labels)}

    A = np.zeros((len(triples), len(phi_labels)))
    M = np.zeros((len(triples), len(gb_labels)))

    for row, triple in enumerate(triples):
        if triple in cob_map:
            for phi, c in cob_map[triple].items():
                A[row, phi_idx[phi]] = c
        if triple in gamma_map:
            for gb, c in gamma_map[triple].items():
                M[row, gb_idx[gb]] = c

    print(f"  Matrix A shape: {A.shape} (equations x phi_params)")
    print(f"  Matrix M shape: {M.shape} (equations x gb_params)")

    # Analyze A: find left null space (solutions to v^T A = 0)
    # Using SVD
    U, S, Vt = np.linalg.svd(A, full_matrices=True)
    rank_A = np.sum(S > 1e-9)
    print(f"  rank(A) = {rank_A} (out of {min(A.shape)})")
    print(f"  dim left_null(A) = {len(triples) - rank_A}")

    # Left null space of A: columns of U corresponding to zero singular values
    left_null_A = U[:, rank_A:]  # shape (len(triples), dim_left_null)
    print(f"  left_null_A shape: {left_null_A.shape}")

    # The triviality condition on gb:
    # For all v in left_null(A): v^T * M * gb = 0
    # This means: (left_null_A^T @ M) * gb = 0
    # Call C = left_null_A^T @ M  (shape: dim_left_null x len(gb))

    C = left_null_A.T @ M
    print(f"  Constraint matrix C = left_null(A)^T @ M shape: {C.shape}")

    # Reduce C to find actual constraints
    # Row-reduce C to find its row space
    Uc, Sc, Vct = np.linalg.svd(C, full_matrices=False)
    rank_C = np.sum(Sc > 1e-9)
    print(f"  rank(C) = {rank_C}")

    if rank_C == 0:
        print("  >> RESULT: The deformation is TRIVIAL for ALL gb values.")
        print("     (No constraint on gb is needed; coboundary image contains all gamma.)")
    else:
        print(f"  >> RESULT: The deformation is trivial only for gb in a codimension-{rank_C} subspace.")
        # The constraint is: Vct[:rank_C, :] @ gb = 0
        # i.e., the top rank_C right singular vectors of C give the constraints
        constraint_vectors = Vct[:rank_C, :]
        print(f"  Triviality constraints (C * gb = 0 where C has rank {rank_C}):")
        for i in range(rank_C):
            cv = constraint_vectors[i]
            terms = []
            for j, gb_lbl in enumerate(gb_labels):
                if abs(cv[j]) > 1e-9:
                    terms.append(f"{cv[j]:.4f}*{gb_lbl}")
            print(f"    Constraint {i+1}: {' + '.join(terms)} = 0")

        # Check allplus case
        gb_allplus = np.ones(len(gb_labels))
        violations = C @ gb_allplus
        max_viol = np.max(np.abs(violations))
        print(f"\n  Allplus check (all gb=1): max |C * gb_allplus| = {max_viol:.6e}")
        if max_viol < 1e-9:
            print("  >> allplus is in the trivial subspace (unexpected given rank_C > 0)")
        else:
            print("  >> allplus is NOT in the trivial subspace => allplus deformation is NON-TRIVIAL")

    # Special cases: zero gb (trivial)
    gb_zero = np.zeros(len(gb_labels))
    violations_zero = C @ gb_zero
    print(f"\n  Zero gb check: max |C * 0| = {np.max(np.abs(violations_zero)):.6e}")
    print("  >> gb=0 (no deformation) is always trivially trivial.")

    # Analyze the constraint structure more carefully
    if rank_C > 0:
        print(f"\n  Detailed constraint analysis:")
        # Find the minimal set of constraints
        # C * gb = 0 is a system in gb
        # Null space of C gives the trivial subspace
        Uc2, Sc2, Vct2 = np.linalg.svd(C)
        null_C = Vct2[rank_C:, :]  # null space of C
        print(f"  Trivial subspace dimension: {null_C.shape[0]} (out of {len(gb_labels)})")
        print(f"  Non-trivial directions: {rank_C}")

    return rank_C, gb_labels, C if 'C' in dir() else None

# Run for n = 1, 2, 3
results = {}
for n in [1, 2, 3]:
    rank_C, gb_labels, C = analyze_n(n)
    results[n] = {"rank_C": rank_C, "gb_labels": gb_labels, "C": C}

print("\n\n" + "="*60)
print("SUMMARY")
print("="*60)
for n in [1, 2, 3]:
    r = results[n]
    print(f"n={n}: C({n+1})=osp(2|{2*n}), {len(r['gb_labels'])} gb params, rank(constraint)={r['rank_C']}")
    if r['rank_C'] == 0:
        print(f"       => trivial for ALL gb")
    else:
        print(f"       => trivial only if gb lies in a codim-{r['rank_C']} subspace")

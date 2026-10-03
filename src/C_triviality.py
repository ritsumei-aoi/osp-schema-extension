"""
C_triviality.py

Triviality analysis for the inhomogeneous deformation of C(n+1) = osp(2|2n).

Compares Schema 3 (evaluated gamma with all gb=1) with the coboundary space
(Schema 4) to determine:
1. Whether the specific gb=1 deformation is trivial (= some coboundary delta f)
2. What conditions on the gb parameters make the general deformation trivial

Method:
  For gamma to be trivial, we need: gamma(X,Y) = (delta f)(X,Y) for all X,Y.
  This is a LINEAR SYSTEM in the phi parameters of f.

  We solve: sum_phi M_{(X,Y,Z), phi} * phi_val = gamma_eval_{(X,Y,Z)}
  where M is the coboundary matrix (from Schema 4) and gamma_eval is from Schema 3.
"""

from __future__ import annotations
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))


def load_schema(n: int, kind: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_{kind}.json")
    with open(path) as f:
        return json.load(f)


def build_triviality_system(n: int, gb_values: dict = None):
    """
    Build the linear system: M * phi_vec = gamma_vec
    to test whether the deformation is trivial.

    Returns (M, gamma_vec, phi_labels, xyz_keys) where:
    - M[row][col] = coefficient of phi_labels[col] in coboundary entry row
    - gamma_vec[row] = evaluated gamma value for that (X,Y,Z) triple
    - xyz_keys = list of (X,Y,Z) triples (rows)
    - phi_labels = list of phi parameter labels (columns)
    """
    schema3 = load_schema(n, "evaluated")
    schema4 = load_schema(n, "coboundary")
    schema1 = load_schema(n, "structure")

    basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    parity = schema1["parity"]

    phi_labels = schema4["f_map"]["phi_labels"]
    phi_to_col = {p: i for i, p in enumerate(phi_labels)}

    # Collect all (X,Y,Z) triples that appear in either gamma or coboundary
    all_triples = set()
    for e in schema3["evaluated_gamma"]:
        all_triples.add((e["X"], e["Y"], e["Z"]))
    for e in schema4["coboundary_coefficients"]:
        all_triples.add((e["X"], e["Y"], e["Z"]))

    xyz_keys = sorted(all_triples)
    triple_to_row = {t: i for i, t in enumerate(xyz_keys)}
    n_rows = len(xyz_keys)
    n_cols = len(phi_labels)

    # Build coboundary matrix M
    M = [[Fraction(0)] * n_cols for _ in range(n_rows)]
    for e in schema4["coboundary_coefficients"]:
        triple = (e["X"], e["Y"], e["Z"])
        row = triple_to_row[triple]
        col = phi_to_col[e["phi"]]
        M[row][col] += Fraction(e["coeff"])

    # Build gamma vector
    gamma_vec = [Fraction(0)] * n_rows
    for e in schema3["evaluated_gamma"]:
        triple = (e["X"], e["Y"], e["Z"])
        row = triple_to_row[triple]
        gamma_vec[row] += Fraction(e["coeff"])

    return M, gamma_vec, phi_labels, xyz_keys


def gaussian_elimination(M, b):
    """
    Solve linear system M*x = b using Gaussian elimination over Fractions.
    M: n_rows x n_cols matrix
    b: n_rows vector
    Returns (solution, is_consistent, rank) where solution may be None if inconsistent.
    """
    n_rows = len(M)
    n_cols = len(M[0])

    # Build augmented matrix [M | b]
    aug = [M[i][:] + [b[i]] for i in range(n_rows)]

    pivot_cols = []
    row = 0
    for col in range(n_cols):
        # Find pivot
        pivot_r = None
        for r in range(row, n_rows):
            if aug[r][col] != 0:
                pivot_r = r
                break
        if pivot_r is None:
            continue

        aug[row], aug[pivot_r] = aug[pivot_r], aug[row]
        pivot_val = aug[row][col]
        aug[row] = [v / pivot_val for v in aug[row]]
        pivot_cols.append(col)

        for r in range(n_rows):
            if r != row and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][c] - factor * aug[row][c] for c in range(n_cols + 1)]
        row += 1

    rank = len(pivot_cols)

    # Check consistency: rows beyond pivot with nonzero RHS
    for r in range(rank, n_rows):
        if aug[r][-1] != 0:
            return None, False, rank

    # Extract particular solution (free variables set to 0)
    solution = [Fraction(0)] * n_cols
    for i, col in enumerate(pivot_cols):
        solution[col] = aug[i][-1]

    return solution, True, rank


def analyze_triviality_specific(n: int) -> dict:
    """
    Analyze triviality for specific gb assignment (all gb=1).
    Returns analysis dict.
    """
    M, gamma_vec, phi_labels, xyz_keys = build_triviality_system(n)
    solution, is_consistent, rank = gaussian_elimination(M, gamma_vec)

    n_phi = len(phi_labels)
    n_constraints = len(xyz_keys)

    result = {
        "n": n,
        "algebra": f"C({n+1})",
        "gb_assignment": "all gb = +1",
        "n_constraints": n_constraints,
        "n_phi_params": n_phi,
        "coboundary_matrix_rank": rank,
        "is_trivial": is_consistent,
        "solution": None,
        "non_trivial_triples": [],
        "null_space_dimension": n_phi - rank
    }

    if is_consistent:
        # Find specific solution
        non_zero_phi = {phi_labels[i]: str(solution[i])
                        for i in range(n_phi) if solution[i] != 0}
        result["solution"] = non_zero_phi
    else:
        # Find which constraints are violated
        # Re-examine which (X,Y,Z) contribute to inconsistency
        result["non_trivial_triples"] = _find_inconsistent_constraints(M, gamma_vec, xyz_keys, rank)

    return result


def _find_inconsistent_constraints(M, b, xyz_keys, rank):
    """
    After Gaussian elimination reveals inconsistency, find which equations conflict.
    Returns list of (X,Y,Z,gamma_value) for inconsistent constraints.
    """
    n_rows = len(M)
    n_cols = len(M[0])

    aug = [M[i][:] + [b[i]] for i in range(n_rows)]
    row = 0
    for col in range(n_cols):
        pivot_r = None
        for r in range(row, n_rows):
            if aug[r][col] != 0:
                pivot_r = r
                break
        if pivot_r is None:
            continue
        aug[row], aug[pivot_r] = aug[pivot_r], aug[row]
        pivot_val = aug[row][col]
        aug[row] = [v / pivot_val for v in aug[row]]
        for r in range(n_rows):
            if r != row and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][c] - factor * aug[row][c] for c in range(n_cols + 1)]
        row += 1

    inconsistent = []
    for r in range(rank, n_rows):
        if aug[r][-1] != 0:
            # This row has 0 LHS but nonzero RHS
            inconsistent.append({
                "triple": xyz_keys[r],
                "gamma_value": str(aug[r][-1])
            })

    return inconsistent[:20]  # Return at most 20 examples


def analyze_general_triviality(n: int) -> dict:
    """
    Analyze what conditions on gb parameters make the deformation trivial.

    Strategy: Build the system symbolically in gb.
    For each (X,Y,Z) triple: (delta f)_{XYZ} = gamma_{XYZ}
    where gamma_{XYZ} = sum_gb coeff_{XYZ,gb} * gb_{...}

    For each gb parameter separately, check if the corresponding gamma component
    is in the image of the coboundary operator (coboundary matrix M).

    A general deformation gamma = sum_gb gb_{...} * gamma^{(gb)}(X,Y)
    is trivial iff each gamma^{(gb)} is independently in the coboundary space.
    """
    schema2 = load_schema(n, "gamma")
    schema4 = load_schema(n, "coboundary")
    schema1 = load_schema(n, "structure")

    basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    phi_labels = schema4["f_map"]["phi_labels"]
    phi_to_col = {p: i for i, p in enumerate(phi_labels)}

    # Collect all (X,Y,Z) triples
    all_triples = set()
    for e in schema2["gamma_coefficients"]:
        all_triples.add((e["X"], e["Y"], e["Z"]))
    for e in schema4["coboundary_coefficients"]:
        all_triples.add((e["X"], e["Y"], e["Z"]))

    xyz_keys = sorted(all_triples)
    triple_to_row = {t: i for i, t in enumerate(xyz_keys)}
    n_rows = len(xyz_keys)
    n_cols = len(phi_labels)

    # Coboundary matrix M (independent of gb)
    M = [[Fraction(0)] * n_cols for _ in range(n_rows)]
    for e in schema4["coboundary_coefficients"]:
        triple = (e["X"], e["Y"], e["Z"])
        row = triple_to_row.get(triple)
        if row is None:
            continue
        col = phi_to_col.get(e["phi"])
        if col is None:
            continue
        M[row][col] += Fraction(e["coeff"])

    # For each gb parameter, build the corresponding gamma vector
    gb_params = list(schema2["gb_matrix"]["parameters"].keys())
    gb_results = {}

    for gb in gb_params:
        gamma_vec = [Fraction(0)] * n_rows
        for e in schema2["gamma_coefficients"]:
            if e["gb"] != gb:
                continue
            triple = (e["X"], e["Y"], e["Z"])
            row = triple_to_row.get(triple)
            if row is None:
                continue
            gamma_vec[row] += Fraction(e["coeff"])

        # Check if this gamma^{(gb)} is in image of M
        _, is_consistent, _ = gaussian_elimination(M, gamma_vec)
        gb_results[gb] = is_consistent

    return {
        "n": n,
        "algebra": f"C({n+1})",
        "per_gb_analysis": gb_results,
        "all_trivial": all(gb_results.values()),
        "trivial_gb_params": [gb for gb, ok in gb_results.items() if ok],
        "non_trivial_gb_params": [gb for gb, ok in gb_results.items() if not ok]
    }


def main():
    print("=" * 65)
    print("C(n+1) Triviality Analysis")
    print("=" * 65)

    for n in [1, 2, 3]:
        print(f"\n{'='*30} C({n+1}) = osp(2|{2*n}), n={n} {'='*30}")

        # 1. Specific analysis (all gb = +1)
        print(f"\n[1] Specific analysis (all gb = +1):")
        res = analyze_triviality_specific(n)
        print(f"  Constraints (X,Y,Z triples): {res['n_constraints']}")
        print(f"  Phi parameters (f map):       {res['n_phi_params']}")
        print(f"  Coboundary matrix rank:        {res['coboundary_matrix_rank']}")
        print(f"  Null space dimension:          {res['null_space_dimension']}")
        if res["is_trivial"]:
            print(f"  Result: TRIVIAL (deformation is a coboundary)")
            if res["solution"]:
                print(f"  Non-zero phi values: {len(res['solution'])}")
                for k, v in list(res["solution"].items())[:5]:
                    print(f"    {k} = {v}")
        else:
            print(f"  Result: NON-TRIVIAL (deformation is NOT a coboundary)")
            if res["non_trivial_triples"]:
                print(f"  Sample inconsistent constraints:")
                for item in res["non_trivial_triples"][:5]:
                    print(f"    {item['triple']}: gamma={item['gamma_value']}")

        # 2. Per-gb analysis
        print(f"\n[2] Per-gb parameter triviality analysis:")
        gen_res = analyze_general_triviality(n)
        print(f"  Trivial components:     {gen_res['trivial_gb_params']}")
        print(f"  Non-trivial components: {gen_res['non_trivial_gb_params']}")
        all_triv = gen_res['all_trivial']
        print(f"  All gb trivial independently: {'YES' if all_triv else 'NO'}")

    print("\n" + "=" * 65)
    print("Analysis complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()

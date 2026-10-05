"""
C(n+1) = osp(2|2n) triviality condition search.

Compares Layer 3 (evaluated deformation gamma) with Layer 4 (coboundary δf)
to determine conditions under which the deformation is trivial, i.e.,
γ(X,Y) = (δf)(X,Y) for some odd linear map f.

This reduces to a linear system: for each (X,Y,Z), the evaluated gamma
coefficient must equal the sum of coboundary contributions from phi parameters.
"""

import json
import sys
import numpy as np
from fractions import Fraction
from datetime import date


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def build_triviality_system(n):
    """Build the linear system γ = δf.

    For each generator triple (X,Y,Z), we need:
      gamma_evaluated(X,Y,Z) = Σ_phi coboundary(X,Y,Z,phi) * phi_value

    This is a linear system A·φ = b where:
    - b is the vector of evaluated gamma coefficients
    - A is the coboundary coefficient matrix
    - φ is the vector of phi parameters to solve for
    """
    gamma_data = load_json(f"data/C_{n}_gamma.json")
    coboundary_data = load_json(f"data/C_{n}_coboundary.json")
    structure_data = load_json(f"data/C_{n}_structure.json")

    gb_params = gamma_data["gb_matrix"]["parameters"]
    phi_params = coboundary_data["odd_linear_map_f"]["parameters"]

    all_triples = set()
    for entry in gamma_data["gamma_coefficients"]:
        all_triples.add((entry["X"], entry["Y"], entry["Z"]))
    for entry in coboundary_data["coboundary_coefficients"]:
        all_triples.add((entry["X"], entry["Y"], entry["Z"]))

    triple_list = sorted(all_triples)
    triple_idx = {t: i for i, t in enumerate(triple_list)}
    phi_idx = {p: i for i, p in enumerate(phi_params)}

    n_triples = len(triple_list)
    n_phi = len(phi_params)
    n_gb = len(gb_params)

    gb_idx = {p: i for i, p in enumerate(gb_params)}
    B_matrix = np.zeros((n_triples, n_gb), dtype=float)
    for entry in gamma_data["gamma_coefficients"]:
        triple = (entry["X"], entry["Y"], entry["Z"])
        row = triple_idx[triple]
        col = gb_idx[entry["gb_param"]]
        B_matrix[row, col] += float(Fraction(entry["coeff"]))

    A_matrix = np.zeros((n_triples, n_phi), dtype=float)
    for entry in coboundary_data["coboundary_coefficients"]:
        triple = (entry["X"], entry["Y"], entry["Z"])
        row = triple_idx[triple]
        col = phi_idx[entry["phi_param"]]
        A_matrix[row, col] += float(Fraction(entry["coeff"]))

    return {
        "A": A_matrix,
        "B": B_matrix,
        "triple_list": triple_list,
        "phi_params": phi_params,
        "gb_params": gb_params,
        "n_triples": n_triples,
        "n_phi": n_phi,
        "n_gb": n_gb,
    }


def analyze_triviality(n):
    """Analyze whether γ = δf is solvable for all gb assignments."""
    system = build_triviality_system(n)
    A = system["A"]
    B = system["B"]

    print(f"\n  System dimensions: {system['n_triples']} equations, "
          f"{system['n_phi']} phi unknowns, {system['n_gb']} gb parameters")

    rank_A = np.linalg.matrix_rank(A, tol=1e-10)
    print(f"  rank(A) = {rank_A}")

    aug_ranks = []
    for j in range(system["n_gb"]):
        b_col = B[:, j:j+1]
        aug = np.hstack([A, b_col])
        rank_aug = np.linalg.matrix_rank(aug, tol=1e-10)
        aug_ranks.append(rank_aug)

    individual_solvable = []
    for j, param in enumerate(system["gb_params"]):
        if aug_ranks[j] == rank_A:
            individual_solvable.append(param)

    print(f"  Individual gb solvability: {len(individual_solvable)}/{system['n_gb']} parameters")
    for j, param in enumerate(system["gb_params"]):
        status = "SOLVABLE" if aug_ranks[j] == rank_A else f"UNSOLVABLE (rank={aug_ranks[j]})"
        print(f"    {param}: rank(A|b) = {aug_ranks[j]} -> {status}")

    b_all = B @ np.ones(system["n_gb"])
    aug_all = np.hstack([A, b_all.reshape(-1, 1)])
    rank_aug_all = np.linalg.matrix_rank(aug_all, tol=1e-10)
    all_plus_solvable = (rank_aug_all == rank_A)
    print(f"\n  All-plus profile: rank(A|b_all) = {rank_aug_all} -> "
          f"{'SOLVABLE (trivial)' if all_plus_solvable else 'UNSOLVABLE (non-trivial)'}")

    col_space_A = np.linalg.svd(A, full_matrices=False)
    U, S, Vt = col_space_A
    tol = 1e-10
    rank_eff = np.sum(S > tol)
    Q = U[:, :rank_eff]

    solvable_subspace_dim = 0
    for j in range(system["n_gb"]):
        b_col = B[:, j]
        proj = Q @ (Q.T @ b_col)
        residual = np.linalg.norm(b_col - proj)
        if residual < tol:
            solvable_subspace_dim += 1

    print(f"\n  Summary: {solvable_subspace_dim}/{system['n_gb']} gb directions are in col(A)")

    general_aug = np.hstack([A, B])
    rank_general = np.linalg.matrix_rank(general_aug, tol=1e-10)
    general_solvable = (rank_general == rank_A)
    print(f"  General solvability: rank(A|B) = {rank_general} -> "
          f"{'ALL gb trivial' if general_solvable else 'NOT all gb trivial'}")

    if not general_solvable:
        print(f"\n  The deformation is NON-TRIVIAL in general.")
        print(f"  rank(A) = {rank_A}, rank(A|B) = {rank_general}")
        print(f"  There are {rank_general - rank_A} independent constraints on gb "
              f"that cannot be matched by any coboundary.")

    return {
        "rank_A": rank_A,
        "rank_A_B": rank_general,
        "all_trivial": general_solvable,
        "individual_solvable": individual_solvable,
        "n_constraints": rank_general - rank_A if not general_solvable else 0,
    }


def find_trivial_subspace(n):
    """Find the subspace of gb parameters for which the deformation IS trivial."""
    system = build_triviality_system(n)
    A = system["A"]
    B = system["B"]

    U, S, Vt = np.linalg.svd(A, full_matrices=False)
    tol = 1e-10
    rank_A = np.sum(S > tol)
    Q = U[:, :rank_A]

    P_perp = np.eye(system["n_triples"]) - Q @ Q.T

    C = P_perp @ B

    U_c, S_c, Vt_c = np.linalg.svd(C, full_matrices=False)
    rank_C = np.sum(S_c > tol)

    if rank_C == 0:
        print(f"\n  All gb directions are trivial (C=0).")
        return system["n_gb"], []

    null_dim = system["n_gb"] - rank_C
    print(f"\n  Trivial subspace dimension: {null_dim} out of {system['n_gb']} gb parameters")
    print(f"  Non-trivial directions: {rank_C}")

    if rank_C > 0 and rank_C < system["n_gb"]:
        V_null = Vt_c[rank_C:, :]
        print(f"  Null space vectors (trivial gb combinations):")
        for i, v in enumerate(V_null):
            nonzero = [(system["gb_params"][j], round(v[j], 6))
                       for j in range(len(v)) if abs(v[j]) > tol]
            print(f"    v_{i+1}: {nonzero}")

    return null_dim, []


def main():
    for n in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"=== Triviality Analysis for C({n+1}) = osp(2|{2*n}) [n={n}] ===")
        print(f"{'='*60}")

        result = analyze_triviality(n)
        find_trivial_subspace(n)

    print(f"\n{'='*60}")
    print("Analysis complete.")


if __name__ == "__main__":
    main()

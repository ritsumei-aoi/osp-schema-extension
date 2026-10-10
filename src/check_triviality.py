"""
check_triviality.py — Triviality analysis for C(n+1) deformations.

For each n in {1, 2, 3}:
  - Load Layer 2 gamma structure (symbolic, linear in gb parameters)
  - Load Layer 4 coboundary structure (linear in phi parameters)
  - Set up the linear system:  A * phi = b(gb)
  - Determine the necessary and sufficient conditions on gb for a solution to exist

Mathematical framework
----------------------
The deformation gamma is trivial iff gamma = delta_f for some odd linear map f.
Writing f in the basis {Z_i} as f(Z_j) = sum_i phi_{ij} Z_i, the condition becomes:

    A * phi = b(gb)          (linear system in phi, with RHS linear in gb)

This system has a solution iff b(gb) lies in the column space of A, i.e.,
    for all v with v^T A = 0:  v^T b(gb) = 0.

Since b(gb) = M * gb (M is the gamma coefficient matrix, gb the parameter vector):
    C * gb = 0,    where C = left_null(A)^T @ M

is the necessary and sufficient triviality condition on gb.

Usage
-----
    python src/check_triviality.py [--data-dir <path>]

The default data directory is  data/  relative to the repository root.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def get_phi_labels(coboundary_data: dict) -> list[str]:
    phi_params = coboundary_data["map_f"]["phi_parameters"]
    if "labels" in phi_params:
        return phi_params["labels"]
    return (phi_params["odd_to_even"]["labels"] +
            phi_params["even_to_odd"]["labels"])


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def analyze_n(n: int, data_dir: Path) -> dict:
    """Analyse the triviality condition for C(n+1) = osp(2|2n)."""
    print(f"\n{'='*60}")
    print(f"  C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    gamma_data = load_json(data_dir / f"C_{n}_gamma.json")
    coboundary_data = load_json(data_dir / f"C_{n}_coboundary.json")

    # ---- collect gb and phi labels ----------------------------------------

    gb_labels: list[str] = []
    for entry in gamma_data["gamma_structure"]:
        for term in entry["gamma_terms"]:
            lbl = term["gb_label"]
            if lbl not in gb_labels:
                gb_labels.append(lbl)
    gb_labels.sort()

    phi_labels = get_phi_labels(coboundary_data)

    print(f"  gb parameters  ({len(gb_labels)}): {gb_labels}")
    print(f"  phi parameters ({len(phi_labels)}): {len(phi_labels)} total")

    # ---- collect (X, Y, Z) constraint triples ------------------------------

    cob_map: dict[tuple, dict[str, float]] = {}
    for entry in coboundary_data["coboundary_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["delta_f_terms"]:
            key = (X, Y, term["Z"])
            phi = term["phi_label"]
            cob_map.setdefault(key, {})[phi] = (
                cob_map.get(key, {}).get(phi, 0.0) + float(term["coeff"])
            )

    gamma_map: dict[tuple, dict[str, float]] = {}
    for entry in gamma_data["gamma_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["gamma_terms"]:
            key = (X, Y, term["Z"])
            gb = term["gb_label"]
            gamma_map.setdefault(key, {})[gb] = (
                gamma_map.get(key, {}).get(gb, 0.0) + float(term["coeff"])
            )

    triples = sorted(set(cob_map) | set(gamma_map))
    print(f"  Total (X,Y,Z) constraint triples: {len(triples)}")

    # ---- build matrices A (coboundary) and M (gamma) -----------------------

    phi_idx = {p: i for i, p in enumerate(phi_labels)}
    gb_idx  = {g: i for i, g in enumerate(gb_labels)}

    A = np.zeros((len(triples), len(phi_labels)))
    M = np.zeros((len(triples), len(gb_labels)))

    for row, triple in enumerate(triples):
        for phi, c in cob_map.get(triple, {}).items():
            A[row, phi_idx[phi]] = c
        for gb, c in gamma_map.get(triple, {}).items():
            M[row, gb_idx[gb]] = c

    print(f"  Matrix A shape: {A.shape}  (equations × phi_params)")
    print(f"  Matrix M shape: {M.shape}  (equations × gb_params)")

    # ---- SVD of A to find left null space ----------------------------------

    U, S, Vt = np.linalg.svd(A, full_matrices=True)
    rank_A = int(np.sum(S > 1e-9))
    dim_lnull = len(triples) - rank_A
    print(f"  rank(A) = {rank_A}  (out of {min(A.shape)})")
    print(f"  dim left_null(A) = {dim_lnull}")

    left_null_A = U[:, rank_A:]          # shape: (len(triples), dim_lnull)

    # ---- constraint matrix C -----------------------------------------------

    C = left_null_A.T @ M               # shape: (dim_lnull, len(gb_labels))
    print(f"  Constraint matrix C = left_null(A)^T @ M shape: {C.shape}")

    _Uc, Sc, Vct = np.linalg.svd(C, full_matrices=False)
    rank_C = int(np.sum(Sc > 1e-9))
    print(f"  rank(C) = {rank_C}")

    # ---- interpret results -------------------------------------------------

    if rank_C == 0:
        print("  >> RESULT: The deformation is TRIVIAL for ALL gb values.")
    else:
        print(f"  >> RESULT: trivial only when gb lies in a codimension-{rank_C} subspace.")
        print(f"  Triviality constraints (each entry of C * gb = 0):")
        for i in range(rank_C):
            cv = Vct[i]
            terms = [f"{cv[j]:+.4f}*{gb_labels[j]}"
                     for j in range(len(gb_labels)) if abs(cv[j]) > 1e-9]
            print(f"    Constraint {i+1}: {' '.join(terms)} = 0")

        # allplus check
        gb_allplus = np.ones(len(gb_labels))
        max_viol = float(np.max(np.abs(C @ gb_allplus)))
        print(f"\n  Allplus check (all gb=1): max|C * gb_allplus| = {max_viol:.6e}")
        label = "NON-TRIVIAL" if max_viol > 1e-9 else "trivial (unexpected)"
        print(f"  >> allplus deformation is {label}")

    # zero-gb check
    max_zero = float(np.max(np.abs(C @ np.zeros(len(gb_labels)))))
    print(f"\n  Zero gb check: max|C * 0| = {max_zero:.6e}  (always trivial)")

    # trivial subspace dimension
    null_dim = len(gb_labels) - rank_C
    print(f"\n  Trivial subspace dimension: {null_dim}  (out of {len(gb_labels)} gb params)")
    print(f"  Non-trivial directions:     {rank_C}")

    return {
        "n": n,
        "rank_A": rank_A,
        "rank_C": rank_C,
        "gb_labels": gb_labels,
        "phi_count": len(phi_labels),
        "triple_count": len(triples),
        "C": C,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).resolve().parent.parent / "data"),
        help="Directory containing C_n_*.json schema files (default: <repo>/data)",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.is_dir():
        print(f"Error: data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    results = {}
    for n in [1, 2, 3]:
        results[n] = analyze_n(n, data_dir)

    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for n in [1, 2, 3]:
        r = results[n]
        gb_dim = len(r["gb_labels"])
        rank_C = r["rank_C"]
        verdict = "trivial for ALL gb" if rank_C == 0 else f"trivial only if gb = 0  (codim-{rank_C} subspace = {{0}})"
        print(f"n={n}: C({n+1})=osp(2|{2*n}),  {gb_dim} gb params,  rank(C)={rank_C}  =>  {verdict}")


if __name__ == "__main__":
    main()

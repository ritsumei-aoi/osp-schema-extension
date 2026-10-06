#!/usr/bin/env python3
"""
src/triviality_search.py

Triviality condition search for C(n+1) = osp(2|2n).

The deformation gamma (Layer 3, all gb=1) is trivial iff there exists an
odd linear map f: g -> g such that

    gamma_eval(X, Y; Z) = (delta f)(X, Y; Z)   for all X, Y, Z in basis.

This is a linear system  A * phi = b  over Q where:
  - phi  = vector of all phi parameters from Schema 4
  - A_{(X,Y,Z), phi_k} = coboundary coefficient from Schema 4
  - b_{(X,Y,Z)}        = kappa coefficient from Schema 3

We solve this system using exact (Fraction) Gaussian elimination and report:
  - Is the system consistent?
  - If not, which constraints are violated?
  - The dimension of the solution space (if consistent).
"""

import json
import os
from fractions import Fraction


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n: int):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as f:
        s3 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as f:
        s4 = json.load(f)
    return s1, s3, s4


# ── Gaussian elimination over Q ───────────────────────────────────────────────

def rref(A, b):
    """
    Reduced row echelon form of [A | b] over Q (exact arithmetic).
    Returns (pivot_cols, is_consistent, solution_dim, inconsistent_rows).

    inconsistent_rows: list of (row_idx, b_val) for rows where A_row = 0, b != 0.
    solution_dim: dim(null space) = n_cols - rank(A).
    """
    m = len(A)           # number of equations
    n = len(A[0])        # number of variables
    # Work on augmented matrix
    M = [list(A[i]) + [b[i]] for i in range(m)]

    pivot_cols = []
    row = 0
    for col in range(n):
        # Find pivot
        pivot = None
        for r in range(row, m):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        M[row], M[pivot] = M[pivot], M[row]
        # Scale
        sc = M[row][col]
        M[row] = [x / sc for x in M[row]]
        # Eliminate
        for r in range(m):
            if r != row and M[r][col] != 0:
                fac = M[r][col]
                M[r] = [M[r][c] - fac * M[row][c] for c in range(n + 1)]
        pivot_cols.append(col)
        row += 1

    rank = len(pivot_cols)
    solution_dim = n - rank

    # Check consistency
    inconsistent_rows = []
    for r in range(rank, m):
        if M[r][n] != 0:
            inconsistent_rows.append((r, M[r][n]))

    is_consistent = len(inconsistent_rows) == 0
    return pivot_cols, is_consistent, solution_dim, inconsistent_rows, M


def analyze(n: int):
    s1, s3, s4 = load(n)

    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    parity = {k: int(v) for k, v in s1["parity"].items()}

    # ── phi parameter index ───────────────────────────────────────────────────
    phi_list = (
        [e["phi"] for e in s4["f_parametrization"]["phi_eo_labels"]] +
        [e["phi"] for e in s4["f_parametrization"]["phi_oe_labels"]]
    )
    phi_idx = {p: i for i, p in enumerate(phi_list)}
    n_phi = len(phi_list)

    # ── Build b: gamma_eval values from Schema 3 kappa part ──────────────────
    gamma_eval: dict = {}   # (X,Y,Z) -> Fraction
    for e in s3["kappa_structure_constants"]:
        key = (e["X"], e["Y"], e["Z"])
        gamma_eval[key] = gamma_eval.get(key, Fraction(0)) + Fraction(e["coeff"])

    # ── Build A: coboundary coefficients from Schema 4 ────────────────────────
    cob_coeffs: dict = {}  # (X,Y,Z) -> {phi_lbl: Fraction}
    for e in s4["coboundary_entries"]:
        key = (e["X"], e["Y"], e["Z"])
        cob_coeffs.setdefault(key, {})
        for t in e["phi_terms"]:
            cob_coeffs[key][t["phi"]] = (
                cob_coeffs[key].get(t["phi"], Fraction(0)) + Fraction(t["scalar"])
            )

    # ── All equation rows: union of gamma_eval keys and cob_coeffs keys ──────
    all_rows = sorted(set(gamma_eval.keys()) | set(cob_coeffs.keys()))
    n_rows = len(all_rows)
    row_idx = {r: i for i, r in enumerate(all_rows)}

    # Build A matrix and b vector
    A = [[Fraction(0)] * n_phi for _ in range(n_rows)]
    b = [Fraction(0)] * n_rows
    for key, coeffs in cob_coeffs.items():
        r = row_idx[key]
        for phi_lbl, c in coeffs.items():
            A[r][phi_idx[phi_lbl]] = c
    for key, val in gamma_eval.items():
        r = row_idx[key]
        b[r] = val

    # Separate rows into three classes before solving
    rows_gamma_only = [(key, b[row_idx[key]]) for key in all_rows
                       if key in gamma_eval and key not in cob_coeffs]
    rows_cob_only   = [key for key in all_rows
                       if key not in gamma_eval and key in cob_coeffs]
    rows_both       = [key for key in all_rows
                       if key in gamma_eval and key in cob_coeffs]

    # ── Solve ─────────────────────────────────────────────────────────────────
    pivot_cols, is_consistent, solution_dim, incons_rows, M = rref(A, b)

    return {
        "n": n,
        "n_phi": n_phi,
        "n_rows": n_rows,
        "n_gamma_eval": len(gamma_eval),
        "n_cob_entries": len(cob_coeffs),
        "rows_gamma_only": rows_gamma_only,
        "rows_cob_only_count": len(rows_cob_only),
        "rows_both_count": len(rows_both),
        "rank": len(pivot_cols),
        "solution_dim": solution_dim,
        "is_consistent": is_consistent,
        "n_inconsistent": len(incons_rows),
        "incons_rows": incons_rows,
        "M": M,
        "all_rows": all_rows,
        "gamma_eval": gamma_eval,
        "cob_coeffs": cob_coeffs,
        "phi_list": phi_list,
    }


def report(res: dict):
    n = res["n"]
    print(f"\n{'='*65}")
    print(f"C({n+1}) = osp(2|{2*n}),  n={n}")
    print(f"{'='*65}")
    print(f"  phi parameters          : {res['n_phi']}")
    print(f"  equation rows total     : {res['n_rows']}")
    print(f"    gamma_eval only (b≠0, A=0): {len(res['rows_gamma_only'])}")
    print(f"    coboundary only (b=0, A≠0): {res['rows_cob_only_count']}")
    print(f"    both (b≠0, A≠0)           : {res['rows_both_count']}")
    print(f"  rank(A)                 : {res['rank']}")
    print(f"  solution_dim (null(A))  : {res['solution_dim']}")
    print(f"  Consistent?             : {'YES' if res['is_consistent'] else 'NO'}")
    print(f"  Inconsistent equations  : {res['n_inconsistent']}")

    if res["rows_gamma_only"]:
        print(f"\n  *** STRUCTURAL OBSTRUCTION: {len(res['rows_gamma_only'])} rows "
              f"with gamma_eval ≠ 0 but no coboundary term ***")
        print("  These (X, Y, Z) entries make the system structurally inconsistent:")
        for (X, Y, Z), val in res["rows_gamma_only"][:8]:
            print(f"    gamma_eval({X},{Y};{Z}) = {val}  [no phi terms in coboundary]")
        if len(res["rows_gamma_only"]) > 8:
            print(f"    ... ({len(res['rows_gamma_only'])-8} more)")


def compare_support(n: int):
    """
    Report which (X,Y,Z) triples appear in gamma_eval but NOT in coboundary.
    These are the structural obstructions.
    """
    _, s3, s4 = load(n)
    gamma_eval = {(e["X"], e["Y"], e["Z"]) for e in s3["kappa_structure_constants"]}
    cob_support = {(e["X"], e["Y"], e["Z"]) for e in s4["coboundary_entries"]}
    only_gamma = sorted(gamma_eval - cob_support)
    only_cob   = sorted(cob_support - gamma_eval)
    both       = sorted(gamma_eval & cob_support)
    return only_gamma, only_cob, both


def main():
    results = []
    for n in [1, 2, 3]:
        res = analyze(n)
        report(res)
        results.append(res)

    # Detailed obstruction analysis for n=1
    print(f"\n{'='*65}")
    print("DETAILED OBSTRUCTION ANALYSIS  (n=1)")
    print(f"{'='*65}")
    only_gamma, only_cob, both = compare_support(1)
    print(f"  (X,Y,Z) in gamma_eval only (obstructions): {len(only_gamma)}")
    print(f"  (X,Y,Z) in coboundary only (constraints) : {len(only_cob)}")
    print(f"  (X,Y,Z) in both                          : {len(both)}")
    print()
    print("  Sample obstructions (first 12):")
    for (X, Y, Z) in only_gamma[:12]:
        res1 = results[0]
        val = res1["gamma_eval"].get((X, Y, Z), Fraction(0))
        print(f"    gamma_eval({X}, {Y}; {Z}) = {val}")

    # Classify obstructions by (X parity, Y parity, Z parity)
    s1_n1, s3_n1, _ = load(1)
    par = {k: int(v) for k, v in s1_n1["parity"].items()}
    parity_classes: dict = {}
    for (X, Y, Z) in only_gamma:
        cls = (par[X], par[Y], par[Z])
        parity_classes.setdefault(cls, []).append((X, Y, Z))
    print()
    print("  Obstruction parity classes (px, py, pz): count")
    for cls, lst in sorted(parity_classes.items()):
        print(f"    {cls}: {len(lst)}")

    # Summary table
    print(f"\n{'='*65}")
    print("SUMMARY TABLE")
    print(f"{'='*65}")
    print(f"{'n':>3}  {'phi':>5}  {'rows':>5}  {'rank':>5}  "
          f"{'sol_dim':>7}  {'consist':>8}  {'obstr':>6}")
    for res in results:
        print(f"  {res['n']:>1}  {res['n_phi']:>5}  {res['n_rows']:>5}  "
              f"{res['rank']:>5}  {res['solution_dim']:>7}  "
              f"{'YES' if res['is_consistent'] else 'NO':>8}  "
              f"{len(res['rows_gamma_only']):>6}")

    print()
    if all(not r["is_consistent"] and r["rows_gamma_only"] for r in results):
        print("CONCLUSION: The deformation is NON-TRIVIAL for all n=1,2,3.")
        print("  The gamma_eval (all gb=1) lies OUTSIDE the image of delta.")
    elif all(r["is_consistent"] for r in results):
        print("CONCLUSION: The deformation IS TRIVIAL for all n=1,2,3.")
    else:
        print("CONCLUSION: Mixed results across n values.")


if __name__ == "__main__":
    main()

"""
I08: Triviality search for C(n+1) inhomogeneous deformation.

Compares Schema 3 (evaluated gamma) and Schema 4 (coboundary) to determine
whether the deformation is trivial (coboundary) for various gb parameter choices.

The deformation gamma_gb is trivial iff there exists an odd map f such that
(delta f)(X,Y) = gamma_gb(X,Y) for all X,Y in g.

Linear algebra setup:
  A * phi = B * gb
where A is the coboundary matrix (from Schema 4) and B is the gamma matrix (from Schema 2).
"""

from __future__ import annotations
import json
from fractions import Fraction


def load_schemas(n: int):
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        s4 = json.load(f)
    return s1, s2, s4


def analyze_n(n: int) -> dict:
    s1, s2, s4 = load_schemas(n)
    parity = s1["parity"]
    basis = s1["basis"]["even"] + s1["basis"]["odd"]

    # Collect all (X, Y, Z) keys that appear in either gamma or coboundary
    eqn_keys_set = set()

    # From Schema 2 (gamma)
    gb_params = sorted(set(e["gb_param"] for e in s2["gamma_coefficients"]))

    # Build gamma matrix B: rows = (X,Y,Z) keys, cols = gb params
    gamma_data: dict[tuple[str,str,str], dict[str, Fraction]] = {}
    for e in s2["gamma_coefficients"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        gb = e["gb_param"]
        c = Fraction(e["coeff"])
        key = (X, Y, Z)
        eqn_keys_set.add(key)
        if key not in gamma_data:
            gamma_data[key] = {}
        gamma_data[key][gb] = gamma_data[key].get(gb, Fraction(0)) + c

    # From Schema 4 (coboundary)
    phi_params = sorted(set(e["phi_param"] for e in s4["coboundary_coefficients"]))

    cob_data: dict[tuple[str,str,str], dict[str, Fraction]] = {}
    for e in s4["coboundary_coefficients"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        phi = e["phi_param"]
        c = Fraction(e["coeff"])
        key = (X, Y, Z)
        eqn_keys_set.add(key)
        if key not in cob_data:
            cob_data[key] = {}
        cob_data[key][phi] = cob_data[key].get(phi, Fraction(0)) + c

    eqn_keys = sorted(eqn_keys_set)
    n_eqns = len(eqn_keys)
    n_phi = len(phi_params)
    n_gb = len(gb_params)

    print(f"\n=== n={n}: dim={len(basis)}, phi_params={n_phi}, gb_params={n_gb}, equations={n_eqns} ===")

    # Build the coboundary matrix A (n_eqns x n_phi) over rationals
    phi_idx = {p: i for i, p in enumerate(phi_params)}
    gb_idx = {g: i for i, g in enumerate(gb_params)}
    eqn_idx = {k: i for i, k in enumerate(eqn_keys)}

    # Use Gaussian elimination over Q for exactness
    # Build augmented matrix [A | B] where A is coboundary, B is gamma (negated on RHS)
    # System: A * phi = B * gb, i.e., A * phi - B * gb = 0

    # We check: for each column of B (one gb direction), does A * phi = b_gb have a solution?
    # This is equivalent to: rank([A | b_gb]) = rank(A).

    # Build A as list of lists of Fraction
    A = [[Fraction(0)] * n_phi for _ in range(n_eqns)]
    B = [[Fraction(0)] * n_gb for _ in range(n_eqns)]

    for key, phi_dict in cob_data.items():
        i = eqn_idx[key]
        for phi, c in phi_dict.items():
            j = phi_idx[phi]
            A[i][j] += c

    for key, gb_dict in gamma_data.items():
        i = eqn_idx[key]
        for gb, c in gb_dict.items():
            j = gb_idx[gb]
            B[i][j] += c

    # Gaussian elimination over Q to compute rank(A) and rank([A|B])
    def rref_rational(mat, ncols_a, ncols_total):
        """Row reduce mat in place. Returns rank of first ncols_a columns."""
        nr = len(mat)
        nc = ncols_total
        rank_a = 0
        pivot_col = 0
        pivot_row = 0
        while pivot_row < nr and pivot_col < ncols_a:
            # Find pivot
            found = -1
            for r in range(pivot_row, nr):
                if mat[r][pivot_col] != 0:
                    found = r
                    break
            if found == -1:
                pivot_col += 1
                continue
            # Swap
            mat[pivot_row], mat[found] = mat[found], mat[pivot_row]
            # Scale
            inv = Fraction(1) / mat[pivot_row][pivot_col]
            for c in range(nc):
                mat[pivot_row][c] *= inv
            # Eliminate
            for r in range(nr):
                if r != pivot_row and mat[r][pivot_col] != 0:
                    factor = mat[r][pivot_col]
                    for c in range(nc):
                        mat[r][c] -= factor * mat[pivot_row][c]
            rank_a += 1
            pivot_row += 1
            pivot_col += 1
        return rank_a

    # Build [A | B] as full matrix
    AB = [A[i][:] + B[i][:] for i in range(n_eqns)]
    rank_a = rref_rational(AB, n_phi, n_phi + n_gb)

    # After RREF of A, check if B columns are in the image of A
    # After elimination, any row where A-part is all-zero but B-part is nonzero = inconsistency
    inconsistencies = []
    for i, row in enumerate(AB):
        a_part = row[:n_phi]
        b_part = row[n_phi:]
        if all(c == 0 for c in a_part) and any(c != 0 for c in b_part):
            # Find which gb direction this inconsistency affects
            for j, gb in enumerate(gb_params):
                if b_part[j] != 0:
                    inconsistencies.append((i, gb, b_part[j]))

    # Also compute rank of A alone
    A_only = [A[i][:] for i in range(n_eqns)]
    rank_A_only = rref_rational(A_only, n_phi, n_phi)

    print(f"  rank(A) = {rank_A_only}")
    print(f"  Inconsistencies (equations with A-zero but B-nonzero): {len(inconsistencies)}")

    if not inconsistencies:
        print(f"  TRIVIAL: The deformation is trivial for all gb — lies in image of coboundary map.")
        trivial = True
    else:
        print(f"  NON-TRIVIAL: {len(inconsistencies)} constraint(s) violated:")
        for idx, (row_i, gb, coeff) in enumerate(inconsistencies[:10]):
            print(f"    gb={gb}, row={row_i}, coeff={coeff}")
        trivial = False

    # Structural analysis: which gb directions cause non-triviality?
    bad_gb = sorted(set(gb for _, gb, _ in inconsistencies))
    good_gb = [gb for gb in gb_params if gb not in bad_gb]

    if not trivial:
        print(f"  Non-trivial gb directions: {bad_gb}")
        print(f"  Potentially trivial gb directions: {good_gb}")

    return {
        "n": n,
        "trivial": trivial,
        "rank_A": rank_A_only,
        "n_phi": n_phi,
        "n_gb": n_gb,
        "n_equations": n_eqns,
        "inconsistencies": len(inconsistencies),
        "bad_gb": bad_gb,
        "good_gb": good_gb
    }


def main():
    all_results = []
    for n in [1, 2, 3]:
        r = analyze_n(n)
        all_results.append(r)

    print("\n=== Summary ===")
    for r in all_results:
        status = "TRIVIAL" if r["trivial"] else f"NON-TRIVIAL ({r['inconsistencies']} violations)"
        print(f"  n={r['n']}: {status}, rank(A)={r['rank_A']}, phi={r['n_phi']}, gb={r['n_gb']}")

    print("\n=== Conjecture ===")
    trivial_ns = [r["n"] for r in all_results if r["trivial"]]
    nontrivial_ns = [r["n"] for r in all_results if not r["trivial"]]

    if not nontrivial_ns:
        print("All tested cases (n=1,2,3) are trivial.")
        print("Conjecture: The inhomogeneous deformation of C(n+1) is ALWAYS TRIVIAL.")
        print("Every gamma_gb lies in the image of the coboundary map delta.")
    else:
        for r in all_results:
            if not r["trivial"]:
                print(f"n={r['n']}: non-trivial gb directions: {r['bad_gb']}")
        all_bad = set()
        for r in all_results:
            all_bad.update(r.get("bad_gb", []))
        print(f"\nConsistently non-trivial gb directions across n: patterns suggest structural obstruction.")
        print(f"Conjecture: The deformation is trivial iff the following gb directions vanish: {sorted(all_bad)[:8]}...")


if __name__ == "__main__":
    main()

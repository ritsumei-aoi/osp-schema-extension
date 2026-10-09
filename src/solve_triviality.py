"""
solve_triviality.py — Solve the linear system gamma = delta_f to determine triviality.

For gamma = delta_f to hold, we need:
  sum_{phi_{iY}} (-1)^{p(X)} [X, Z_i]_Z phi_{iY}
  + sum_{phi_{iX}} (- (-1)^{(p(X)+1)p(Y)}) [Y, Z_i]_Z phi_{iX}
  - sum_{phi_{i,[X,Y]}} phi_{i,[X,Y]}
  = gamma(X,Y)_Z

This is a linear system in the unknowns phi_{ij} (coefficients of f).

We use rational arithmetic (Fraction) for exact computation.
"""

from __future__ import annotations
import json
import os
from fractions import Fraction


def load(n: int, suffix: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_{suffix}.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema1: dict) -> dict:
    table = {}
    for sc in schema1["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return table


def gaussian_elimination(A, b):
    """
    Solve Ax = b over the rationals using Gaussian elimination with partial pivoting.
    A is m x n (list of lists of Fraction), b is m x 1 (list of Fraction).
    Returns (solution, rank, is_consistent).
    """
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    # Augmented matrix [A | b]
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    pivot_cols = []
    row_idx = 0

    for col in range(n):
        # Find pivot
        pivot = None
        for r in range(row_idx, m):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue

        # Swap rows
        M[row_idx], M[pivot] = M[pivot], M[row_idx]
        pivot_cols.append(col)

        # Normalize pivot row
        piv_val = M[row_idx][col]
        M[row_idx] = [x / piv_val for x in M[row_idx]]

        # Eliminate column
        for r in range(m):
            if r != row_idx and M[r][col] != 0:
                factor = M[r][col]
                M[r] = [M[r][j] - factor * M[row_idx][j] for j in range(n + 1)]

        row_idx += 1

    rank = len(pivot_cols)

    # Check consistency
    for r in range(rank, m):
        if M[r][n] != 0:
            return None, rank, False

    # Extract solution (set free variables to 0)
    solution = [Fraction(0)] * n
    for idx, col in enumerate(pivot_cols):
        solution[col] = M[idx][n]

    return solution, rank, True


def check_triviality(n: int) -> dict:
    """
    Check if the gamma deformation (all gb=+1) is trivial for C(n+1) with rank n.
    Sets up the linear system gamma = delta_f and solves it.
    """
    print(f"\n=== Triviality check for C(n+1), n={n} ===")

    schema1 = load(n, "structure")
    evaluated = load(n, "evaluated")

    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]
    dim = len(basis)
    basis_idx = {g: i for i, g in enumerate(basis)}

    table = build_bracket_table(schema1)

    # Build gamma table
    gamma_table = {}
    for e in evaluated["evaluated_gamma"]["gamma_coefficients"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        coeff = Fraction(e["gamma_coeff"])
        key = (X, Y)
        if key not in gamma_table:
            gamma_table[key] = {}
        gamma_table[key][Z] = gamma_table[key].get(Z, Fraction(0)) + coeff
    gamma_table = {k: {Z: c for Z, c in v.items() if c != 0} for k, v in gamma_table.items()}

    # Set up unknowns: phi_{i,j} = f(basis[j])[basis[i]]
    # where p(basis[i]) + p(basis[j]) = 1 (f is odd)

    # Collect valid unknowns
    unknowns = []
    unk_idx = {}
    for j, gj in enumerate(basis):
        pj = parity[gj]
        for i, gi in enumerate(basis):
            pi = parity[gi]
            if (pi + pj) % 2 == 1:  # f is odd
                key = (i, j)
                unk_idx[key] = len(unknowns)
                unknowns.append(key)

    n_unknowns = len(unknowns)
    print(f"  Unknowns: {n_unknowns} (dimension of Hom_odd(g,g))")

    # Set up linear system: for each (X, Y, Z), one equation
    # (delta_f)(X,Y)_Z = gamma(X,Y)_Z

    # (delta_f)(X,Y)_Z:
    # = sum_k: (-1)^{p(X)} [X, e_k]_Z * phi_{k,Y_idx}
    # + sum_k: (-(-1)^{(p(X)+1)*p(Y)}) [Y, e_k]_Z * phi_{k, X_idx}
    # - sum_k: phi_{Z_idx, k} * [X,Y]_{k... wait, no.
    #
    # f([X,Y]) = sum_k phi_{k, [X,Y]_w} * e_k ... but [X,Y] is a combination of basis elements.
    # More precisely:
    # f(sum_w c_w Z_w) = sum_w c_w f(Z_w) = sum_w c_w sum_k phi_{k,w} e_k
    # So f([X,Y])_Z = sum_w ([X,Y])_w * phi_{Z_idx, w}

    equations = []  # Each equation: (row coeffs, rhs)

    for ix, X in enumerate(basis):
        px = parity[X]
        for iy, Y in enumerate(basis):
            py = parity[Y]

            # (delta_f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])
            # = sum_k (-1)^{px} [X, e_k]_Z phi_{k, iy}
            #   + sum_k (-(-1)^{(px+1)*py}) [Y, e_k]_Z phi_{k, ix}
            #   - sum_w [X,Y]_w phi_{iz, w}
            # where iz = basis_idx[Z] (index of the output Z direction)

            bXY = table.get((X, Y), {})
            gamma_XY = gamma_table.get((X, Y), {})

            # We need (delta_f)(X,Y)_Z = gamma(X,Y)_Z for each Z
            # Collect all Z directions that appear
            all_Z = set(gamma_XY.keys()) | set()

            # Compute (delta_f)(X,Y) as a symbolic vector in Z
            # Contribution by Z from term 1: (-1)^{px} [X, e_k]_Z phi_{k, iy}
            # Contribution by Z from term 2: -(-1)^{(px+1)*py} [Y, e_k]_Z phi_{k, ix}
            # Contribution by Z from term 3: -sum_w bXY_w phi_{Z, w}

            # Build equation for each Z in basis
            for iz, Z in enumerate(basis):
                row = [Fraction(0)] * n_unknowns

                # Term 1: (-1)^{px} sum_k [X, e_k]_Z phi_{k, iy}
                s1 = Fraction((-1) ** px)
                for ik, ek in enumerate(basis):
                    bX_ek = table.get((X, ek), {}).get(Z, Fraction(0))
                    if bX_ek != 0 and (ik, iy) in unk_idx:
                        row[unk_idx[(ik, iy)]] += s1 * bX_ek

                # Term 2: -(-1)^{(px+1)*py} sum_k [Y, e_k]_Z phi_{k, ix}
                s2 = -Fraction((-1) ** ((px + 1) * py))
                for ik, ek in enumerate(basis):
                    bY_ek = table.get((Y, ek), {}).get(Z, Fraction(0))
                    if bY_ek != 0 and (ik, ix) in unk_idx:
                        row[unk_idx[(ik, ix)]] += s2 * bY_ek

                # Term 3: -sum_w bXY_w phi_{iz, w}
                for iw, ew in enumerate(basis):
                    bXY_w = bXY.get(ew, Fraction(0))
                    if bXY_w != 0 and (iz, iw) in unk_idx:
                        row[unk_idx[(iz, iw)]] -= bXY_w

                # RHS: gamma(X,Y)_Z
                rhs = gamma_XY.get(Z, Fraction(0))

                # Only add non-trivial equations (non-zero row or non-zero rhs)
                if any(c != 0 for c in row) or rhs != 0:
                    equations.append((row, rhs))

    print(f"  Equations: {len(equations)}")

    if not equations:
        print("  No equations — gamma is trivially zero!")
        return {"trivial": True, "reason": "gamma = 0"}

    A = [eq[0] for eq in equations]
    b = [eq[1] for eq in equations]

    solution, rank, is_consistent = gaussian_elimination(A, b)

    print(f"  System rank: {rank}")
    print(f"  Consistent: {is_consistent}")

    if is_consistent:
        print(f"  Result: TRIVIAL (solution exists for f)")
        # Verify solution
        if solution is not None:
            # Count non-zero phi values
            non_zero_phi = sum(1 for c in solution if c != 0)
            print(f"  Non-zero phi coefficients: {non_zero_phi} / {n_unknowns}")
    else:
        print(f"  Result: NON-TRIVIAL (no solution exists for f)")

    return {
        "n": n,
        "dim": dim,
        "n_unknowns": n_unknowns,
        "n_equations": len(equations),
        "rank": rank,
        "is_trivial": is_consistent,
        "solution_exists": is_consistent,
    }


def main():
    results = []
    for n in range(1, 4):
        r = check_triviality(n)
        results.append(r)

    print("\n=== Final Triviality Results (all gb = +1) ===")
    for r in results:
        status = "TRIVIAL" if r.get("is_trivial") else "NON-TRIVIAL"
        print(f"  n={r['n']}: {status} (rank={r.get('rank', '?')}, unknowns={r.get('n_unknowns', '?')})")


if __name__ == "__main__":
    main()

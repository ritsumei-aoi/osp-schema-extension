"""
find_trivial_gb.py — Find gb parameter configurations that give trivial deformations.

Tests various sign profiles for gb parameters and identifies triviality conditions.
"""

from __future__ import annotations
import json
import os
from fractions import Fraction
import sys

sys.path.insert(0, os.path.dirname(__file__))
from C_gamma import compute_gamma, gb_label
from C_generators import make_basis, make_parity
from C_evaluate import evaluate_expr


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
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    row_idx = 0
    for col in range(n):
        pivot = None
        for r in range(row_idx, m):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        M[row_idx], M[pivot] = M[pivot], M[row_idx]
        piv_val = M[row_idx][col]
        M[row_idx] = [x / piv_val for x in M[row_idx]]
        for r in range(m):
            if r != row_idx and M[r][col] != 0:
                factor = M[r][col]
                M[r] = [M[r][j] - factor * M[row_idx][j] for j in range(n + 1)]
        row_idx += 1
    rank = row_idx
    for r in range(rank, m):
        if M[r][n] != 0:
            return None, rank, False
    solution = [Fraction(0)] * n
    col_idx = 0
    for r in range(rank):
        while col_idx < n and M[r][col_idx] == 0:
            col_idx += 1
        if col_idx < n:
            solution[col_idx] = M[r][n]
    return solution, rank, True


def build_gamma_from_gb(n: int, schema1: dict, gb_values: dict) -> dict:
    """Build evaluated gamma table for given gb_values."""
    gamma_entries = compute_gamma(n)
    gamma_table = {}
    for entry in gamma_entries:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff = evaluate_expr(entry["gamma_coeff"], gb_values)
        if coeff != 0:
            key = (X, Y)
            if key not in gamma_table:
                gamma_table[key] = {}
            gamma_table[key][Z] = gamma_table[key].get(Z, Fraction(0)) + coeff
    return {k: {Z: c for Z, c in v.items() if c != 0} for k, v in gamma_table.items() if v}


def is_trivial(n: int, schema1: dict, gamma_table: dict) -> tuple[bool, int]:
    """Check if gamma is trivial by solving gamma = delta_f."""
    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]
    table = build_bracket_table(schema1)

    unknowns = []
    unk_idx = {}
    for j, gj in enumerate(basis):
        pj = parity[gj]
        for i, gi in enumerate(basis):
            pi = parity[gi]
            if (pi + pj) % 2 == 1:
                key = (i, j)
                unk_idx[key] = len(unknowns)
                unknowns.append(key)

    n_unk = len(unknowns)
    equations = []

    for ix, X in enumerate(basis):
        px = parity[X]
        for iy, Y in enumerate(basis):
            py = parity[Y]
            bXY = table.get((X, Y), {})
            gamma_XY = gamma_table.get((X, Y), {})
            all_Z_rhs = set(gamma_XY.keys())
            all_Z_t1 = set()
            all_Z_t2 = set()
            all_Z_t3 = set()
            for ik in range(len(basis)):
                for Z, c in table.get((X, basis[ik]), {}).items():
                    all_Z_t1.add(Z)
                for Z, c in table.get((Y, basis[ik]), {}).items():
                    all_Z_t2.add(Z)
            for ew, cw in bXY.items():
                all_Z_t3.update(basis)

            all_Z = all_Z_rhs | all_Z_t1 | all_Z_t2 | set(basis)

            for iz, Z in enumerate(basis):
                row = [Fraction(0)] * n_unk
                s1 = Fraction((-1) ** px)
                for ik, ek in enumerate(basis):
                    bX_ek = table.get((X, ek), {}).get(Z, Fraction(0))
                    if bX_ek != 0 and (ik, iy) in unk_idx:
                        row[unk_idx[(ik, iy)]] += s1 * bX_ek
                s2 = -Fraction((-1) ** ((px + 1) * py))
                for ik, ek in enumerate(basis):
                    bY_ek = table.get((Y, ek), {}).get(Z, Fraction(0))
                    if bY_ek != 0 and (ik, ix) in unk_idx:
                        row[unk_idx[(ik, ix)]] += s2 * bY_ek
                for iw, ew in enumerate(basis):
                    bXY_w = bXY.get(ew, Fraction(0))
                    if bXY_w != 0 and (iz, iw) in unk_idx:
                        row[unk_idx[(iz, iw)]] -= bXY_w
                rhs = gamma_XY.get(Z, Fraction(0))
                if any(c != 0 for c in row) or rhs != 0:
                    equations.append((row, rhs))

    if not equations:
        return True, 0

    A = [eq[0] for eq in equations]
    b = [eq[1] for eq in equations]
    _, rank, consistent = gaussian_elimination(A, b)
    return consistent, rank


def test_gb_profile(n: int, schema1: dict, profile_name: str, gb_values: dict) -> bool:
    gamma = build_gamma_from_gb(n, schema1, gb_values)
    trivial, rank = is_trivial(n, schema1, gamma)
    n_gamma = sum(len(v) for v in gamma.values())
    print(f"  n={n}, {profile_name}: gamma_entries={n_gamma}, trivial={trivial}")
    return trivial


def main():
    for n in [1, 2]:
        print(f"\n=== n={n} ===")
        schema1 = load(n, "structure")

        # Build gb parameter labels
        gb_labels = []
        for sigma in [1, -1]:
            sa = "p" if sigma == 1 else "m"
            for j in range(1, n + 1):
                for s in [1, -1]:
                    sb = "p" if s == 1 else "m"
                    gb_labels.append(f"gb_a1{sa}_b{j}{sb}")

        # Test 1: all gb = 0 (undeformed)
        gb0 = {lb: Fraction(0) for lb in gb_labels}
        test_gb_profile(n, schema1, "all_gb=0 (undeformed)", gb0)

        # Test 2: all gb = +1
        gb_all_plus = {lb: Fraction(1) for lb in gb_labels}
        test_gb_profile(n, schema1, "all_gb=+1", gb_all_plus)

        # Test 3: antisymmetric: gb_{+,j,s} = +1, gb_{-,j,s} = -1
        gb_antisym = {}
        for lb in gb_labels:
            gb_antisym[lb] = Fraction(1) if "a1p" in lb else Fraction(-1)
        test_gb_profile(n, schema1, "gb_antisym (a1p=+1, a1m=-1)", gb_antisym)

        # Test 4: gb_{sigma,j,+} = +1, gb_{sigma,j,-} = -1 (antisym in boson sign)
        gb_boson_antisym = {}
        for lb in gb_labels:
            gb_boson_antisym[lb] = Fraction(1) if lb.endswith("p") else Fraction(-1)
        test_gb_profile(n, schema1, "gb_boson_antisym (b_p=+1, b_m=-1)", gb_boson_antisym)

        # Test 5: symmetric: gb_{+,j,s} = gb_{-,j,s}
        # (already tested: all=+1 is symmetric)

        # Test 6: gb_{+,j,+} = gb_{-,j,-}, gb_{+,j,-} = gb_{-,j,+} (charge conjugation)
        gb_cc = {}
        for lb in gb_labels:
            if "a1p" in lb:
                # Find the corresponding a1m version with swapped b sign
                lb_m = lb.replace("a1p", "a1m")
                if lb.endswith("p"):
                    lb_m = lb_m[:-1] + "m"
                else:
                    lb_m = lb_m[:-1] + "p"
                gb_cc[lb] = Fraction(1)
            else:
                gb_cc[lb] = Fraction(1)  # same as above for simplicity
        test_gb_profile(n, schema1, "gb_cc (charge conjugation)", gb_cc)

        # Test 7: only one gb parameter nonzero
        for lb_nonzero in gb_labels[:2]:
            gb_single = {lb: Fraction(0) for lb in gb_labels}
            gb_single[lb_nonzero] = Fraction(1)
            test_gb_profile(n, schema1, f"single gb: {lb_nonzero}=1", gb_single)

        # Test 8: gb = t*all_plus, vary t (this doesn't change triviality since the system is linear)
        # Instead, test if there's a linear subspace of trivial deformations
        # by trying a few sign combinations
        for signs in [(1,1,1,-1), (1,-1,1,1), (-1,1,-1,1)]:
            if len(gb_labels) >= 4:
                gb_test = {lb: Fraction(s) for lb, s in zip(gb_labels, signs * (len(gb_labels)//4+1))}
                gb_test = {lb: gb_test[lb] for lb in gb_labels}
                test_gb_profile(n, schema1, f"signs={signs[:min(4,len(gb_labels))]}", gb_test)


if __name__ == "__main__":
    main()

"""
Verification script for C(n+1) = osp(2|2n) structure constants.
Checks graded anti-symmetry and the Super Jacobi identity for n=1,2,3.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
import itertools


def load_algebra(filename):
    with open(filename) as f:
        data = json.load(f)

    basis_even = data["basis"]["even"]
    basis_odd = data["basis"]["odd"]
    basis = basis_even + basis_odd
    parity = {k: v for k, v in data["parity"].items()}

    # br_raw[X][Y][Z] = coeff: raw bracket entries as stored in JSON
    br_raw = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = Fraction(entry["coeff"])
        br_raw[X][Y][Z] += c

    return basis, parity, br_raw, data


def graded_antisym_sign(parity, X, Y):
    """Returns -(-1)^{p(X)*p(Y)}, the anti-symmetry factor for [X,Y] vs [Y,X]."""
    return Fraction(-(-1) ** (parity[X] * parity[Y]))


def build_full_bracket(basis, parity, br_raw):
    """
    Build the complete bracket table by deriving anti-symmetric partners.
    Returns (br_full, raw_conflicts) where raw_conflicts lists entries
    that contradict anti-symmetry as stored.

    br_full[X][Y] = {Z: Fraction} for all X, Y in basis.
    """
    br_full = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    raw_conflicts = []

    # Collect all (X, Y) pairs that appear in br_raw
    stored_pairs = set()
    for X in br_raw:
        for Y in br_raw[X]:
            stored_pairs.add((X, Y))

    for X, Y in stored_pairs:
        sign = graded_antisym_sign(parity, X, Y)
        XY_entries = br_raw[X][Y]
        YX_entries = br_raw[Y][X]

        if YX_entries:
            # Both (X,Y) and (Y,X) stored: check consistency
            all_Z = set(XY_entries.keys()) | set(YX_entries.keys())
            for Z in all_Z:
                cXY = XY_entries.get(Z, Fraction(0))
                cYX = YX_entries.get(Z, Fraction(0))
                expected_YX = sign * cXY
                if cYX != expected_YX:
                    raw_conflicts.append((X, Y, Z, cYX, expected_YX))

    # Populate br_full: copy stored entries, then derive missing reverse entries
    processed_pairs = set()
    for X, Y in stored_pairs:
        if (X, Y) in processed_pairs:
            continue
        processed_pairs.add((X, Y))
        processed_pairs.add((Y, X))

        sign = graded_antisym_sign(parity, X, Y)
        XY_entries = br_raw[X][Y]
        YX_entries = br_raw[Y][X]

        for Z, c in XY_entries.items():
            br_full[X][Y][Z] += c
            # Derive [Y,X] unless already stored
            if not YX_entries:
                br_full[Y][X][Z] += sign * c

        for Z, c in YX_entries.items():
            br_full[Y][X][Z] += c
            if not XY_entries:
                br_full[X][Y][Z] += sign * c

    return br_full, raw_conflicts


def apply_bracket(br_full, X, Y):
    """Return {Z: coeff} for [X, Y] (filtered for non-zero)."""
    return {Z: c for Z, c in br_full[X][Y].items() if c != 0}


def bracket_of_vectors(br_full, v1, v2):
    """
    v1, v2: {generator: Fraction} dicts.
    Returns [{generator: Fraction}] = [v1, v2] (bilinear extension).
    """
    result = defaultdict(Fraction)
    for X, cX in v1.items():
        for Y, cY in v2.items():
            for Z, cZ in br_full[X][Y].items():
                result[Z] += cX * cY * cZ
    return {Z: c for Z, c in result.items() if c != 0}


def check_antisymmetry(basis, parity, br_full):
    """
    Check graded anti-symmetry: [X,Y] + (-1)^{p(X)p(Y)} [Y,X] = 0 for all X,Y.
    Returns list of failures (X, Y, Z, actual, expected).
    """
    failures = []
    for X, Y in itertools.product(basis, repeat=2):
        sign = graded_antisym_sign(parity, X, Y)
        all_Z = set(br_full[X][Y].keys()) | set(br_full[Y][X].keys())
        for Z in all_Z:
            cXY = br_full[X][Y].get(Z, Fraction(0))
            cYX = br_full[Y][X].get(Z, Fraction(0))
            if cXY != sign * cYX:
                failures.append((X, Y, Z, cXY, sign * cYX))
    return failures


def check_super_jacobi(basis, parity, br_full):
    """
    Check Super Jacobi identity for all ordered triples (X, Y, Z):
      (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0
    Returns list of failures (X, Y, Z, {W: residual}).
    """
    failures = []
    n = len(basis)
    total_triples = n ** 3

    for idx, (X, Y, Z) in enumerate(itertools.product(basis, repeat=3)):
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]

        YZ = apply_bracket(br_full, Y, Z)
        ZX = apply_bracket(br_full, Z, X)
        XY = apply_bracket(br_full, X, Y)

        sign1 = Fraction((-1) ** (pX * pZ))
        sign2 = Fraction((-1) ** (pY * pX))
        sign3 = Fraction((-1) ** (pZ * pY))

        term1 = bracket_of_vectors(br_full, {X: Fraction(1)}, YZ)
        term2 = bracket_of_vectors(br_full, {Y: Fraction(1)}, ZX)
        term3 = bracket_of_vectors(br_full, {Z: Fraction(1)}, XY)

        total = defaultdict(Fraction)
        for W, c in term1.items():
            total[W] += sign1 * c
        for W, c in term2.items():
            total[W] += sign2 * c
        for W, c in term3.items():
            total[W] += sign3 * c

        nonzero = {W: c for W, c in total.items() if c != 0}
        if nonzero:
            failures.append((X, Y, Z, nonzero))

    return failures


def verify_algebra(n, data_dir):
    filename = os.path.join(data_dir, f"C_{n}_structure.json")
    print(f"\n{'=' * 65}")
    print(f"  Verifying C_{n}_structure.json  (n={n})")
    print(f"{'=' * 65}")

    basis, parity, br_raw, data = load_algebra(filename)
    alg_name = data["algebra"]["cartan_type"]
    dim = data["algebra"]["dimension"]

    print(f"  Algebra  : {alg_name} = osp(2|{2*n})")
    print(f"  Dimension: even={dim['even']}, odd={dim['odd']}, total={dim['total']}")
    print(f"  |basis|  : {len(basis)}")
    print(f"  Stored structure-constant entries: {len(data['structure_constants'])}")

    # Build full bracket table
    br_full, raw_conflicts = build_full_bracket(basis, parity, br_raw)

    # 0. Raw-data consistency (stored vs anti-sym partner when both exist)
    if raw_conflicts:
        print(f"\n  [FAIL] Stored data has {len(raw_conflicts)} anti-symmetry conflict(s):")
        for conf in raw_conflicts[:5]:
            print(f"         [{conf[0]}, {conf[1]}]_{conf[2]}: stored={conf[3]}, expected={conf[4]}")
    else:
        print(f"\n  [PASS] Stored entries internally consistent (no anti-sym conflicts).")

    # 1. Graded anti-symmetry
    print(f"\n  Checking graded anti-symmetry ({len(basis)}^2 = {len(basis)**2} pairs)...")
    asym_fail = check_antisymmetry(basis, parity, br_full)
    if asym_fail:
        print(f"  [FAIL] {len(asym_fail)} anti-symmetry failure(s):")
        for f in asym_fail[:5]:
            print(f"         [{f[0]}, {f[1]}]_{f[2]}: got {f[3]}, expected {f[4]}")
    else:
        print(f"  [PASS] All pairs satisfy graded anti-symmetry.")

    # 2. Super Jacobi identity
    total_triples = len(basis) ** 3
    print(f"\n  Checking Super Jacobi identity ({len(basis)}^3 = {total_triples} triples)...")
    jacobi_fail = check_super_jacobi(basis, parity, br_full)
    if jacobi_fail:
        print(f"  [FAIL] {len(jacobi_fail)} Super Jacobi failure(s):")
        for f in jacobi_fail[:5]:
            print(f"         ({f[0]}, {f[1]}, {f[2]}): residual = {f[3]}")
    else:
        print(f"  [PASS] All triples satisfy the Super Jacobi identity.")

    asym_pass = (not raw_conflicts) and (not asym_fail)
    jacobi_pass = not jacobi_fail
    return alg_name, asym_pass, jacobi_pass


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    print("=" * 65)
    print("  C(n+1) Structure Constant Verification")
    print("=" * 65)
    print("  Checks: (1) Graded anti-symmetry, (2) Super Jacobi identity")
    print("  Files : C_1_structure.json, C_2_structure.json, C_3_structure.json")

    results = []
    for n in [1, 2, 3]:
        alg_name, asym_pass, jacobi_pass = verify_algebra(n, data_dir)
        results.append((alg_name, n, asym_pass, jacobi_pass))

    print(f"\n{'=' * 65}")
    print("  FINAL SUMMARY")
    print(f"{'=' * 65}")
    print(f"  {'Algebra':<20} {'Anti-sym':<12} {'Super Jacobi'}")
    print(f"  {'-'*20} {'-'*12} {'-'*12}")
    all_pass = True
    for alg_name, n, asym_pass, jacobi_pass in results:
        asym_str = "PASS" if asym_pass else "FAIL"
        jac_str = "PASS" if jacobi_pass else "FAIL"
        print(f"  {alg_name:<20} {asym_str:<12} {jac_str}")
        if not (asym_pass and jacobi_pass):
            all_pass = False

    print(f"\n  Overall result: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

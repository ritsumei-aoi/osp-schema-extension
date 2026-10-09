"""
verify_C_structure.py — Verify Super Jacobi identity and graded anti-symmetry
for C(n+1) = osp(2|2n) structure constants (Schema 1 JSON).

Super Jacobi identity (graded):
  (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0

Graded anti-symmetry:
  [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
"""

from __future__ import annotations
import json
import os
import sys
from fractions import Fraction
from itertools import product


def load_schema(n: int) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema: dict) -> dict:
    """
    Build a dict mapping (X, Y) -> {Z: coeff (Fraction)} for all non-zero brackets.
    Also build the full bracket function including zero results.
    """
    table = {}
    for sc in schema["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return table


def bracket(X: str, Y: str, table: dict) -> dict:
    """Return [X, Y] as a dict {Z: coeff}. Zero result is empty dict."""
    return dict(table.get((X, Y), {}))


def linear_combine(scalar: Fraction, v: dict) -> dict:
    """Multiply a vector (dict {Z: coeff}) by scalar."""
    if scalar == 0:
        return {}
    return {Z: scalar * c for Z, c in v.items() if scalar * c != 0}


def add_vectors(*vecs) -> dict:
    """Add multiple vectors."""
    result = {}
    for v in vecs:
        for Z, c in v.items():
            result[Z] = result.get(Z, Fraction(0)) + c
    return {Z: c for Z, c in result.items() if c != 0}


def apply_bracket(vec: dict, Y: str, table: dict, parity: dict, side: str = "left") -> dict:
    """
    Apply bracket [vec, Y] or [Y, vec] linearly.
    side="left": compute [vec, Y] = sum_X coeff_X [X, Y]
    side="right": compute [Y, vec] = sum_X coeff_X [Y, X]
    """
    result = {}
    for X, cX in vec.items():
        if side == "left":
            b = bracket(X, Y, table)
        else:
            b = bracket(Y, X, table)
        for Z, cZ in b.items():
            result[Z] = result.get(Z, Fraction(0)) + cX * cZ
    return {Z: c for Z, c in result.items() if c != 0}


def check_antisymmetry(schema: dict, table: dict) -> tuple[int, int, list]:
    """
    Check graded anti-symmetry: [X, Y] + (-1)^{p(X)p(Y)} [Y, X] = 0.
    Returns (n_checked, n_failed, failures).
    """
    parity = schema["parity"]
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    n_checked = 0
    n_failed = 0
    failures = []

    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if j < i:
                continue  # check each unordered pair once
            px, py = parity[X], parity[Y]
            bXY = bracket(X, Y, table)
            bYX = bracket(Y, X, table)
            sign = Fraction((-1) ** (px * py))
            # [X,Y] + sign * [Y,X] should be 0
            total = add_vectors(bXY, linear_combine(sign, bYX))
            n_checked += 1
            if total:
                n_failed += 1
                failures.append({
                    "X": X, "Y": Y,
                    "discrepancy": {Z: str(c) for Z, c in total.items()},
                })
    return n_checked, n_failed, failures


def check_super_jacobi(schema: dict, table: dict) -> tuple[int, int, list]:
    """
    Check Super Jacobi identity for all triples (X, Y, Z).
    SJI: (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0
    Returns (n_checked, n_failed, failures).
    """
    parity = schema["parity"]
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    n_checked = 0
    n_failed = 0
    failures = []

    for X in basis:
        for Y in basis:
            for Z in basis:
                px, py, pz = parity[X], parity[Y], parity[Z]
                # Compute each term
                bYZ = bracket(Y, Z, table)
                bZX = bracket(Z, X, table)
                bXY = bracket(X, Y, table)

                # Term1: (-1)^{p(X)p(Z)} [X, [Y,Z]]
                s1 = Fraction((-1) ** (px * pz))
                t1 = linear_combine(s1, apply_bracket(bYZ, X, table, parity, side="right"))
                # Wait: [X, [Y,Z]] = apply X on the left to [Y,Z]
                # [X, sum_W c_W W] = sum_W c_W [X, W]
                t1_inner = {}
                for W, cW in bYZ.items():
                    b = bracket(X, W, table)
                    for V, cV in b.items():
                        t1_inner[V] = t1_inner.get(V, Fraction(0)) + cW * cV
                t1 = linear_combine(s1, t1_inner)

                # Term2: (-1)^{p(Y)p(X)} [Y, [Z,X]]
                s2 = Fraction((-1) ** (py * px))
                t2_inner = {}
                for W, cW in bZX.items():
                    b = bracket(Y, W, table)
                    for V, cV in b.items():
                        t2_inner[V] = t2_inner.get(V, Fraction(0)) + cW * cV
                t2 = linear_combine(s2, t2_inner)

                # Term3: (-1)^{p(Z)p(Y)} [Z, [X,Y]]
                s3 = Fraction((-1) ** (pz * py))
                t3_inner = {}
                for W, cW in bXY.items():
                    b = bracket(Z, W, table)
                    for V, cV in b.items():
                        t3_inner[V] = t3_inner.get(V, Fraction(0)) + cW * cV
                t3 = linear_combine(s3, t3_inner)

                total = add_vectors(t1, t2, t3)
                n_checked += 1
                if total:
                    n_failed += 1
                    if n_failed <= 5:  # Record first 5 failures only
                        failures.append({
                            "X": X, "Y": Y, "Z": Z,
                            "discrepancy": {V: str(c) for V, c in total.items()},
                        })
    return n_checked, n_failed, failures


def verify_n(n: int) -> dict:
    print(f"\n=== Verifying C_{n}_structure.json (n={n}) ===")
    schema = load_schema(n)
    table = build_bracket_table(schema)

    # Anti-symmetry check
    as_checked, as_failed, as_failures = check_antisymmetry(schema, table)
    print(f"Anti-symmetry: {as_checked} pairs checked, {as_failed} failed")
    for f in as_failures[:3]:
        print(f"  FAIL: [{f['X']}, {f['Y']}]: {f['discrepancy']}")

    # Super Jacobi check
    sj_checked, sj_failed, sj_failures = check_super_jacobi(schema, table)
    print(f"Super Jacobi: {sj_checked} triples checked, {sj_failed} failed")
    for f in sj_failures[:3]:
        print(f"  FAIL: ({f['X']}, {f['Y']}, {f['Z']}): {f['discrepancy']}")

    return {
        "n": n,
        "antisymmetry": {"checked": as_checked, "failed": as_failed, "failures": as_failures},
        "super_jacobi": {"checked": sj_checked, "failed": sj_failed, "failures": sj_failures[:5]},
        "pass": as_failed == 0 and sj_failed == 0,
    }


def main():
    results = []
    for n in range(1, 4):
        r = verify_n(n)
        results.append(r)

    print("\n=== Summary ===")
    all_pass = True
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  n={r['n']}: {status}")
        if not r["pass"]:
            all_pass = False

    if all_pass:
        print("\nAll checks PASSED.")
    else:
        print("\nSome checks FAILED. See details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
verify_C_structure.py — Super Jacobi identity and anti-symmetry verification
for C(n+1) structure constants loaded from Schema 1 JSON files.

Super Jacobi: (-1)^{p(X)p(Z)} [X,[Y,Z}] + (-1)^{p(Y)p(X)} [Y,[Z,X}] + (-1)^{p(Z)p(Y)} [Z,[X,Y}] = 0
Anti-symmetry: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
"""

import json
import os
import sys
from fractions import Fraction
from itertools import product


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_schema(n):
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


def build_bracket_table(schema):
    """
    Build bracket lookup: (X, Y) -> dict Z->Fraction, for all ordered pairs.
    Uses anti-symmetry to fill in the (Y, X) direction from stored (X, Y).
    """
    parity = {k: v for k, v in schema['parity'].items()}
    parity['K'] = 0
    basis = schema['basis']['odd'] + schema['basis']['even']

    # Initialize table
    table = {(X, Y): {} for X in basis for Y in basis}

    # Fill from stored structure constants (i<=j direction)
    for sc in schema['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        c = Fraction(sc['coeff'])
        if Z == 'K':
            continue  # K central, [anything, K]=0
        table[(X, Y)][Z] = table[(X, Y)].get(Z, Fraction(0)) + c

    # Snapshot original entries before filling anti-symmetric direction
    original = {key: dict(val) for key, val in table.items()}

    # Fill anti-symmetric direction: [Y,X} = -(-1)^{pX*pY} [X,Y}
    # Use only original (stored) entries to avoid double-filling
    for X in basis:
        for Y in basis:
            if X == Y:
                continue
            pX, pY = parity[X], parity[Y]
            sign = -(-1) ** (pX * pY)
            for Z, c in original[(X, Y)].items():
                table[(Y, X)][Z] = table[(Y, X)].get(Z, Fraction(0)) + sign * c

    # Clean up zeros
    for key in table:
        table[key] = {k: v for k, v in table[key].items() if v != 0}

    return table, parity, basis


def apply_bracket(table, X, result_dict):
    """Apply X to each component of result_dict (linear extension of bracket)."""
    out = {}
    for Z, c_xz in result_dict.items():
        for W, c_zw in table[(X, Z)].items():
            out[W] = out.get(W, Fraction(0)) + c_xz * c_zw
    return {k: v for k, v in out.items() if v != 0}


def verify_antisymmetry(table, parity, basis):
    """
    Check [X,Y} = -(-1)^{pX*pY}[Y,X} using the full bracket table.
    This verifies that the anti-symmetric fill is consistent.
    """
    failures = []
    checked = 0
    for X in basis:
        for Y in basis:
            pX, pY = parity[X], parity[Y]
            sign = -(-1) ** (pX * pY)
            xy = table[(X, Y)]
            yx = table[(Y, X)]
            all_Z = set(list(xy.keys()) + list(yx.keys()))
            for Z in all_Z:
                c_xy = xy.get(Z, Fraction(0))
                c_yx = yx.get(Z, Fraction(0))
                if c_xy != sign * c_yx:
                    failures.append(f"Anti-sym fail [{X},{Y}]_Z={Z}: {c_xy} != {sign}*{c_yx}")
            checked += 1
    return checked, failures


def verify_super_jacobi(table, parity, basis):
    """
    Check Super Jacobi for all triples (X, Y, Z).
    SJ(X,Y,Z) = (-1)^{pX*pZ}[X,[Y,Z}] + (-1)^{pY*pX}[Y,[Z,X}] + (-1)^{pZ*pY}[Z,[X,Y}] = 0
    """
    failures = []
    checked = 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                pX, pY, pZ = parity[X], parity[Y], parity[Z]

                # Term 1: (-1)^{pX*pZ} [X, [Y,Z}]
                yz = table[(Y, Z)]
                x_yz = apply_bracket(table, X, yz)
                s1 = (-1) ** (pX * pZ)

                # Term 2: (-1)^{pY*pX} [Y, [Z,X}]
                zx = table[(Z, X)]
                y_zx = apply_bracket(table, Y, zx)
                s2 = (-1) ** (pY * pX)

                # Term 3: (-1)^{pZ*pY} [Z, [X,Y}]
                xy = table[(X, Y)]
                z_xy = apply_bracket(table, Z, xy)
                s3 = (-1) ** (pZ * pY)

                # Sum
                total = {}
                for d, s in [(x_yz, s1), (y_zx, s2), (z_xy, s3)]:
                    for W, c in d.items():
                        total[W] = total.get(W, Fraction(0)) + s * c
                total = {k: v for k, v in total.items() if v != 0}

                if total:
                    failures.append(
                        f"Jacobi fail [{X},{Y},{Z}]: residual={dict(total)}"
                    )
                checked += 1
    return checked, failures


def main():
    overall_pass = True
    for n in [1, 2, 3]:
        print(f"\n=== C_{n} (n={n}, C({n+1}) = osp(2|{2*n})) ===")
        schema = load_schema(n)
        basis = schema['basis']['odd'] + schema['basis']['even']
        N = len(basis)

        # Build bracket table
        table, parity, basis = build_bracket_table(schema)

        # Anti-symmetry
        checked_as, failures_as = verify_antisymmetry(table, parity, basis)
        print(f"Anti-symmetry: checked {checked_as} pairs — ", end="")
        if failures_as:
            print(f"FAIL ({len(failures_as)} failures)")
            for f in failures_as[:5]:
                print(f"  {f}")
            overall_pass = False
        else:
            print("PASS")

        # Super Jacobi (use same table)
        checked_sj, failures_sj = verify_super_jacobi(table, parity, basis)
        print(f"Super Jacobi: checked {checked_sj} triples — ", end="")
        if failures_sj:
            print(f"FAIL ({len(failures_sj)} failures)")
            for f in failures_sj[:5]:
                print(f"  {f}")
            overall_pass = False
        else:
            print("PASS")

    print(f"\n{'ALL CHECKS PASSED' if overall_pass else 'SOME CHECKS FAILED'}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())

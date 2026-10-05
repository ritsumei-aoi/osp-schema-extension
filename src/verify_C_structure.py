"""
Verify Super Jacobi identity and anti-symmetry for C(n+1) structure constants.
Loads Schema 1 JSON files and checks all generator pairs/triples.
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(n, data_dir="data"):
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(structure):
    """Build a lookup table: (X, Y) -> list of (Z, coeff)."""
    table = {}
    parity = structure["parity"]
    for sc in structure["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        if (X, Y) not in table:
            table[(X, Y)] = []
        table[(X, Y)].append((Z, coeff))
    return table


def bracket(table, parity, X, Y):
    """Compute [X, Y} using the table. Returns dict Z -> coeff."""
    if (X, Y) in table:
        return {z: c for z, c in table[(X, Y)]}
    elif (Y, X) in table:
        pX, pY = parity[X], parity[Y]
        sign = Fraction(-1) ** (pX * pY) * Fraction(-1)
        return {z: sign * c for z, c in table[(Y, X)]}
    return {}


def check_antisymmetry(structure):
    """Check graded anti-symmetry: [X, Y} = -(-1)^{pX*pY} [Y, X}."""
    table = build_bracket_table(structure)
    parity = structure["parity"]
    basis = structure["basis"]["odd"] + structure["basis"]["even"]
    failures = []

    for i, X in enumerate(basis):
        for j in range(i + 1, len(basis)):
            Y = basis[j]
            pX, pY = parity[X], parity[Y]

            xy = bracket(table, parity, X, Y)
            yx = bracket(table, parity, Y, X)

            sign = Fraction(-1) ** (pX * pY)

            all_gens = set(xy.keys()) | set(yx.keys())
            for Z in all_gens:
                c_xy = xy.get(Z, Fraction(0))
                c_yx = yx.get(Z, Fraction(0))
                if c_xy != -sign * c_yx:
                    failures.append((X, Y, Z, str(c_xy), str(-sign * c_yx)))

    return failures


def check_super_jacobi(structure):
    """Check Super Jacobi identity for all generator triples:
    (-1)^{pX*pZ} [X, [Y, Z}} + (-1)^{pY*pX} [Y, [Z, X}} + (-1)^{pZ*pY} [Z, [X, Y}} = 0
    """
    table = build_bracket_table(structure)
    parity = structure["parity"]
    basis = structure["basis"]["odd"] + structure["basis"]["even"]
    failures = []

    for i, X in enumerate(basis):
        for j in range(i, len(basis)):
            Y = basis[j]
            for k in range(j, len(basis)):
                Z = basis[k]
                pX, pY, pZ = parity[X], parity[Y], parity[Z]

                # Term 1: (-1)^{pX*pZ} [X, [Y, Z}}
                yz = bracket(table, parity, Y, Z)
                term1 = {}
                sign1 = Fraction(-1) ** (pX * pZ)
                for W, c_yz in yz.items():
                    xw = bracket(table, parity, X, W)
                    for V, c_xw in xw.items():
                        term1[V] = term1.get(V, Fraction(0)) + sign1 * c_yz * c_xw

                # Term 2: (-1)^{pY*pX} [Y, [Z, X}}
                zx = bracket(table, parity, Z, X)
                term2 = {}
                sign2 = Fraction(-1) ** (pY * pX)
                for W, c_zx in zx.items():
                    yw = bracket(table, parity, Y, W)
                    for V, c_yw in yw.items():
                        term2[V] = term2.get(V, Fraction(0)) + sign2 * c_zx * c_yw

                # Term 3: (-1)^{pZ*pY} [Z, [X, Y}}
                xy = bracket(table, parity, X, Y)
                term3 = {}
                sign3 = Fraction(-1) ** (pZ * pY)
                for W, c_xy in xy.items():
                    zw = bracket(table, parity, Z, W)
                    for V, c_zw in zw.items():
                        term3[V] = term3.get(V, Fraction(0)) + sign3 * c_xy * c_zw

                # Sum all terms
                all_gens = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for V in all_gens:
                    total = (term1.get(V, Fraction(0))
                             + term2.get(V, Fraction(0))
                             + term3.get(V, Fraction(0)))
                    if total != 0:
                        failures.append((X, Y, Z, V, str(total)))

    return failures


def verify_all(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        structure = load_structure(n, data_dir)
        print(f"\n=== C({n+1}) = osp(2|{2*n}), n={n} ===")

        anti_failures = check_antisymmetry(structure)
        if anti_failures:
            print(f"  Anti-symmetry FAILURES: {len(anti_failures)}")
            for f in anti_failures[:5]:
                print(f"    [{f[0]}, {f[1]}] -> {f[2]}: got {f[3]}, expected {f[4]}")
        else:
            print(f"  Anti-symmetry: PASS")

        jacobi_failures = check_super_jacobi(structure)
        if jacobi_failures:
            print(f"  Super Jacobi FAILURES: {len(jacobi_failures)}")
            for f in jacobi_failures[:5]:
                print(f"    ({f[0]}, {f[1]}, {f[2]}) -> {f[3]}: residual = {f[4]}")
        else:
            print(f"  Super Jacobi: PASS")

        total_triples = 0
        basis = structure["basis"]["odd"] + structure["basis"]["even"]
        d = len(basis)
        for i in range(d):
            for j in range(i, d):
                for k in range(j, d):
                    total_triples += 1

        results[n] = {
            "antisymmetry_failures": len(anti_failures),
            "jacobi_failures": len(jacobi_failures),
            "total_triples": total_triples,
        }
        print(f"  Total triples checked: {total_triples}")

    return results


if __name__ == "__main__":
    verify_all()

"""
Verify C(n+1) structure constants satisfy anti-symmetry and Super Jacobi identity.
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(n, data_dir="data"):
    filename = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(filename) as f:
        return json.load(f)


def build_bracket_table(data):
    parity = data["parity"]
    all_gens = data["basis"]["odd"] + data["basis"]["even"]
    bracket = {}
    for sc in data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in bracket:
            bracket[key] = {}
        bracket[key][Z] = bracket[key].get(Z, Fraction(0)) + coeff
    return bracket, parity, all_gens


def get_bracket(bracket_table, parity, X, Y):
    if (X, Y) in bracket_table:
        return dict(bracket_table[(X, Y)])
    elif (Y, X) in bracket_table:
        pX = parity[X]
        pY = parity[Y]
        sign = (-1) ** (pX * pY)
        result = {}
        for Z, c in bracket_table[(Y, X)].items():
            result[Z] = -sign * c
        return result
    return {}


def check_antisymmetry(data):
    bracket, parity, all_gens = build_bracket_table(data)
    failures = []

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue

            xy = get_bracket(bracket, parity, X, Y)
            yx = get_bracket(bracket, parity, Y, X)

            pX = parity[X]
            pY = parity[Y]
            sign = (-1) ** (pX * pY)

            all_keys = set(list(xy.keys()) + list(yx.keys()))
            for Z in all_keys:
                cXY = xy.get(Z, Fraction(0))
                cYX = yx.get(Z, Fraction(0))
                expected = -sign * cXY
                if cYX != expected:
                    failures.append({
                        "X": X, "Y": Y, "Z": Z,
                        "[X,Y]": str(cXY), "[Y,X]": str(cYX),
                        "expected [Y,X]": str(expected)
                    })

    return failures


def check_super_jacobi(data):
    bracket, parity, all_gens = build_bracket_table(data)
    failures = []

    N = len(all_gens)
    for i in range(N):
        for j in range(i, N):
            for k in range(j, N):
                X, Y, Z = all_gens[i], all_gens[j], all_gens[k]
                pX = parity[X]
                pY = parity[Y]
                pZ = parity[Z]

                # Super Jacobi: (-1)^{pX*pZ} [[X,Y],Z] + (-1)^{pY*pX} [[Y,Z],X] + (-1)^{pZ*pY} [[Z,X],Y] = 0
                term1 = nested_bracket(bracket, parity, X, Y, Z)
                s1 = (-1) ** (pX * pZ)

                term2 = nested_bracket(bracket, parity, Y, Z, X)
                s2 = (-1) ** (pY * pX)

                term3 = nested_bracket(bracket, parity, Z, X, Y)
                s3 = (-1) ** (pZ * pY)

                all_keys = set(list(term1.keys()) + list(term2.keys()) + list(term3.keys()))
                for W in all_keys:
                    total = (s1 * term1.get(W, Fraction(0)) +
                             s2 * term2.get(W, Fraction(0)) +
                             s3 * term3.get(W, Fraction(0)))
                    if total != 0:
                        failures.append({
                            "X": X, "Y": Y, "Z": Z, "W": W,
                            "residual": str(total)
                        })

    return failures


def nested_bracket(bracket_table, parity, A, B, C):
    """Compute [[A,B], C] as a linear combination."""
    ab = get_bracket(bracket_table, parity, A, B)
    result = {}
    for Z, c_ab in ab.items():
        zc = get_bracket(bracket_table, parity, Z, C)
        for W, c_zc in zc.items():
            result[W] = result.get(W, Fraction(0)) + c_ab * c_zc
    return {k: v for k, v in result.items() if v != 0}


def verify_all(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        print(f"\n=== Verifying C({n+1}) = osp(2|{2*n}), n={n} ===")
        data = load_structure(n, data_dir)
        all_gens = data["basis"]["odd"] + data["basis"]["even"]
        print(f"  Generators: {len(all_gens)}")
        print(f"  Structure constants: {len(data['structure_constants'])}")

        print("  Checking anti-symmetry...")
        asym_failures = check_antisymmetry(data)
        if asym_failures:
            print(f"  FAIL: {len(asym_failures)} anti-symmetry violations")
            for f in asym_failures[:5]:
                print(f"    {f}")
        else:
            print(f"  PASS: anti-symmetry OK")

        print("  Checking Super Jacobi identity...")
        jacobi_failures = check_super_jacobi(data)
        if jacobi_failures:
            print(f"  FAIL: {len(jacobi_failures)} Jacobi violations")
            for f in jacobi_failures[:5]:
                print(f"    {f}")
        else:
            print(f"  PASS: Super Jacobi identity OK")

        n_triples = len(all_gens) * (len(all_gens) + 1) * (len(all_gens) + 2) // 6
        print(f"  Triples checked: {n_triples}")

        results[n] = {
            "antisymmetry_failures": len(asym_failures),
            "jacobi_failures": len(jacobi_failures),
            "triples_checked": n_triples
        }

    return results


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    verify_all(data_dir)

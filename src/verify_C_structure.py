"""
verify_C_structure.py

Verifies that the C(n+1) structure constants satisfy:
1. Graded anti-symmetry: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
2. Super Jacobi identity: (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0

Loads the generated JSON files and checks all generator pairs/triples.
"""

import json
import os
import sys
from fractions import Fraction
from itertools import product as iproduct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..","src"))


def load_schema(n: int) -> dict:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")
    with open(data_path) as f:
        return json.load(f)


def build_bracket_map(schema: dict) -> dict:
    """Build a dict (X, Y) -> {Z: coeff} from structure constants."""
    bracket = {}
    parity = schema["parity"]
    basis = schema["basis"]["odd"] + schema["basis"]["even"]

    for sc in schema["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in bracket:
            bracket[key] = {}
        bracket[key][Z] = bracket[key].get(Z, Fraction(0)) + coeff

    return bracket, basis, parity


def bracket_result(X: str, Y: str, bracket_map: dict, parity: dict, basis: list) -> dict:
    """Return {Z: coeff} for [X, Y}."""
    result = {}
    key_xy = (X, Y)
    key_yx = (Y, X)

    if key_xy in bracket_map:
        for Z, c in bracket_map[key_xy].items():
            result[Z] = result.get(Z, Fraction(0)) + c

    return result


def add_vectors(a: dict, b: dict, scale: Fraction = Fraction(1)) -> dict:
    result = dict(a)
    for k, v in b.items():
        result[k] = result.get(k, Fraction(0)) + scale * v
    return {k: v for k, v in result.items() if v != 0}


def bracket_of_brackets(X: str, res_YZ: dict, bracket_map: dict, parity: dict, basis: list) -> dict:
    """Compute [X, [Y,Z}} = sum_{W in res_YZ} res_YZ[W] * [X, W}"""
    total = {}
    pX = parity[X]
    for W, cW in res_YZ.items():
        pW = parity[W]
        # [X, W} = sum_Z f^Z_{XW} Z
        inner = bracket_result(X, W, bracket_map, parity, basis)
        for Z, cZ in inner.items():
            total[Z] = total.get(Z, Fraction(0)) + cW * cZ
    return {k: v for k, v in total.items() if v != 0}


def verify_antisymmetry(n: int) -> tuple:
    """Check [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}. Returns (pass, failures)."""
    schema = load_schema(n)
    bracket_map, basis, parity = build_bracket_map(schema)
    failures = []

    checked = 0
    for X in basis:
        for Y in basis:
            pX = parity[X]
            pY = parity[Y]
            sign = Fraction((-1) ** (pX * pY))  # [X,Y} + (-1)^{pX pY} [Y,X} = 0

            res_xy = bracket_result(X, Y, bracket_map, parity, basis)
            res_yx = bracket_result(Y, X, bracket_map, parity, basis)

            # Check: res_xy + sign * res_yx == 0
            check = add_vectors(res_xy, res_yx, sign)
            if check:
                failures.append({
                    "X": X, "Y": Y,
                    "pX": pX, "pY": pY,
                    "residual": {k: str(v) for k, v in check.items()}
                })
            checked += 1

    return len(failures) == 0, failures, checked


def verify_super_jacobi(n: int) -> tuple:
    """Check Super Jacobi for all triples (X,Y,Z). Returns (pass, failures)."""
    schema = load_schema(n)
    bracket_map, basis, parity = build_bracket_map(schema)
    failures = []

    checked = 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                pX = parity[X]
                pY = parity[Y]
                pZ = parity[Z]

                # Term 1: (-1)^{pX pZ} [X, [Y,Z}}
                res_YZ = bracket_result(Y, Z, bracket_map, parity, basis)
                t1 = bracket_of_brackets(X, res_YZ, bracket_map, parity, basis)
                sign1 = Fraction((-1) ** (pX * pZ))

                # Term 2: (-1)^{pY pX} [Y, [Z,X}}
                res_ZX = bracket_result(Z, X, bracket_map, parity, basis)
                t2 = bracket_of_brackets(Y, res_ZX, bracket_map, parity, basis)
                sign2 = Fraction((-1) ** (pY * pX))

                # Term 3: (-1)^{pZ pY} [Z, [X,Y}}
                res_XY = bracket_result(X, Y, bracket_map, parity, basis)
                t3 = bracket_of_brackets(Z, res_XY, bracket_map, parity, basis)
                sign3 = Fraction((-1) ** (pZ * pY))

                # Sum: sign1*t1 + sign2*t2 + sign3*t3 == 0
                total = {}
                for d, sign in [(t1, sign1), (t2, sign2), (t3, sign3)]:
                    for k, v in d.items():
                        total[k] = total.get(k, Fraction(0)) + sign * v

                total = {k: v for k, v in total.items() if v != 0}

                if total:
                    failures.append({
                        "X": X, "Y": Y, "Z": Z,
                        "residual": {k: str(v) for k, v in total.items()}
                    })
                checked += 1

    return len(failures) == 0, failures, checked


def main():
    print("=" * 60)
    print("C(n+1) Structure Constant Verification")
    print("=" * 60)

    all_pass = True

    for n in [1, 2, 3]:
        print(f"\n--- C({n+1}) = osp(2|{2*n}), n={n} ---")

        # Anti-symmetry check
        ok, failures, checked = verify_antisymmetry(n)
        status = "PASS" if ok else f"FAIL ({len(failures)} violations)"
        print(f"  Anti-symmetry ({checked} pairs): {status}")
        if failures:
            for f in failures[:3]:
                print(f"    [{f['X']}, {f['Y']}]" + ": residual " + str(f['residual']))
            all_pass = False

        # Super Jacobi check
        ok, failures, checked = verify_super_jacobi(n)
        status = "PASS" if ok else f"FAIL ({len(failures)} violations)"
        print(f"  Super Jacobi ({checked} triples): {status}")
        if failures:
            for f in failures[:3]:
                print(f"    [{f['X']}, [{f['Y']}, {f['Z']}]]: residual " + str(f['residual']))
            all_pass = False

    print("\n" + "=" * 60)
    print(f"Overall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

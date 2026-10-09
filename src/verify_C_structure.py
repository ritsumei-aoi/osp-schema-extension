"""
Verification script for C(n+1) structure constants.

Checks:
1. Graded anti-symmetry: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
2. Super Jacobi identity: (-1)^{p(X)p(Z)} [X,[Y,Z}] + cyclic = 0
"""

from __future__ import annotations
import json
import os
import sys
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, os.path.dirname(__file__))


def load_schema(n: int) -> dict:
    path = f"data/C_{n}_structure.json"
    with open(path) as f:
        return json.load(f)


def build_sc_dict(schema: dict) -> dict[tuple[str, str], dict[str, Fraction]]:
    """
    Build a dict: (X, Y) -> {Z: coeff} for the graded bracket [X,Y}.
    """
    sc: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in schema["structure_constants"]:
        key = (entry["X"], entry["Y"])
        if key not in sc:
            sc[key] = {}
        z = entry["Z"]
        c = Fraction(entry["coeff"])
        sc[key][z] = sc[key].get(z, Fraction(0)) + c
    # Remove zero entries
    for key in list(sc.keys()):
        sc[key] = {z: c for z, c in sc[key].items() if c != 0}
        if not sc[key]:
            del sc[key]
    return sc


def bracket(sc_dict, parity, X, Y):
    """Compute [X, Y} as dict {Z: coeff}."""
    result = {}
    for z, c in sc_dict.get((X, Y), {}).items():
        result[z] = result.get(z, Fraction(0)) + c
    return {z: c for z, c in result.items() if c != 0}


def add_dicts(d1, d2, sign=1):
    result = dict(d1)
    for z, c in d2.items():
        result[z] = result.get(z, Fraction(0)) + sign * c
    return {z: c for z, c in result.items() if c != 0}


def check_antisymmetry(schema, sc_dict, basis, parity):
    """Check [X,Y} = -(-1)^{p(X)*p(Y)} [Y,X} for all pairs."""
    failures = []
    all_gens = basis["even"] + basis["odd"]
    for X, Y in combinations(all_gens, 2):
        xy = bracket(sc_dict, parity, X, Y)
        yx = bracket(sc_dict, parity, Y, X)
        sign = (-1) ** (parity[X] * parity[Y])
        # [X,Y} + sign * [Y,X} should be 0
        combined = add_dicts(xy, yx, sign)
        if combined:
            failures.append((X, Y, combined))
    # Also check [X,X} for odd X
    for X in all_gens:
        if parity[X] == 1:
            # {X, X} might be nonzero, but we check [X,X} + [X,X} = 2*[X,X} should be [X,X}
            # Actually anti-symmetry: [X,X} = -(-1)^1 [X,X} = [X,X}, so no constraint on its own
            # from antisymmetry. [X,X} = {X,X} for odd X, which can be nonzero.
            pass
    return failures


def check_super_jacobi(schema, sc_dict, basis, parity):
    """
    Check Super Jacobi: sum over cyclic permutations of
    (-1)^{p(X)p(Z)} [X,[Y,Z}] = 0
    """
    failures = []
    all_gens = basis["even"] + basis["odd"]

    for X in all_gens:
        for Y in all_gens:
            for Z in all_gens:
                # (-1)^{p(X)p(Z)} [X,[Y,Z}] + (-1)^{p(Y)p(X)} [Y,[Z,X}] + (-1)^{p(Z)p(Y)} [Z,[X,Y}] = 0
                yz = bracket(sc_dict, parity, Y, Z)
                zx = bracket(sc_dict, parity, Z, X)
                xy = bracket(sc_dict, parity, X, Y)

                result = {}
                # Term 1: (-1)^{p(X)p(Z)} [X, [Y,Z}]
                sign1 = (-1) ** (parity[X] * parity[Z])
                for W, c in yz.items():
                    xw = bracket(sc_dict, parity, X, W)
                    for V, d in xw.items():
                        result[V] = result.get(V, Fraction(0)) + sign1 * c * d
                # Term 2: (-1)^{p(Y)p(X)} [Y, [Z,X}]
                sign2 = (-1) ** (parity[Y] * parity[X])
                for W, c in zx.items():
                    yw = bracket(sc_dict, parity, Y, W)
                    for V, d in yw.items():
                        result[V] = result.get(V, Fraction(0)) + sign2 * c * d
                # Term 3: (-1)^{p(Z)p(Y)} [Z, [X,Y}]
                sign3 = (-1) ** (parity[Z] * parity[Y])
                for W, c in xy.items():
                    zw = bracket(sc_dict, parity, Z, W)
                    for V, d in zw.items():
                        result[V] = result.get(V, Fraction(0)) + sign3 * c * d

                result = {V: c for V, c in result.items() if c != 0}
                if result:
                    failures.append((X, Y, Z, result))

    return failures


def verify_n(n: int) -> dict:
    schema = load_schema(n)
    sc_dict = build_sc_dict(schema)
    parity = schema["parity"]
    basis = schema["basis"]
    all_gens = basis["even"] + basis["odd"]

    print(f"\n=== Verifying C_{n}_structure.json (n={n}) ===")
    print(f"  Basis: {len(all_gens)} generators, {len(schema['structure_constants'])} structure constants")

    # Anti-symmetry
    asym_fails = check_antisymmetry(schema, sc_dict, basis, parity)
    if asym_fails:
        print(f"  FAIL: Anti-symmetry: {len(asym_fails)} failures")
        for f in asym_fails[:3]:
            print(f"    [{f[0]},{f[1]}]: residual={f[2]}")
    else:
        print(f"  PASS: Anti-symmetry checked for all {len(all_gens)*(len(all_gens)-1)//2} pairs")

    # Super Jacobi
    jac_fails = check_super_jacobi(schema, sc_dict, basis, parity)
    if jac_fails:
        print(f"  FAIL: Super Jacobi: {len(jac_fails)} failures")
        for f in jac_fails[:3]:
            print(f"    J({f[0]},{f[1]},{f[2]}): residual={f[3]}")
    else:
        print(f"  PASS: Super Jacobi checked for all {len(all_gens)**3} triples")

    return {
        "n": n,
        "antisymmetry_pass": len(asym_fails) == 0,
        "antisymmetry_failures": len(asym_fails),
        "jacobi_pass": len(jac_fails) == 0,
        "jacobi_failures": len(jac_fails),
    }


def main():
    results = []
    for n in [1, 2, 3]:
        r = verify_n(n)
        results.append(r)

    print("\n=== Summary ===")
    all_pass = True
    for r in results:
        status = "PASS" if r["antisymmetry_pass"] and r["jacobi_pass"] else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  n={r['n']}: antisymmetry={r['antisymmetry_pass']}, jacobi={r['jacobi_pass']} -> {status}")
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

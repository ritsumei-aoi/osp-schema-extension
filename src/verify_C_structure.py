"""
verify_C_structure.py: Verify anti-symmetry and Super Jacobi identity
for C(n+1) structure constants loaded from Schema 1 JSON files.

Super Jacobi identity (graded): for X,Y,Z homogeneous,
  (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0

Anti-symmetry (graded):
  [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
"""

import json
import sys
from fractions import Fraction
from itertools import product


def load_schema(n):
    fname = f"data/C_{n}_structure.json"
    with open(fname) as f:
        return json.load(f)


def build_sc_table(schema):
    """Build bracket table: sc[(X,Y)] = {Z: coeff} (as Fraction)."""
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    sc = {}
    for entry in schema["structure_constants"]:
        X, Y, Z, c = entry["X"], entry["Y"], entry["Z"], Fraction(entry["coeff"])
        key = (X, Y)
        if key not in sc:
            sc[key] = {}
        sc[key][Z] = sc[key].get(Z, Fraction(0)) + c
    # Clean up zeros
    for key in list(sc.keys()):
        sc[key] = {z: c for z, c in sc[key].items() if c != 0}
        if not sc[key]:
            del sc[key]
    return sc, basis, parity


def bracket(sc, parity, X, Y):
    """Compute [X,Y} as dict {Z: coeff}. Returns graded bracket."""
    px = parity.get(X, 0)
    py = parity.get(Y, 0)
    result = {}
    # Direct lookup
    direct = sc.get((X, Y), {})
    for z, c in direct.items():
        result[z] = result.get(z, Fraction(0)) + c
    # Reverse: [Y,X} = -(-1)^{px*py} [X,Y} rearranged:
    # [X,Y} stored; for [Y,X} we use anti-symmetry
    # But we store [X,Y} directly; check if (Y,X) has explicit entries
    # (some may be stored in reverse direction)
    reverse = sc.get((Y, X), {})
    sign = (-1) ** (px * py)
    for z, c in reverse.items():
        result[z] = result.get(z, Fraction(0)) - sign * c
    # Clean
    return {z: c for z, c in result.items() if c != 0}


def add_dicts(d1, d2):
    result = dict(d1)
    for k, v in d2.items():
        result[k] = result.get(k, Fraction(0)) + v
    return {k: v for k, v in result.items() if v != 0}


def scale_dict(d, s):
    return {k: v * s for k, v in d.items() if v * s != 0}


def bracket_composed(sc, parity, X, result_dict):
    """Compute [X, result_dict] = sum_Z coeff_Z [X, Z]."""
    out = {}
    for Z, c in result_dict.items():
        br = bracket(sc, parity, X, Z)
        for W, d in br.items():
            out[W] = out.get(W, Fraction(0)) + c * d
    return {k: v for k, v in out.items() if v != 0}


def verify_antisymmetry(sc, parity, basis, verbose=False):
    """Check [X,Y} + (-1)^{p(X)p(Y)} [Y,X} = 0 for all X,Y."""
    failures = []
    for X in basis:
        for Y in basis:
            px = parity.get(X, 0)
            py = parity.get(Y, 0)
            sign = (-1) ** (px * py)
            bXY = bracket(sc, parity, X, Y)
            bYX = bracket(sc, parity, Y, X)
            # [X,Y} + sign*[Y,X} should be 0
            combined = add_dicts(bXY, scale_dict(bYX, Fraction(sign)))
            if combined:
                failures.append((X, Y, combined))
    return failures


def verify_super_jacobi(sc, parity, basis, verbose=False):
    """Check Super Jacobi identity for all triples (X,Y,Z)."""
    failures = []
    for X in basis:
        for Y in basis:
            for Z in basis:
                px = parity.get(X, 0)
                py = parity.get(Y, 0)
                pz = parity.get(Z, 0)

                # Term 1: (-1)^{px*pz} [X,[Y,Z]]
                bYZ = bracket(sc, parity, Y, Z)
                t1 = scale_dict(bracket_composed(sc, parity, X, bYZ),
                                Fraction((-1) ** (px * pz)))

                # Term 2: (-1)^{py*px} [Y,[Z,X]]
                bZX = bracket(sc, parity, Z, X)
                t2 = scale_dict(bracket_composed(sc, parity, Y, bZX),
                                Fraction((-1) ** (py * px)))

                # Term 3: (-1)^{pz*py} [Z,[X,Y]]
                bXY = bracket(sc, parity, X, Y)
                t3 = scale_dict(bracket_composed(sc, parity, Z, bXY),
                                Fraction((-1) ** (pz * py)))

                total = add_dicts(add_dicts(t1, t2), t3)
                if total:
                    failures.append((X, Y, Z, total))
    return failures


def main():
    results = {}
    for n in [1, 2, 3]:
        print(f"\n=== C_{n} (C({n+1}) = osp(2|{2*n})) ===")
        schema = load_schema(n)
        sc, basis, parity = build_sc_table(schema)

        print(f"  Basis: {len(basis)} generators ({schema['algebra']['dimension']['even']} even, {schema['algebra']['dimension']['odd']} odd)")
        print(f"  Non-zero brackets: {len(schema['structure_constants'])}")

        print("  Checking anti-symmetry...", end=" ")
        asym_failures = verify_antisymmetry(sc, parity, basis)
        if asym_failures:
            print(f"FAIL ({len(asym_failures)} violations)")
            for X, Y, res in asym_failures[:3]:
                print(f"    [{X},{Y}] anti-symmetry violation: {res}")
        else:
            print("PASS")

        print("  Checking Super Jacobi identity...", end=" ")
        sj_failures = verify_super_jacobi(sc, parity, basis)
        if sj_failures:
            print(f"FAIL ({len(sj_failures)} violations)")
            for X, Y, Z, res in sj_failures[:3]:
                print(f"    [{X},{Y},{Z}] Jacobi violation: {res}")
        else:
            print("PASS")

        results[n] = {
            "antisymmetry": len(asym_failures) == 0,
            "super_jacobi": len(sj_failures) == 0,
            "asym_failures": len(asym_failures),
            "jacobi_failures": len(sj_failures)
        }

    print("\n=== Summary ===")
    all_pass = True
    for n, r in results.items():
        status = "PASS" if r["antisymmetry"] and r["super_jacobi"] else "FAIL"
        all_pass = all_pass and (r["antisymmetry"] and r["super_jacobi"])
        print(f"  C_{n}: antisymmetry={'OK' if r['antisymmetry'] else 'FAIL'}, "
              f"super_jacobi={'OK' if r['super_jacobi'] else 'FAIL'} [{status}]")
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    return results


if __name__ == "__main__":
    main()

"""
verify_C_structure.py: Load Schema 1 JSON and verify structure constants.

Checks:
  1. Graded anti-symmetry: [X,Y} + (-1)^{pX pY} [Y,X} = 0 for all pairs
  2. Super Jacobi identity:
       (-1)^{pX pZ}[X,[Y,Z}} + (-1)^{pY pX}[Y,[Z,X}} + (-1)^{pZ pY}[Z,[X,Y}} = 0
     for all unordered triples (with repetition).
"""

from fractions import Fraction
from collections import defaultdict
import json
from pathlib import Path
import sys
import time


def parse_coeff(s: str) -> Fraction:
    if '/' in s:
        a, b = s.split('/')
        return Fraction(int(a), int(b))
    return Fraction(int(s))


def load_and_build(n: int):
    """Load JSON and build full bracket table (both directions)."""
    path = Path(f'data/C_{n}_structure.json')
    with open(path) as f:
        schema = json.load(f)

    parity = {k: int(v) for k, v in schema['parity'].items()}
    all_gens = list(schema['basis']['even']) + list(schema['basis']['odd'])

    # Parse SC entries → forward table fwd[(X,Y)][Z] = Fraction
    fwd = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        c = parse_coeff(entry['coeff'])
        fwd[(X, Y)][Z] += c

    # Build full bracket table including reverse direction via anti-symmetry.
    # bt[X][Y] = {Z: Fraction} (zero bracket → empty dict)
    bt = {g: {h: {} for h in all_gens} for g in all_gens}

    for (X, Y), terms in fwd.items():
        # Forward direction
        for Z, c in terms.items():
            if c != 0:
                bt[X][Y][Z] = bt[X][Y].get(Z, Fraction(0)) + c
        # Reverse: [Y,X} = -(-1)^{pX pY} [X,Y}
        sign = Fraction((-1) ** (parity[X] * parity[Y]))
        for Z, c in terms.items():
            rc = -sign * c
            if rc != 0:
                bt[Y][X][Z] = bt[Y][X].get(Z, Fraction(0)) + rc

    # Clean up numerical zeros
    for X in all_gens:
        for Y in all_gens:
            bt[X][Y] = {Z: c for Z, c in bt[X][Y].items() if c != 0}

    return schema, parity, all_gens, bt


def check_antisymmetry(parity, all_gens, bt):
    """
    Verify [X,Y} + (-1)^{pX pY}[Y,X} = 0 for all ordered pairs.
    Since bt[Y][X] was constructed by applying anti-symmetry to bt[X][Y],
    this is a consistency check of the table construction (data loading).
    """
    failures = []
    for X in all_gens:
        for Y in all_gens:
            sign = (-1) ** (parity[X] * parity[Y])
            XY = bt[X][Y]
            YX = bt[Y][X]
            all_Z = set(XY.keys()) | set(YX.keys())
            for Z in all_Z:
                res = XY.get(Z, Fraction(0)) + sign * YX.get(Z, Fraction(0))
                if res != 0:
                    failures.append((X, Y, Z, res))
    return failures


def bracket_of(X, elem, bt):
    """Compute [X, elem} by multilinearity: elem = {W: coeff} → Σ coeff·[X,W}."""
    result = defaultdict(Fraction)
    for W, cW in elem.items():
        for U, c in bt[X][W].items():
            result[U] += cW * c
    return {k: v for k, v in result.items() if v != 0}


def check_jacobi(parity, all_gens, bt):
    """
    Verify Super Jacobi for all unordered triples (i <= j <= k):
      (-1)^{pX pZ}[X,[Y,Z}} + (-1)^{pY pX}[Y,[Z,X}} + (-1)^{pZ pY}[Z,[X,Y}} = 0
    This is a genuine algebraic check (nontrivial combinations of SC entries).
    Returns (failures list, triple_count).
    """
    failures = []
    triple_count = 0
    N = len(all_gens)

    for i in range(N):
        X = all_gens[i]
        pX = parity[X]
        for j in range(i, N):
            Y = all_gens[j]
            pY = parity[Y]
            for k in range(j, N):
                Z = all_gens[k]
                pZ = parity[Z]
                triple_count += 1

                YZ = bt[Y][Z]
                ZX = bt[Z][X]
                XY = bt[X][Y]

                if not YZ and not ZX and not XY:
                    continue

                X_YZ = bracket_of(X, YZ, bt) if YZ else {}
                Y_ZX = bracket_of(Y, ZX, bt) if ZX else {}
                Z_XY = bracket_of(Z, XY, bt) if XY else {}

                if not X_YZ and not Y_ZX and not Z_XY:
                    continue

                s1 = (-1) ** (pX * pZ)
                s2 = (-1) ** (pY * pX)
                s3 = (-1) ** (pZ * pY)

                jacobi = defaultdict(Fraction)
                for W, c in X_YZ.items():
                    jacobi[W] += s1 * c
                for W, c in Y_ZX.items():
                    jacobi[W] += s2 * c
                for W, c in Z_XY.items():
                    jacobi[W] += s3 * c
                jacobi = {k: v for k, v in jacobi.items() if v != 0}

                if jacobi:
                    failures.append((X, Y, Z, dict(jacobi)))

    return failures, triple_count


def verify(n: int) -> bool:
    t0 = time.time()
    print(f"\n=== C({n+1}) = osp(2|{2*n}) ===")
    schema, parity, all_gens, bt = load_and_build(n)
    dim = schema['algebra']['dimension']
    sc_count = len(schema['structure_constants'])
    print(f"  Generators: {len(all_gens)}  (even: {dim['even']}, odd: {dim['odd']})")
    print(f"  SC JSON entries: {sc_count}")

    # Check 1: Anti-symmetry
    asym_fails = check_antisymmetry(parity, all_gens, bt)
    N = len(all_gens)
    if asym_fails:
        print(f"  [FAIL] Anti-symmetry: {len(asym_fails)} inconsistencies")
        for X, Y, Z, r in asym_fails[:5]:
            print(f"    ({X},{Y},{Z}): residual = {r}")
    else:
        print(f"  [PASS] Anti-symmetry: {N}x{N} = {N*N} ordered pairs consistent")

    # Check 2: Super Jacobi identity
    jac_fails, triple_count = check_jacobi(parity, all_gens, bt)
    t1 = time.time()
    if jac_fails:
        print(f"  [FAIL] Jacobi: {len(jac_fails)} failures / {triple_count} triples  ({t1-t0:.2f}s)")
        for X, Y, Z, r in jac_fails[:5]:
            print(f"    ({X},{Y},{Z}): residual = {r}")
    else:
        print(f"  [PASS] Jacobi: all {triple_count} triples (i<=j<=k) OK  ({t1-t0:.2f}s)")

    return len(asym_fails) == 0 and len(jac_fails) == 0


def main():
    all_pass = True
    for n in [1, 2, 3]:
        ok = verify(n)
        all_pass = all_pass and ok

    print("\n" + "=" * 40)
    if all_pass:
        print("RESULT: ALL CHECKS PASSED")
    else:
        print("RESULT: SOME CHECKS FAILED — see details above")
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())

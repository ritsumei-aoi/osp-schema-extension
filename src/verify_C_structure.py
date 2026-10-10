#!/usr/bin/env python3
"""
Verification script for C(n+1) structure constants.
Checks graded anti-symmetry and Super Jacobi identity.

Usage: python verify_C_structure.py [data_dir]
  data_dir: path to directory containing C_1_structure.json, etc.
             defaults to ../data relative to this script's location.
"""

import json
import sys
from fractions import Fraction
from pathlib import Path


def load_structure(path):
    with open(path) as f:
        return json.load(f)


def build_raw_bracket(data):
    """Build directly-stored brackets from structure_constants array.
    Returns basis, parity dict, raw_bracket dict.
    raw_bracket[(X,Y)] = {Z: Fraction(coeff)}
    """
    basis = data['basis']['odd'] + data['basis']['even']
    parity = {g: data['parity'][g] for g in basis}

    raw_bracket = {}
    for entry in data['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        coeff = Fraction(entry['coeff'])
        key = (X, Y)
        if key not in raw_bracket:
            raw_bracket[key] = {}
        raw_bracket[key][Z] = raw_bracket[key].get(Z, Fraction(0)) + coeff

    # Remove zero coefficients
    for key in list(raw_bracket):
        raw_bracket[key] = {z: c for z, c in raw_bracket[key].items() if c != 0}
        if not raw_bracket[key]:
            del raw_bracket[key]

    return basis, parity, raw_bracket


def full_bracket(X, Y, raw_bracket, parity):
    """Compute [X, Y] using stored data; derive via graded anti-symmetry if only [Y,X] stored.
    Returns {Z: Fraction(coeff)}.
    Graded anti-symmetry: [X,Y] = -(-1)^(p(X)*p(Y)) [Y,X]
    """
    if (X, Y) in raw_bracket:
        return dict(raw_bracket[(X, Y)])
    elif (Y, X) in raw_bracket:
        px, py = parity[X], parity[Y]
        # sign = -(-1)^(px*py)
        sign = Fraction(-1) * Fraction((-1) ** (px * py))
        return {z: sign * c for z, c in raw_bracket[(Y, X)].items()}
    else:
        return {}


def add_dicts(d1, d2):
    """Add two {Z: coeff} dicts."""
    result = dict(d1)
    for k, v in d2.items():
        result[k] = result.get(k, Fraction(0)) + v
    return {k: v for k, v in result.items() if v != 0}


def scale_dict(d, s):
    return {k: v * s for k, v in d.items()}


def check_antisymmetry(basis, parity, raw_bracket):
    """Check graded anti-symmetry.

    For all stored (X,Y), if (Y,X) is also stored, verify:
      [X,Y] + (-1)^(p(X)*p(Y)) [Y,X] = 0.
    For diagonal (X,X) with even X, verify [X,X] = 0.

    Returns list of (X, Y, residual_dict) failures.
    """
    failures = []
    checked = set()

    for (X, Y) in raw_bracket:
        if (X, Y) in checked:
            continue
        px, py = parity[X], parity[Y]

        if X == Y:
            # Diagonal: even generators must have [X,X]=0
            if px == 0:
                xy = raw_bracket[(X, Y)]
                if xy:
                    failures.append((X, Y, dict(xy)))
            # Odd diagonal: [X,X] = {X,X} can be nonzero; no constraint from anti-sym alone
        elif (Y, X) in raw_bracket:
            # Both stored: check consistency
            sign = Fraction((-1) ** (px * py))
            residual = add_dicts(raw_bracket[(X, Y)], scale_dict(raw_bracket[(Y, X)], sign))
            if residual:
                failures.append((X, Y, residual))
            checked.add((X, Y))
            checked.add((Y, X))
        else:
            checked.add((X, Y))

    return failures


def compute_bracket_of_linear_combo(combo, Y, raw_bracket, parity):
    """Compute [combo, Y] where combo = {X: coeff}.
    Returns {Z: coeff}.
    """
    result = {}
    for X, cX in combo.items():
        inner = full_bracket(X, Y, raw_bracket, parity)
        for Z, cZ in inner.items():
            result[Z] = result.get(Z, Fraction(0)) + cX * cZ
    return {z: c for z, c in result.items() if c != 0}


def check_super_jacobi(basis, parity, raw_bracket):
    """Check Super Jacobi identity for all triples (X, Y, Z):
      (-1)^(p(X)*p(Z)) [X,[Y,Z]] + (-1)^(p(Y)*p(X)) [Y,[Z,X]] + (-1)^(p(Z)*p(Y)) [Z,[X,Y]] = 0.

    Returns list of (X, Y, Z, residual_dict) failures.
    """
    failures = []
    n = len(basis)

    for i, X in enumerate(basis):
        px = parity[X]
        for j, Y in enumerate(basis):
            py = parity[Y]
            for k, Z in enumerate(basis):
                pz = parity[Z]

                # Term 1: (-1)^(px*pz) [X, [Y,Z]]
                yz = full_bracket(Y, Z, raw_bracket, parity)
                t1 = compute_bracket_of_linear_combo(yz, X, raw_bracket, parity)
                # Wait: [X, [Y,Z]] not [[Y,Z], X]. Let me fix.
                # [X, res] where res = [Y,Z] = {W: cW}
                # = sum_W cW [X, W]
                t1 = {}
                for W, cW in yz.items():
                    xw = full_bracket(X, W, raw_bracket, parity)
                    for V, cV in xw.items():
                        t1[V] = t1.get(V, Fraction(0)) + Fraction((-1)**(px * pz)) * cW * cV

                # Term 2: (-1)^(py*px) [Y, [Z,X]]
                zx = full_bracket(Z, X, raw_bracket, parity)
                t2 = {}
                for W, cW in zx.items():
                    yw = full_bracket(Y, W, raw_bracket, parity)
                    for V, cV in yw.items():
                        t2[V] = t2.get(V, Fraction(0)) + Fraction((-1)**(py * px)) * cW * cV

                # Term 3: (-1)^(pz*py) [Z, [X,Y]]
                xy = full_bracket(X, Y, raw_bracket, parity)
                t3 = {}
                for W, cW in xy.items():
                    zw = full_bracket(Z, W, raw_bracket, parity)
                    for V, cV in zw.items():
                        t3[V] = t3.get(V, Fraction(0)) + Fraction((-1)**(pz * py)) * cW * cV

                # Sum all three terms
                total = {}
                for d in [t1, t2, t3]:
                    for v, c in d.items():
                        total[v] = total.get(v, Fraction(0)) + c
                total = {v: c for v, c in total.items() if c != 0}

                if total:
                    failures.append((X, Y, Z, total))

    return failures


def verify_file(path, label):
    print(f"\n{'='*60}")
    print(f"Verifying: {label}  [{path.name}]")
    print('='*60)

    data = load_structure(path)
    n = data['algebra']['n']
    dim = data['algebra']['dimension']
    print(f"  Algebra : {data['algebra']['cartan_type']} = osp(2|{2*n}), n={n}")
    print(f"  Dim     : total={dim['total']}, even={dim['even']}, odd={dim['odd']}")

    basis, parity, raw_bracket = build_raw_bracket(data)
    print(f"  Basis   : {len(basis)} generators")
    print(f"  SC entries (stored): {len(data['structure_constants'])}")

    # ---- Anti-symmetry ----
    print("\n  [1] Graded anti-symmetry check ...")
    asym_fails = check_antisymmetry(basis, parity, raw_bracket)
    if asym_fails:
        print(f"  FAIL: {len(asym_fails)} violation(s)")
        for X, Y, res in asym_fails[:5]:
            print(f"    [X={X}, Y={Y}] residual = {dict(res)}")
    else:
        print(f"  PASS: all stored bracket pairs satisfy graded anti-symmetry")

    # ---- Super Jacobi ----
    dim_basis = len(basis)
    total_triples = dim_basis ** 3
    print(f"\n  [2] Super Jacobi identity check ({total_triples} ordered triples) ...")
    jacobi_fails = check_super_jacobi(basis, parity, raw_bracket)
    if jacobi_fails:
        print(f"  FAIL: {len(jacobi_fails)} violation(s)")
        for X, Y, Z, res in jacobi_fails[:5]:
            print(f"    Jacobi([{X},{Y},{Z}]) residual = {dict(res)}")
    else:
        print(f"  PASS: all {total_triples} triples satisfy Super Jacobi identity")

    passed = (len(asym_fails) == 0 and len(jacobi_fails) == 0)
    return passed, {
        'asym_failures': len(asym_fails),
        'jacobi_failures': len(jacobi_fails),
        'asym_details': asym_fails[:10],
        'jacobi_details': jacobi_fails[:10],
        'basis_size': dim_basis,
        'total_triples': total_triples,
    }


def main():
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1])
    else:
        data_dir = Path(__file__).parent.parent / 'data'

    print("C(n+1) Structure Constant Verification")
    print("Checks: graded anti-symmetry + Super Jacobi identity")
    print(f"Data directory: {data_dir}")

    all_pass = True
    summary = {}

    for n in [1, 2, 3]:
        path = data_dir / f'C_{n}_structure.json'
        if not path.exists():
            print(f"\nERROR: {path} not found!")
            all_pass = False
            summary[n] = {'status': 'FILE_MISSING'}
            continue
        label = f"C_{n}_structure (n={n})"
        passed, info = verify_file(path, label)
        summary[n] = {'status': 'PASS' if passed else 'FAIL', **info}
        if not passed:
            all_pass = False

    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print('='*60)
    for n, info in summary.items():
        status = info['status']
        if status in ('PASS', 'FAIL'):
            asym = info['asym_failures']
            jac = info['jacobi_failures']
            triples = info['total_triples']
            print(f"  n={n}: {status:4s}  anti-sym failures={asym}  "
                  f"Jacobi failures={jac}/{triples} triples")
        else:
            print(f"  n={n}: {status}")

    if all_pass:
        print("\nOVERALL RESULT: ALL CHECKS PASSED ✓")
    else:
        print("\nOVERALL RESULT: FAILURES DETECTED — root cause analysis required")

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())

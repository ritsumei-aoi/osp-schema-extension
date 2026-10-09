#!/usr/bin/env python3
"""
Verification script for C(n+1) structure constants.

Checks:
1. Graded antisymmetry: [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
2. Super Jacobi identity: (-1)^{p(X)p(Z)} [X,[Y,Z}} + cyclic = 0

Loads from data/C_{n}_structure.json.
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load_structure(n):
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


def build_bracket_map(data):
    """Build a map: (X, Y) -> {Z: Fraction(coeff)} from structure constants."""
    basis = data['basis']['even'] + data['basis']['odd']
    parity = data['parity']
    bracket = {}

    for label in basis:
        for label2 in basis:
            bracket[(label, label2)] = {}

    for sc in data['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        c = Fraction(sc['coeff'])
        if (X, Y) not in bracket:
            bracket[(X, Y)] = {}
        bracket[(X, Y)][Z] = bracket[(X, Y)].get(Z, Fraction(0)) + c

    return bracket, parity, basis


def apply_bracket(bracket, X, Y, parity, basis):
    """Return {Z: coeff} for [X,Y}."""
    result = bracket.get((X, Y), {})
    return {k: v for k, v in result.items() if v != 0}


def triple_bracket(bracket, X, Y, Z, parity, basis):
    """Compute [X, [Y, Z}}."""
    inner = apply_bracket(bracket, Y, Z, parity, basis)
    result = defaultdict(Fraction)
    for w, cw in inner.items():
        outer = apply_bracket(bracket, X, w, parity, basis)
        for u, cu in outer.items():
            result[u] += cw * cu
    return {k: v for k, v in result.items() if v != 0}


def check_antisymmetry(data):
    """Check [X,Y} = -(-1)^{p(X)p(Y)} [Y,X} for all X, Y."""
    bracket, parity, basis = build_bracket_map(data)
    failures = []
    total = 0
    for X in basis:
        for Y in basis:
            total += 1
            XY = bracket.get((X, Y), {})
            YX = bracket.get((Y, X), {})
            sign = -1 if (parity[X] * parity[Y]) % 2 == 1 else 1
            # Check: XY + sign * YX == 0
            diff = defaultdict(Fraction)
            for z, c in XY.items():
                diff[z] += c
            for z, c in YX.items():
                diff[z] += Fraction(sign) * c
            diff = {k: v for k, v in diff.items() if v != 0}
            if diff:
                failures.append((X, Y, diff))
    return failures, total


def check_super_jacobi(data):
    """Check Super Jacobi identity for all triples (X, Y, Z).

    Graded Jacobi: (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0
    """
    bracket, parity, basis = build_bracket_map(data)
    failures = []
    total = 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                total += 1
                pX = parity[X]
                pY = parity[Y]
                pZ = parity[Z]

                # Term 1: (-1)^{pX*pZ} [X, [Y,Z}}
                s1 = (-1) ** (pX * pZ)
                t1 = triple_bracket(bracket, X, Y, Z, parity, basis)
                # Term 2: (-1)^{pY*pX} [Y, [Z,X}}
                s2 = (-1) ** (pY * pX)
                t2 = triple_bracket(bracket, Y, Z, X, parity, basis)
                # Term 3: (-1)^{pZ*pY} [Z, [X,Y}}
                s3 = (-1) ** (pZ * pY)
                t3 = triple_bracket(bracket, Z, X, Y, parity, basis)

                combined = defaultdict(Fraction)
                for w, c in t1.items():
                    combined[w] += Fraction(s1) * c
                for w, c in t2.items():
                    combined[w] += Fraction(s2) * c
                for w, c in t3.items():
                    combined[w] += Fraction(s3) * c
                combined = {k: v for k, v in combined.items() if v != 0}
                if combined:
                    failures.append((X, Y, Z, combined))
    return failures, total


def run_verification(n):
    print(f'\n=== C({n+1}) (n={n}) ===')
    data = load_structure(n)
    basis = data['basis']['even'] + data['basis']['odd']
    dim = len(basis)
    print(f'Dimension: {dim}')

    # Antisymmetry
    print('Checking antisymmetry...')
    asym_failures, asym_total = check_antisymmetry(data)
    if asym_failures:
        print(f'FAIL: {len(asym_failures)}/{asym_total} antisymmetry violations')
        for X, Y, diff in asym_failures[:5]:
            print(f'  [{X}, {Y}]: discrepancy = {diff}')
    else:
        print(f'PASS: all {asym_total} antisymmetry checks passed')

    # Super Jacobi
    print('Checking Super Jacobi identity...')
    jacobi_failures, jacobi_total = check_super_jacobi(data)
    if jacobi_failures:
        print(f'FAIL: {len(jacobi_failures)}/{jacobi_total} Jacobi violations')
        for X, Y, Z, res in jacobi_failures[:5]:
            print(f'  Jacobi({X},{Y},{Z}) = {res}')
    else:
        print(f'PASS: all {jacobi_total} Jacobi checks passed')

    return len(asym_failures) == 0 and len(jacobi_failures) == 0


def main():
    all_pass = True
    for n in [1, 2, 3]:
        ok = run_verification(n)
        all_pass = all_pass and ok

    print('\n=== Summary ===')
    if all_pass:
        print('ALL CHECKS PASSED')
    else:
        print('SOME CHECKS FAILED')
        sys.exit(1)


if __name__ == '__main__':
    main()

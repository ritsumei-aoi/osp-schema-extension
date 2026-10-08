"""Verify the Schema 1 files data/C_{n}_structure.json for n = 1, 2, 3.

This script reads only the JSON files. It does not import the oscillator engine, so it checks the
written structure constants themselves.

Checks, for every pair and every triple of basis elements:
  * parity grading: every structure constant [X,Y] -> Z satisfies p(Z) = p(X) + p(Y) mod 2
  * anti-symmetry:  [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]
  * super-Jacobi:   [X,[Y,Z]] = [[X,Y],Z] + (-1)^{p(X)p(Y)} [Y,[X,Z]]

Usage:  python3 src/verify_C_structure.py
"""

import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)


def load_structure(n, data_dir=DATA_DIR):
    path = os.path.join(data_dir, 'C_%d_structure.json' % n)
    with open(path, encoding='utf-8') as fh:
        doc = json.load(fh)
    basis = doc['basis']['even'] + doc['basis']['odd']
    parity = {label: doc['parity'][label] for label in basis}
    table = {}
    for entry in doc['structure_constants']:
        key = (entry['X'], entry['Y'])
        table.setdefault(key, {})[entry['Z']] = Fraction(entry['coeff'])
    return doc, basis, parity, table


def bracket(table, u, v):
    """Bracket of two vectors (dicts label -> Fraction) using the structure-constant table."""
    out = {}
    for x, a in u.items():
        for y, b in v.items():
            for z, c in table.get((x, y), {}).items():
                out[z] = out.get(z, 0) + a * b * c
    return {z: c for z, c in out.items() if c != 0}


def add(u, v, sign=1):
    out = dict(u)
    for k, c in v.items():
        out[k] = out.get(k, 0) + sign * c
    return {k: c for k, c in out.items() if c != 0}


def check_table(basis, parity, table):
    """Run all checks on a structure-constant table.  Returns (pairs, triples, failures)."""
    failures = {'parity': [], 'antisymmetry': [], 'jacobi': []}

    for (x, y), img in table.items():
        for z in img:
            if (parity[z] - parity[x] - parity[y]) % 2 != 0:
                failures['parity'].append((x, y, z))

    pairs = 0
    for x in basis:
        for y in basis:
            pairs += 1
            sign = (-1) ** (parity[x] * parity[y])
            lhs = table.get((x, y), {})
            rhs = table.get((y, x), {})
            if add(lhs, rhs, sign):
                failures['antisymmetry'].append((x, y))

    triples = 0
    for x in basis:
        for y in basis:
            for z in basis:
                triples += 1
                sign = (-1) ** (parity[x] * parity[y])
                yz = bracket(table, {y: Fraction(1)}, {z: Fraction(1)})
                xz = bracket(table, {x: Fraction(1)}, {z: Fraction(1)})
                xy = bracket(table, {x: Fraction(1)}, {y: Fraction(1)})
                left = bracket(table, {x: Fraction(1)}, yz)
                right = add(bracket(table, xy, {z: Fraction(1)}),
                            bracket(table, {y: Fraction(1)}, xz), sign)
                if add(left, right, -1):
                    failures['jacobi'].append((x, y, z))
    return pairs, triples, failures


def verify(n, data_dir=DATA_DIR):
    doc, basis, parity, table = load_structure(n, data_dir)
    pairs, triples, failures = check_table(basis, parity, table)
    status = 'PASS' if not any(failures.values()) else 'FAIL'
    return {
        'n': n,
        'algebra': 'C(%d)' % (n + 1),
        'dimension': len(basis),
        'pairs_checked': pairs,
        'triples_checked': triples,
        'nonzero_structure_constants': sum(len(v) for v in table.values()),
        'parity_violations': len(failures['parity']),
        'antisymmetry_failures': len(failures['antisymmetry']),
        'jacobi_failures': len(failures['jacobi']),
        'status': status,
        'failure_samples': {k: v[:5] for k, v in failures.items()},
    }


def main():
    reports = []
    for n in RANKS:
        report = verify(n)
        reports.append(report)
        print('n=%d %s dim=%d pairs=%d triples=%d parity=%d antisym=%d jacobi=%d -> %s' % (
            n, report['algebra'], report['dimension'], report['pairs_checked'],
            report['triples_checked'], report['parity_violations'],
            report['antisymmetry_failures'], report['jacobi_failures'], report['status']))
    with open(os.path.join(DATA_DIR, 'C_structure_verification.json'), 'w', encoding='utf-8') as fh:
        json.dump(reports, fh, indent=2)
        fh.write('\n')
    return 0 if all(r['status'] == 'PASS' for r in reports) else 1


if __name__ == '__main__':
    raise SystemExit(main())

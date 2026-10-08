"""Verify Schema 1 structure constants of C(n+1) from the JSON files alone (I04).

The script does not import the oscillator engine. It reads
``data/C_{n}_structure.json`` and checks:

1. Format: each entry's labels exist, parity of Z equals p(X)+p(Y) mod 2,
   and no closure residual (Z == "K") is present.
2. Anti-symmetry (super-skew): for every ordered pair the bracket is
   [Y,X] = -(-1)^{p(X)p(Y)} [X,Y]. The JSON stores pairs with index(X) <= index(Y);
   the reverse order is derived from that rule and must agree with any reverse
   entry present.
3. Super-Jacobi identity for every triple (X,Y,Z) of basis elements:
       [X,[Y,Z]] = [[X,Y],Z] + (-1)^{p(X)p(Y)} [Y,[X,Z]].

Usage:  python src/verify_C_structure.py      (exit code 1 if any check fails)
"""

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def load(n):
    with open(DATA_DIR / f'C_{n}_structure.json', encoding='utf-8') as f:
        return json.load(f)


def build_table(schema):
    """Return (labels, parity, table) with table[(i, j)] = {k: Fraction} for all i, j."""
    # PBW order fixed in I01: odd block first, then even block
    labels = schema['basis']['odd'] + schema['basis']['even']
    index = {lab: i for i, lab in enumerate(labels)}
    parity = [schema['parity'][lab] for lab in labels]
    stored = {}
    failures = []
    for entry in schema['structure_constants']:
        if entry['Z'] == 'K':
            failures.append(f"closure residual: {entry}")
            continue
        X, Y, Z = index[entry['X']], index[entry['Y']], index[entry['Z']]
        if Z in stored.get((X, Y), {}):
            failures.append(f"duplicate entry for [{entry['X']},{entry['Y']}] -> {entry['Z']}")
        stored.setdefault((X, Y), {})[Z] = Fraction(entry['coeff'])
        if parity[Z] != (parity[X] + parity[Y]) % 2:
            failures.append(f"parity violated: [{entry['X']},{entry['Y']}] -> {entry['Z']}")
        if X > Y:
            failures.append(f"entry not in index order: [{entry['X']},{entry['Y']}]")

    table = {}
    for i in range(len(labels)):
        for j in range(len(labels)):
            sign = -1 if (parity[i] * parity[j]) % 2 else 1
            if i <= j:
                table[(i, j)] = stored.get((i, j), {})
            else:
                # [X_i, X_j] = -(-1)^{p_i p_j} [X_j, X_i]
                forward = stored.get((j, i), {})
                table[(i, j)] = {k: -sign * v for k, v in forward.items()}
                if (i, j) in stored:
                    failures.append(f"reverse-order entry present for ({labels[i]},{labels[j]})")
    # self-bracket of an even element must vanish (super-skew with sign +1)
    for i in range(len(labels)):
        if parity[i] == 0 and table[(i, i)]:
            failures.append(f"even element {labels[i]} has nonzero [X,X]")
    return labels, parity, table, failures


def bracket(u, v, table):
    out = {}
    for i, a in u.items():
        for j, b in v.items():
            for k, c in table[(i, j)].items():
                out[k] = out.get(k, 0) + a * b * c
    return {k: x for k, x in out.items() if x != 0}


def add(*terms):
    out = {}
    for sign, vec in terms:
        for k, x in vec.items():
            out[k] = out.get(k, 0) + sign * x
    return {k: x for k, x in out.items() if x != 0}


def check_jacobi(labels, parity, table):
    n = len(labels)
    failures = []
    checked = 0
    for x in range(n):
        for y in range(n):
            for z in range(n):
                X, Y, Z = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                lhs = bracket(X, bracket(Y, Z, table), table)
                xy = bracket(X, Y, table)
                xz = bracket(X, Z, table)
                s = -1 if (parity[x] * parity[y]) % 2 else 1
                rhs = add((1, bracket(xy, Z, table)),
                          (s, bracket(Y, xz, table)))
                checked += 1
                if add((1, lhs), (-1, rhs)):
                    failures.append((labels[x], labels[y], labels[z]))
    return checked, failures


def main():
    all_ok = True
    for n in (1, 2, 3):
        schema = load(n)
        labels, parity, table, fmt_failures = build_table(schema)
        n_even = sum(1 for p in parity if p == 0)
        n_odd = len(parity) - n_even
        checked, jac_failures = check_jacobi(labels, parity, table)
        ok = not fmt_failures and not jac_failures
        all_ok &= ok
        print(f'n={n} C({n + 1}): dim={len(labels)} (even {n_even}, odd {n_odd})')
        print(f'  format and super-skew checks: {"PASS" if not fmt_failures else "FAIL"}'
              f' ({len(fmt_failures)} failures)')
        for msg in fmt_failures[:5]:
            print(f'    {msg}')
        print(f'  super-Jacobi triples checked: {checked}')
        print(f'  super-Jacobi: {"PASS" if not jac_failures else "FAIL"}'
              f' ({len(jac_failures)} failing triples)')
        for t in jac_failures[:5]:
            print(f'    {t}')
    print('OVERALL:', 'PASS' if all_ok else 'FAIL')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())

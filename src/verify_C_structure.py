"""Verify C(n+1) Schema 1 structure constants (I04).

Independent of the generator: works only from the JSON files.

Checks, for n = 1, 2, 3:
  1. Graded anti-symmetry:  [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}  for all pairs.
  2. Super Jacobi identity for all ordered triples (X, Y, Z):
     (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0.

Usage: python3 src/verify_C_structure.py
"""

import itertools
import json
import os
import sys
from fractions import Fraction

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        data = json.load(f)
    labels = data["basis"]["odd"] + data["basis"]["even"]
    parity = {l: data["parity"][l] for l in labels}
    bracket = {}
    for rec in data["structure_constants"]:
        key = (rec["X"], rec["Y"])
        bracket.setdefault(key, {})
        z = rec["Z"]
        bracket[key][z] = bracket[key].get(z, Fraction(0)) + Fraction(rec["coeff"])
    return labels, parity, bracket


def brk(bracket, x, y):
    return bracket.get((x, y), {})


def add_scaled(acc, terms, scale):
    for z, c in terms.items():
        acc[z] = acc.get(z, Fraction(0)) + scale * c
        if acc[z] == 0:
            del acc[z]


def verify(n, verbose=True):
    labels, parity, bracket = load(n)
    anti_fail = []
    jacobi_fail = []

    # 1. graded anti-symmetry
    for x, y in itertools.product(labels, repeat=2):
        sign = -1 if (parity[x] and parity[y]) else 1
        lhs = brk(bracket, x, y)
        rhs = brk(bracket, y, x)
        acc = dict(lhs)
        add_scaled(acc, rhs, Fraction(sign))
        if acc:
            anti_fail.append((x, y, acc))

    # 2. super Jacobi
    def sgn(a, b):
        return -1 if (parity[a] and parity[b]) else 1

    for x, y, z in itertools.product(labels, repeat=3):
        acc = {}
        for (a, b, c) in ((x, y, z), (y, z, x), (z, x, y)):
            outer_sign = Fraction(sgn(a, c))
            inner = brk(bracket, b, c)
            for w, cw in inner.items():
                add_scaled(acc, brk(bracket, a, w), outer_sign * cw)
        if acc:
            jacobi_fail.append((x, y, z, acc))

    n_pairs = len(labels) ** 2
    n_triples = len(labels) ** 3
    ok = not anti_fail and not jacobi_fail
    if verbose:
        print(f"C({n + 1}) [n={n}]: {len(labels)} basis elements")
        print(f"  anti-symmetry : {n_pairs} pairs checked, {len(anti_fail)} failures")
        print(f"  super Jacobi  : {n_triples} triples checked, {len(jacobi_fail)} failures")
        for f in anti_fail[:5]:
            print("    ANTI FAIL:", f)
        for f in jacobi_fail[:5]:
            print("    JACOBI FAIL:", f)
        print(f"  => {'PASS' if ok else 'FAIL'}")
    return ok, len(anti_fail), len(jacobi_fail), n_pairs, n_triples


def main():
    all_ok = True
    for n in (1, 2, 3):
        ok, *_ = verify(n)
        all_ok = all_ok and ok
    print("SUMMARY:", "ALL PASS" if all_ok else "FAILURES PRESENT")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

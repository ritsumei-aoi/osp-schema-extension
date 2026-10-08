"""Issue I04: verify super-antisymmetry and the super Jacobi identity for C_{n}_structure.json.

Uses ONLY the structure constants stored in the JSON files (independent of the
oscillator engine that produced them).

Usage: python3 src/verify_C_structure.py [n ...]   (default 1 2 3)
Exit code 0 iff all checks pass.
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import LieSuperalgebra, vec_add  # noqa: E402


def check_antisymmetry(g: LieSuperalgebra):
    """[X,Y} = -(-1)^{p(X)p(Y)} [Y,X} for all ordered pairs (including zero brackets)."""
    failures = []
    for X, Y in product(g.labels, repeat=2):
        sign = -1 if (g.parity[X] and g.parity[Y]) else 1
        lhs = g.bracket(X, Y)
        rhs = {Z: -sign * c for Z, c in g.bracket(Y, X).items()}
        if lhs != rhs:
            failures.append((X, Y, lhs, rhs))
    return failures


def check_jacobi(g: LieSuperalgebra):
    """(-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0."""
    failures = []
    count = 0
    for X, Y, Z in product(g.labels, repeat=3):
        count += 1
        total = {}
        for (A, B, C) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
            sign = Fraction(-1 if (g.parity[A] and g.parity[C]) else 1)
            total = vec_add(total, g.bracket_vec(A, g.bracket(B, C)), sign)
        if total:
            failures.append((X, Y, Z, total))
    return count, failures


def check_parity_closure(g: LieSuperalgebra):
    """p(Z) = p(X)+p(Y) mod 2 for every stored bracket, and all labels are basis labels."""
    failures = []
    for (X, Y), br in g.table.items():
        for Z in br:
            if Z not in g.parity or (g.parity[X] + g.parity[Y]) % 2 != g.parity[Z]:
                failures.append((X, Y, Z))
    return failures


def verify(n: int) -> bool:
    g = LieSuperalgebra.load(n)
    d = len(g.labels)
    print(f"=== C({n+1}) = osp(2|{2*n})  [C_{n}_structure.json]: dim {d}, "
          f"{len(g.table)} non-zero ordered brackets ===")
    pf = check_parity_closure(g)
    print(f"parity/label closure : {'PASS' if not pf else 'FAIL'} ({len(g.table)} brackets checked)")
    af = check_antisymmetry(g)
    print(f"super-antisymmetry   : {'PASS' if not af else 'FAIL'} ({d*d} ordered pairs checked)")
    cnt, jf = check_jacobi(g)
    print(f"super-Jacobi         : {'PASS' if not jf else 'FAIL'} ({cnt} ordered triples checked)")
    for X, Y, lhs, rhs in af[:10]:
        print(f"  antisymmetry failure: [{X},{Y}}}={lhs} vs expected {rhs}")
    for X, Y, Z, tot in jf[:10]:
        print(f"  Jacobi failure: ({X},{Y},{Z}) residual {tot}")
    ok = not (pf or af or jf)
    print(f"result               : {'ALL PASS' if ok else 'FAILURES'}")
    return ok


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    results = [verify(n) for n in ns]
    print("SUMMARY:", " ".join(f"n={n}:{'PASS' if r else 'FAIL'}" for n, r in zip(ns, results)))
    sys.exit(0 if all(results) else 1)

"""
Issue I04: verify the Schema 1 structure constants of C(n+1).

Reads data/C_{n}_structure.json (no dependency on the generator) and checks

  1. graded antisymmetry   [X,Y} = -(-1)^{|X||Y|} [Y,X}        (all ordered pairs)
  2. super Jacobi identity [X,[Y,Z}} = [[X,Y},Z} + (-1)^{|X||Y|}[Y,[X,Z}}   (all triples)
  3. parity consistency    |[X,Y}| = |X| + |Y| mod 2, Z in basis
  4. dimension bookkeeping

Usage: python3 src/verify_C_structure.py [n ...]   (default 1 2 3)
Exit status 0 iff all checks pass.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from itertools import product

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def load_table(path):
    with open(path) as f:
        d = json.load(f)
    basis = d["basis"]["even"] + d["basis"]["odd"]
    par = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return d, basis, par, table


def vec_add(u, v, scale=Fraction(1)):
    r = dict(u)
    for k, c in v.items():
        r[k] = r.get(k, Fraction(0)) + scale * c
    return {k: c for k, c in r.items() if c != 0}


def bracket_vec(table, X, v):
    """[X, v} for v = sum_Z c_Z Z (basis element X)."""
    r = {}
    for Z, c in v.items():
        r = vec_add(r, table.get((X, Z), {}), c)
    return r


def bracket_vec_right(table, v, Z):
    """[v, Z} for v = sum_Y c_Y Y."""
    r = {}
    for Y, c in v.items():
        r = vec_add(r, table.get((Y, Z), {}), c)
    return r


def verify(n, verbose=True):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    d, basis, par, table = load_table(path)
    report = {"n": n, "file": os.path.relpath(path, ROOT), "dim": len(basis)}
    failures = []

    # dimension bookkeeping
    dim = d["algebra"]["dimension"]
    if not (dim["even"] == 2 * n * n + n + 1 == len(d["basis"]["even"])
            and dim["odd"] == 4 * n == len(d["basis"]["odd"])
            and dim["total"] == len(basis)):
        failures.append(("dimension", dim))

    # parity consistency and Z in basis
    bset = set(basis)
    for (X, Y), v in table.items():
        for Z in v:
            if Z not in bset:
                failures.append(("Z not in basis", X, Y, Z))
            elif (par[X] + par[Y]) % 2 != par[Z]:
                failures.append(("parity", X, Y, Z))

    # antisymmetry
    n_pairs = 0
    for X, Y in product(basis, repeat=2):
        n_pairs += 1
        sign = -1 if (par[X] and par[Y]) else 1
        lhs = table.get((X, Y), {})
        rhs = {Z: -sign * c for Z, c in table.get((Y, X), {}).items()}
        if lhs != rhs:
            failures.append(("antisymmetry", X, Y, lhs, rhs))
    report["pairs_checked"] = n_pairs

    # super Jacobi: [X,[Y,Z}} - [[X,Y},Z} - (-1)^{|X||Y|}[Y,[X,Z}} = 0
    n_triples = 0
    n_nontrivial = 0
    for X, Y, Z in product(basis, repeat=3):
        n_triples += 1
        t1 = bracket_vec(table, X, table.get((Y, Z), {}))
        t2 = bracket_vec_right(table, table.get((X, Y), {}), Z)
        t3 = bracket_vec(table, Y, table.get((X, Z), {}))
        s = -1 if (par[X] and par[Y]) else 1
        res = vec_add(vec_add(t1, t2, Fraction(-1)), t3, Fraction(-s))
        if t1 or t2 or t3:
            n_nontrivial += 1
        if res:
            failures.append(("jacobi", X, Y, Z, res))
    report["triples_checked"] = n_triples
    report["triples_with_nonzero_terms"] = n_nontrivial
    report["failures"] = failures
    report["status"] = "PASS" if not failures else "FAIL"
    if verbose:
        print(f"C({n+1}) n={n}  file={report['file']}  dim={report['dim']}")
        print(f"  antisymmetry : {n_pairs} ordered pairs checked")
        print(f"  super Jacobi : {n_triples} triples checked "
              f"({n_nontrivial} with at least one nonzero term)")
        print(f"  parity/basis : {len(table)} nonzero brackets checked")
        print(f"  result       : {report['status']}"
              + (f"  ({len(failures)} failures)" if failures else ""))
        for f in failures[:20]:
            print("   ", f)
    return report


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        ok &= verify(n)["status"] == "PASS"
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)

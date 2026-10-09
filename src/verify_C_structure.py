"""Verify Schema 1 data for C(n+1): graded antisymmetry and super Jacobi identity (Issue I04).

Works purely from the JSON structure constants (independent of the oscillator realization).

Checks, for the bracket table c(X,Y) = {Z: coeff}:
  * parity:        every stored Z has p(Z) = p(X) + p(Y) mod 2
  * antisymmetry:  [Y,X} = -(-1)^{p(X)p(Y)} [X,Y}            for all ordered pairs
  * super Jacobi:  [X,[Y,Z}} = [[X,Y},Z} + (-1)^{p(X)p(Y)} [Y,[X,Z}}   for all triples

Usage: python3 src/verify_C_structure.py [--datadir data] [n ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction


def load_table(path: str):
    with open(path) as fh:
        d = json.load(fh)
    order = d["basis"]["pbw_order"]
    par = d["parity"]
    table = {(X, Y): {} for X in order for Y in order}
    for e in d["structure_constants"]:
        c = Fraction(e["coeff"])
        if c == 0:
            raise ValueError(f"zero coefficient stored for ({e['X']},{e['Y']},{e['Z']})")
        if e["Z"] in table[(e["X"], e["Y"])]:
            raise ValueError(f"duplicate entry ({e['X']},{e['Y']},{e['Z']})")
        table[(e["X"], e["Y"])][e["Z"]] = c
    return d, order, par, table


def ad(table, X, vec: dict) -> dict:
    """[X, vec} for vec = {label: coeff}."""
    out: dict = {}
    for Y, cy in vec.items():
        for Z, cz in table[(X, Y)].items():
            out[Z] = out.get(Z, Fraction(0)) + cy * cz
    return {k: v for k, v in out.items() if v != 0}


def verify(path: str, verbose=True) -> dict:
    d, order, par, table = load_table(path)
    report = {"file": os.path.basename(path), "dim": len(order), "pairs": len(order) ** 2,
              "triples": len(order) ** 3, "parity_failures": [], "antisymmetry_failures": [],
              "jacobi_failures": [], "nonzero_pairs": sum(1 for v in table.values() if v)}
    for (X, Y), c in table.items():
        for Z in c:
            if (par[X] + par[Y]) % 2 != par[Z]:
                report["parity_failures"].append((X, Y, Z))
        sign = -1 if (par[X] and par[Y]) else 1
        expected = {Z: -sign * v for Z, v in c.items()}
        if expected != table[(Y, X)]:
            report["antisymmetry_failures"].append((X, Y))
    for X in order:
        for Y in order:
            sXY = -1 if (par[X] and par[Y]) else 1
            for Z in order:
                lhs = ad(table, X, table[(Y, Z)])
                rhs: dict = {}
                # [[X,Y},Z}
                for W, cw in table[(X, Y)].items():
                    for V, cv in table[(W, Z)].items():
                        rhs[V] = rhs.get(V, Fraction(0)) + cw * cv
                # (-1)^{p(X)p(Y)} [Y,[X,Z}}
                for V, cv in ad(table, Y, table[(X, Z)]).items():
                    rhs[V] = rhs.get(V, Fraction(0)) + sXY * cv
                rhs = {k: v for k, v in rhs.items() if v != 0}
                if lhs != rhs:
                    report["jacobi_failures"].append((X, Y, Z, lhs, rhs))
    report["pass"] = not (report["parity_failures"] or report["antisymmetry_failures"] or report["jacobi_failures"])
    if verbose:
        print(f"{report['file']}: dim {report['dim']}, {report['pairs']} ordered pairs "
              f"({report['nonzero_pairs']} non-zero), {report['triples']} triples")
        print(f"  parity       : {'PASS' if not report['parity_failures'] else 'FAIL (%d)' % len(report['parity_failures'])}")
        print(f"  antisymmetry : {'PASS' if not report['antisymmetry_failures'] else 'FAIL (%d)' % len(report['antisymmetry_failures'])}")
        print(f"  super Jacobi : {'PASS' if not report['jacobi_failures'] else 'FAIL (%d)' % len(report['jacobi_failures'])}")
        for X, Y, Z, lhs, rhs in report["jacobi_failures"][:10]:
            print(f"    Jacobi fails for ({X},{Y},{Z}): lhs={lhs} rhs={rhs}")
        print(f"  overall      : {'PASS' if report['pass'] else 'FAIL'}")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ns", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    args = ap.parse_args(argv)
    ok = True
    for n in args.ns:
        rep = verify(os.path.join(args.datadir, f"C_{n}_structure.json"))
        ok = ok and rep["pass"]
    print("SUMMARY:", "all checks passed" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

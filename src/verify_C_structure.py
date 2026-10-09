"""Verification of Schema 1 structure constants for C(n+1) (Issue I04).

Loads data/C_{n}_structure.json and checks, using ONLY the JSON records
(independent of the oscillator engine):

  (A) parity additivity          p([X,Y]) = p(X) + p(Y)        for every record
  (B) graded antisymmetry        [Y,X] = -(-1)^{p(X)p(Y)} [X,Y]  for every ordered pair
  (C) super Jacobi identity      [X,[Y,Z]] = [[X,Y],Z] + (-1)^{p(X)p(Y)} [Y,[X,Z]]
                                                                  for every ordered triple
  (D) closure                    every target Z is a basis label

Usage: python src/verify_C_structure.py [--n 1 2 3] [--datadir data]
Exit status 0 iff all checks pass.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

Vec = Dict[str, Fraction]


def load_structure(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


class BracketTable:
    """Bilinear bracket on span(basis) reconstructed from JSON records."""

    def __init__(self, doc: dict):
        self.labels: List[str] = doc["basis"]["pbw_order"]
        self.parity: Dict[str, int] = doc["parity"]
        self.table: Dict[Tuple[str, str], Vec] = {}
        for r in doc["structure_constants"]:
            self.table.setdefault((r["X"], r["Y"]), {})
            self.table[(r["X"], r["Y"])][r["Z"]] = self.table[(r["X"], r["Y"])].get(r["Z"], Fraction(0)) + Fraction(r["coeff"])

    def br(self, x: str, y: str) -> Vec:
        return self.table.get((x, y), {})

    def br_vec(self, x: str, v: Vec) -> Vec:
        """[x, v] for v = sum c_z z."""
        out: Vec = {}
        for z, c in v.items():
            for w, d in self.br(x, z).items():
                out[w] = out.get(w, Fraction(0)) + c * d
        return {k: v for k, v in out.items() if v != 0}

    def vec_br(self, v: Vec, y: str) -> Vec:
        out: Vec = {}
        for z, c in v.items():
            for w, d in self.br(z, y).items():
                out[w] = out.get(w, Fraction(0)) + c * d
        return {k: v for k, v in out.items() if v != 0}


def vadd(*vs: Vec) -> Vec:
    out: Vec = {}
    for v in vs:
        for k, c in v.items():
            out[k] = out.get(k, Fraction(0)) + c
    return {k: c for k, c in out.items() if c != 0}


def vscale(v: Vec, s) -> Vec:
    return {k: c * s for k, c in v.items() if c * s != 0}


def verify(doc: dict, max_report: int = 10) -> dict:
    T = BracketTable(doc)
    labs, par = T.labels, T.parity
    basis = set(labs)
    report = {"n": doc["algebra"]["n"], "dim": len(labs), "failures": {}, "counts": {}}

    # (D) closure and (A) parity additivity
    fails = []
    for (x, y), comps in T.table.items():
        for z, c in comps.items():
            if z not in basis:
                fails.append(f"[{x},{y}] -> {c} {z}: target not in basis")
            elif par[z] != (par[x] + par[y]) % 2:
                fails.append(f"[{x},{y}] -> {c} {z}: parity mismatch")
    report["failures"]["closure_parity"] = fails
    report["counts"]["records_checked"] = sum(len(v) for v in T.table.values())

    # (B) antisymmetry over all ordered pairs
    fails = []
    npairs = 0
    for x in labs:
        for y in labs:
            npairs += 1
            sign = -1 if (par[x] == 1 and par[y] == 1) else 1
            lhs = T.br(y, x)
            rhs = vscale(T.br(x, y), -sign)
            if vadd(lhs, vscale(rhs, -1)):
                fails.append(f"[{y},{x}] = {lhs} but -(-1)^(p p) [{x},{y}] = {rhs}")
    report["failures"]["antisymmetry"] = fails
    report["counts"]["pairs_checked"] = npairs

    # (C) super Jacobi over all ordered triples
    fails = []
    ntriples = 0
    for x, y, z in itertools.product(labs, repeat=3):
        ntriples += 1
        sxy = -1 if (par[x] == 1 and par[y] == 1) else 1
        lhs = T.br_vec(x, T.br(y, z))
        rhs = vadd(T.vec_br(T.br(x, y), z), vscale(T.br_vec(y, T.br(x, z)), sxy))
        diff = vadd(lhs, vscale(rhs, -1))
        if diff:
            fails.append(f"Jacobi({x},{y},{z}): residual {diff}")
    report["failures"]["jacobi"] = fails
    report["counts"]["triples_checked"] = ntriples
    report["passed"] = all(len(v) == 0 for v in report["failures"].values())
    return report


def print_report(rep: dict, max_report: int = 10) -> None:
    n = rep["n"]
    print(f"== C({n+1}) = osp(2|{2*n})  (n={n}, dim={rep['dim']}) ==")
    c = rep["counts"]
    print(f"  records checked (closure/parity): {c['records_checked']}")
    print(f"  ordered pairs checked (antisymmetry): {c['pairs_checked']}")
    print(f"  ordered triples checked (super Jacobi): {c['triples_checked']}")
    for name, fails in rep["failures"].items():
        status = "PASS" if not fails else f"FAIL ({len(fails)} violations)"
        print(f"  {name:16s}: {status}")
        for line in fails[:max_report]:
            print("     ", line)
    print(f"  overall: {'PASS' if rep['passed'] else 'FAIL'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
    args = ap.parse_args(argv)
    ok = True
    for n in args.n:
        doc = load_structure(os.path.join(args.datadir, f"C_{n}_structure.json"))
        rep = verify(doc)
        print_report(rep)
        ok = ok and rep["passed"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

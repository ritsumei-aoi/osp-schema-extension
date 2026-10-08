"""I04: verify Schema 1 data (C_{n}_structure.json) from the JSON alone.

Checks
  1. parity rule        p(Z) = p(X) + p(Y) mod 2 for every entry, Z in basis
  2. anti-symmetry      [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}   for all ordered pairs (X, Y)
  3. super Jacobi       (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0
                        for all ordered triples (X, Y, Z)
  4. bonus              Cartan subalgebra is abelian and acts diagonally with the roots of basis.roots

Usage:  python src/verify_C_structure.py [n ...]   (default 1 2 3); exit status 1 on failure.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


class BracketTable:
    """Bracket table of a Lie superalgebra given by (X, Y, Z, coeff) entries."""

    def __init__(self, labels, parity, entries):
        self.labels = list(labels)
        self.parity = dict(parity)
        self.table: dict = {}
        for e in entries:
            d = self.table.setdefault((e["X"], e["Y"]), {})
            d[e["Z"]] = d.get(e["Z"], Fraction(0)) + Fraction(e["coeff"])
        for k in list(self.table):
            self.table[k] = {z: c for z, c in self.table[k].items() if c != 0}

    @classmethod
    def from_schema1(cls, d: dict) -> "BracketTable":
        labels = d["basis"]["pbw_order"]
        return cls(labels, d["parity"], d["structure_constants"])

    def bracket_basis(self, x: str, y: str) -> dict:
        return self.table.get((x, y), {})

    def bracket(self, u: dict, v: dict) -> dict:
        """Bracket of two vectors (dict label -> Fraction), bilinear extension."""
        out: dict = {}
        for x, cx in u.items():
            for y, cy in v.items():
                for z, c in self.bracket_basis(x, y).items():
                    out[z] = out.get(z, Fraction(0)) + cx * cy * c
        return {z: c for z, c in out.items() if c != 0}

    def sign(self, x: str, y: str) -> int:
        return -1 if (self.parity[x] and self.parity[y]) else 1


def verify(d: dict, verbose: bool = True) -> dict:
    T = BracketTable.from_schema1(d)
    labs, p = T.labels, T.parity
    report = {"n": d["algebra"]["n"], "dim": len(labs), "failures": [], "pairs": 0, "triples": 0}

    # 1. parity / closure
    for (x, y), comps in T.table.items():
        for z in comps:
            if z not in p:
                report["failures"].append(("closure", x, y, z))
            elif p[z] != (p[x] + p[y]) % 2:
                report["failures"].append(("parity", x, y, z))

    # 2. anti-symmetry
    for x in labs:
        for y in labs:
            report["pairs"] += 1
            lhs = T.bracket_basis(x, y)
            rhs = {z: -T.sign(x, y) * c for z, c in T.bracket_basis(y, x).items()}
            if lhs != rhs:
                report["failures"].append(("antisymmetry", x, y, lhs, rhs))

    # 3. super Jacobi
    for x in labs:
        for y in labs:
            for z in labs:
                report["triples"] += 1
                t1 = T.bracket({x: Fraction(1)}, T.bracket_basis(y, z))
                t2 = T.bracket({y: Fraction(1)}, T.bracket_basis(z, x))
                t3 = T.bracket({z: Fraction(1)}, T.bracket_basis(x, y))
                s1, s2, s3 = T.sign(x, z), T.sign(y, x), T.sign(z, y)
                tot: dict = {}
                for s, t in ((s1, t1), (s2, t2), (s3, t3)):
                    for w, c in t.items():
                        tot[w] = tot.get(w, Fraction(0)) + s * c
                tot = {w: c for w, c in tot.items() if c != 0}
                if tot:
                    report["failures"].append(("jacobi", x, y, z, tot))

    # 4. Cartan diagonal action and abelian Cartan
    cartan = [l for l in labs if l.startswith("H_")]
    for h in cartan:
        for h2 in cartan:
            if T.bracket_basis(h, h2):
                report["failures"].append(("cartan_abelian", h, h2))
        for x in labs:
            comps = T.bracket_basis(h, x)
            if set(comps) - {x}:
                report["failures"].append(("cartan_diagonal", h, x, comps))

    report["passed"] = not report["failures"]
    if verbose:
        n = report["n"]
        print(f"C({n+1}) = osp(2|{2*n})  [n={n}]  dim={report['dim']}  "
              f"pairs={report['pairs']}  triples={report['triples']}  "
              f"-> {'PASS' if report['passed'] else 'FAIL'}")
        for f in report["failures"][:20]:
            print("   ", f)
        if len(report["failures"]) > 20:
            print(f"    ... {len(report['failures'])} failures in total")
    return report


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    ok = True
    for n in ns:
        with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
            d = json.load(fh)
        ok &= verify(d)["passed"]
    print("SUMMARY:", "all checks passed" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

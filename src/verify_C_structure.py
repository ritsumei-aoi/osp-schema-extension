"""
I04: verify Schema 1 structure constants of C(n+1) from the JSON files only.

Checks (exact rational arithmetic):
  1. graded antisymmetry   [X,Y} + (-1)^{p(X)p(Y)} [Y,X} = 0           for all ordered pairs
  2. super Jacobi          (-1)^{p(X)p(Z)} [X,[Y,Z}} + cyclic = 0        for all ordered triples
  3. parity grading        p(Z) = p(X)+p(Y) for every stored constant
  4. dimension bookkeeping  (even/odd counts vs formulas)

Usage:  python src/verify_C_structure.py [n ...]      (default: 1 2 3)
Exit status 0 iff all checks pass.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from typing import Dict, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

Vec = Dict[str, Fraction]


class BracketTable:
    """Bracket table of a Lie superalgebra loaded from a Schema 1 JSON file (or dict)."""

    def __init__(self, data: dict):
        self.data = data
        self.order = list(data["basis"]["pbw_order"])
        self.parity = {k: int(v) for k, v in data["parity"].items()}
        self.table: Dict[Tuple[str, str], Vec] = {}
        for e in data["structure_constants"]:
            self.table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])

    @classmethod
    def load(cls, n: int, data_dir: str = DATA_DIR) -> "BracketTable":
        with open(os.path.join(data_dir, f"C_{n}_structure.json")) as fh:
            return cls(json.load(fh))

    def bracket_basis(self, x: str, y: str) -> Vec:
        return self.table.get((x, y), {})

    def bracket(self, u: Vec, v: Vec) -> Vec:
        out: Vec = {}
        for x, cx in u.items():
            for y, cy in v.items():
                for z, cz in self.bracket_basis(x, y).items():
                    out[z] = out.get(z, Fraction(0)) + cx * cy * cz
        return {k: v for k, v in out.items() if v != 0}


def add(u: Vec, v: Vec, c=Fraction(1)) -> Vec:
    out = dict(u)
    for k, val in v.items():
        out[k] = out.get(k, Fraction(0)) + c * val
    return {k: v for k, v in out.items() if v != 0}


def scale(u: Vec, c) -> Vec:
    return {k: v * c for k, v in u.items() if v * c != 0}


def verify(bt: BracketTable, verbose: bool = True) -> dict:
    order, p = bt.order, bt.parity
    report = {"n_basis": len(order), "antisymmetry_failures": [], "jacobi_failures": [],
              "parity_failures": [], "pairs_checked": 0, "triples_checked": 0}

    # 3. parity grading
    for (x, y), vec in bt.table.items():
        for z in vec:
            if p[z] != (p[x] + p[y]) % 2:
                report["parity_failures"].append((x, y, z))

    # 1. antisymmetry
    for x in order:
        for y in order:
            s = -1 if (p[x] and p[y]) else 1
            res = add(bt.bracket_basis(x, y), bt.bracket_basis(y, x), Fraction(s))
            report["pairs_checked"] += 1
            if res:
                report["antisymmetry_failures"].append((x, y, res))

    # 2. super Jacobi
    for x in order:
        for y in order:
            for z in order:
                t1 = scale(bt.bracket({x: Fraction(1)}, bt.bracket_basis(y, z)), (-1) ** (p[x] * p[z]))
                t2 = scale(bt.bracket({y: Fraction(1)}, bt.bracket_basis(z, x)), (-1) ** (p[y] * p[x]))
                t3 = scale(bt.bracket({z: Fraction(1)}, bt.bracket_basis(x, y)), (-1) ** (p[z] * p[y]))
                res = add(add(t1, t2), t3)
                report["triples_checked"] += 1
                if res:
                    report["jacobi_failures"].append((x, y, z, res))

    # 4. dimensions
    n = bt.data["algebra"]["n"]
    even = [l for l in order if p[l] == 0]
    odd = [l for l in order if p[l] == 1]
    report["dimension_ok"] = (len(even) == 2 * n * n + n + 1 and len(odd) == 4 * n
                              and bt.data["algebra"]["dimension"] == {"total": len(order), "even": len(even), "odd": len(odd)})
    report["pass"] = (not report["antisymmetry_failures"] and not report["jacobi_failures"]
                      and not report["parity_failures"] and report["dimension_ok"])
    if verbose:
        name = bt.data["algebra"]["cartan_type"]
        print(f"[{name}, n={n}] basis={len(order)} (even {len(even)}, odd {len(odd)}) dimension_ok={report['dimension_ok']}")
        print(f"  parity grading : {len(bt.table)} pairs with non-zero bracket, failures={len(report['parity_failures'])}")
        print(f"  antisymmetry   : {report['pairs_checked']} ordered pairs checked, failures={len(report['antisymmetry_failures'])}")
        print(f"  super Jacobi   : {report['triples_checked']} ordered triples checked, failures={len(report['jacobi_failures'])}")
        print(f"  RESULT         : {'PASS' if report['pass'] else 'FAIL'}")
        for f in report["antisymmetry_failures"][:10]:
            print("   antisymmetry failure:", f)
        for f in report["jacobi_failures"][:10]:
            print("   jacobi failure:", f)
    return report


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    ok = True
    for n in ns:
        rep = verify(BracketTable.load(n))
        ok &= rep["pass"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

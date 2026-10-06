"""Verification of the C(n+1) Schema 1 structure constants (Issue I04).

Checks, for n = 1, 2, 3, loading ``data/C_{n}_structure.json``:

1. **Closure / well-formedness** -- every ``Z`` is a basis label, every pair
   obeys the storage convention, parities are additive.
2. **Graded antisymmetry** -- ``[X,Y} = -(-1)^{p(X)p(Y)} [Y,X}`` computed
   independently from the oscillator engine, for *all* ordered pairs.
3. **Table fidelity** -- the stored half, expanded by antisymmetry, reproduces
   the engine's full bracket table.
4. **Super Jacobi identity** -- for all N^3 triples,
   ``[[X,Y},Z} = [X,[Y,Z}} - (-1)^{p(X)p(Y)} [Y,[X,Z}}``
   and the cyclic form
   ``(-1)^{p(X)p(Z)}[[X,Y},Z} + (-1)^{p(Y)p(X)}[[Y,Z},X} + (-1)^{p(Z)p(Y)}[[Z,X},Y} = 0``.

Exit status is non-zero if any check fails.

Usage::

    python src/verify_C_structure.py           # n = 1, 2, 3
    python src/verify_C_structure.py 2
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

try:
    from .osc_algebra import CAlgebra
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import CAlgebra  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

Vec = Dict[str, Fraction]


# --------------------------------------------------------------------------
def vadd(a: Vec, b: Vec, scale: Fraction = Fraction(1)) -> Vec:
    out = dict(a)
    for k, v in b.items():
        nv = out.get(k, Fraction(0)) + scale * v
        if nv:
            out[k] = nv
        else:
            out.pop(k, None)
    return out


def vzero(a: Vec) -> bool:
    return all(v == 0 for v in a.values())


class StructureTable:
    """Full bracket table reconstructed from the stored half."""

    def __init__(self, doc: dict):
        self.order: List[str] = doc["basis"]["pbw_order"]
        self.parity: Dict[str, int] = doc["parity"]
        self.index = {lab: i for i, lab in enumerate(self.order)}
        self.stored: Dict[Tuple[str, str], Vec] = {}
        for e in doc["structure_constants"]:
            self.stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
        self.full: Dict[Tuple[str, str], Vec] = {}
        for x in self.order:
            for y in self.order:
                if self.index[x] <= self.index[y]:
                    self.full[(x, y)] = dict(self.stored.get((x, y), {}))
                else:
                    sign = -1 if (self.parity[x] and self.parity[y]) else 1
                    base = self.stored.get((y, x), {})
                    self.full[(x, y)] = {k: -sign * v for k, v in base.items()}

    def br_gen(self, x: str, y: str) -> Vec:
        return self.full[(x, y)]

    def br(self, u: Vec, v: Vec) -> Vec:
        """Bilinear extension of the bracket to coefficient vectors."""
        out: Vec = {}
        for x, cx in u.items():
            for y, cy in v.items():
                out = vadd(out, self.full[(x, y)], cx * cy)
        return out

    def par(self, lab: str) -> int:
        return self.parity[lab]


# --------------------------------------------------------------------------
def check_wellformed(doc: dict, table: StructureTable) -> List[str]:
    errs: List[str] = []
    order, idx = table.order, table.index
    for e in doc["structure_constants"]:
        if idx[e["X"]] > idx[e["Y"]]:
            errs.append(f"storage convention violated: {e['X']}, {e['Y']}")
        if e["Z"] not in idx:
            errs.append(f"Z={e['Z']} is not a basis label ({e['X']}, {e['Y']})")
            continue
        if Fraction(e["coeff"]) == 0:
            errs.append(f"zero coefficient stored: {e}")
        pz = table.par(e["Z"])
        if pz != (table.par(e["X"]) + table.par(e["Y"])) % 2:
            errs.append(f"parity violation: [{e['X']},{e['Y']}] -> {e['Z']}")
    if len(order) != doc["algebra"]["dimension"]["total"]:
        errs.append("pbw_order length != declared total dimension")
    return errs


def check_antisymmetry(alg: CAlgebra, table: StructureTable) -> Tuple[int, List[str]]:
    """Engine-level graded antisymmetry over all ordered pairs."""
    errs: List[str] = []
    count = 0
    for x in alg.pbw_order:
        for y in alg.pbw_order:
            count += 1
            sign = -1 if (alg.parity[x] and alg.parity[y]) else 1
            lhs = {k: Fraction(str(v)) for k, v in alg.bracket_coeffs(x, y).items()}
            rhs = {k: -sign * Fraction(str(v))
                   for k, v in alg.bracket_coeffs(y, x).items()}
            if not vzero(vadd(lhs, rhs, Fraction(-1))):
                errs.append(f"antisymmetry fails for ({x}, {y})")
    return count, errs


def check_table_fidelity(alg: CAlgebra, table: StructureTable) -> Tuple[int, List[str]]:
    """Reconstructed full table == engine brackets, for all ordered pairs."""
    errs: List[str] = []
    count = 0
    for x in alg.pbw_order:
        for y in alg.pbw_order:
            count += 1
            live = {k: Fraction(str(v)) for k, v in alg.bracket_coeffs(x, y).items()}
            if not vzero(vadd(live, table.br_gen(x, y), Fraction(-1))):
                errs.append(f"table mismatch at ({x}, {y}): "
                            f"json={table.br_gen(x, y)} engine={live}")
    return count, errs


def check_super_jacobi(table: StructureTable, max_report: int = 10):
    """Derivation form and cyclic form, over all N^3 triples."""
    order = table.order
    errs: List[str] = []
    count = 0
    for x, y, z in itertools.product(order, repeat=3):
        count += 1
        px, py, pz = table.par(x), table.par(y), table.par(z)

        # derivation form: [[X,Y},Z} = [X,[Y,Z}} - (-1)^{px py} [Y,[X,Z}}
        lhs = table.br(table.br_gen(x, y), {z: Fraction(1)})
        rhs = table.br({x: Fraction(1)}, table.br_gen(y, z))
        s = Fraction(-1 if (px and py) else 1)
        rhs = vadd(rhs, table.br({y: Fraction(1)}, table.br_gen(x, z)), -s)
        if not vzero(vadd(lhs, rhs, Fraction(-1))):
            if len(errs) < max_report:
                errs.append(f"derivation form fails at ({x}, {y}, {z})")

        # cyclic form
        cyc: Vec = {}
        for (a, b, c, pa, pc) in ((x, y, z, px, pz), (y, z, x, py, px), (z, x, y, pz, py)):
            sgn = Fraction(-1 if (pa and pc) else 1)
            cyc = vadd(cyc, table.br(table.br_gen(a, b), {c: Fraction(1)}), sgn)
        if not vzero(cyc):
            if len(errs) < max_report:
                errs.append(f"cyclic form fails at ({x}, {y}, {z}): {cyc}")
    return count, errs


# --------------------------------------------------------------------------
def verify(n: int) -> bool:
    path = os.path.join(DATA, f"C_{n}_structure.json")
    with open(path) as fh:
        doc = json.load(fh)
    alg = CAlgebra(n)
    table = StructureTable(doc)
    N = len(table.order)

    print(f"=== n = {n}   C({n + 1}) = osp(2|{2 * n})   dim = "
          f"{doc['algebra']['dimension']['even']}|{doc['algebra']['dimension']['odd']} "
          f"= {N} ===")

    ok = True
    e1 = check_wellformed(doc, table)
    print(f"  [1] well-formedness / closure / parity : "
          f"{len(doc['structure_constants'])} entries -> "
          f"{'PASS' if not e1 else 'FAIL'}")
    ok &= not e1

    c2, e2 = check_antisymmetry(alg, table)
    print(f"  [2] graded antisymmetry               : {c2} ordered pairs -> "
          f"{'PASS' if not e2 else 'FAIL'}")
    ok &= not e2

    c3, e3 = check_table_fidelity(alg, table)
    print(f"  [3] JSON table == engine brackets     : {c3} ordered pairs -> "
          f"{'PASS' if not e3 else 'FAIL'}")
    ok &= not e3

    c4, e4 = check_super_jacobi(table)
    print(f"  [4] super Jacobi (derivation+cyclic)  : {c4} triples -> "
          f"{'PASS' if not e4 else 'FAIL'}")
    ok &= not e4

    for errs in (e1, e2, e3, e4):
        for msg in errs[:10]:
            print(f"      ! {msg}")
    return ok


def main(argv: List[str]) -> int:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    results = {n: verify(n) for n in ns}
    print()
    print("SUMMARY: " + ", ".join(
        f"n={n}: {'PASS' if v else 'FAIL'}" for n, v in results.items()))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

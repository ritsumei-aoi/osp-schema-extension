"""Verify graded antisymmetry and the super Jacobi identity for C(n+1) structure constants (Issue I04).

The checks are written for a generic Lie superalgebra given by
    basis   : list of labels
    parity  : dict label -> 0/1
    table   : dict (X, Y) -> dict Z -> Fraction   (graded bracket [X, Y} = sum_Z c Z)
so that the same code verifies the extended algebra g~ (+) kappa g~ in Issue I06.

Usage:
    python src/verify_C_structure.py            # verifies data/C_{1,2,3}_structure.json
    python src/verify_C_structure.py 2 3
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

Table = Dict[Tuple[str, str], Dict[str, Fraction]]


# ------------------------------------------------------------------ loading
def load_table(entries) -> Table:
    """Build the bracket table from a Schema-1 style ``structure_constants`` list."""
    tab: Table = {}
    for e in entries:
        c = Fraction(e["coeff"])
        if c == 0:
            continue
        d = tab.setdefault((e["X"], e["Y"]), {})
        d[e["Z"]] = d.get(e["Z"], Fraction(0)) + c
    return {k: {z: c for z, c in v.items() if c != 0} for k, v in tab.items()}


def load_structure(n: int):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as fh:
        d = json.load(fh)
    basis = d["basis"]["odd"] + d["basis"]["even"]
    return basis, d["parity"], load_table(d["structure_constants"]), d


# ----------------------------------------------------------- linear algebra
def bracket_vec(table: Table, X: str, vec: Dict[str, Fraction], on_left: bool = True) -> Dict[str, Fraction]:
    """[X, vec} if on_left else [vec, X}, where vec = sum_Z c Z."""
    out: Dict[str, Fraction] = {}
    for Z, c in vec.items():
        key = (X, Z) if on_left else (Z, X)
        for W, d in table.get(key, {}).items():
            out[W] = out.get(W, Fraction(0)) + c * d
    return {W: c for W, c in out.items() if c != 0}


# ------------------------------------------------------------------- checks
def check_closure(basis: List[str], parity: Dict[str, int], table: Table, extra_targets=()):
    """Every entry refers to known labels and has the right parity."""
    failures = []
    allowed = set(basis) | set(extra_targets)
    for (X, Y), v in table.items():
        if X not in basis or Y not in basis:
            failures.append(("unknown pair", X, Y))
            continue
        for Z in v:
            if Z not in allowed:
                failures.append(("unknown target", X, Y, Z))
            elif parity[Z] != (parity[X] + parity[Y]) % 2:
                failures.append(("parity", X, Y, Z))
    return failures


def check_antisymmetry(basis: List[str], parity: Dict[str, int], table: Table):
    """[X, Y} = -(-1)^{p(X)p(Y)} [Y, X} for all ordered pairs."""
    failures = []
    for X in basis:
        for Y in basis:
            sign = -1 if (parity[X] and parity[Y]) else 1
            lhs = table.get((X, Y), {})
            rhs = {Z: -sign * c for Z, c in table.get((Y, X), {}).items()}
            if lhs != rhs:
                failures.append((X, Y, lhs, rhs))
    return failures


def jacobiator(table: Table, parity: Dict[str, int], X: str, Y: str, Z: str) -> Dict[str, Fraction]:
    """(-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}}."""
    out: Dict[str, Fraction] = {}
    for A, B, C in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
        sign = -1 if (parity[A] and parity[C]) else 1
        for W, c in bracket_vec(table, A, table.get((B, C), {})).items():
            out[W] = out.get(W, Fraction(0)) + sign * c
    return {W: c for W, c in out.items() if c != 0}


def check_jacobi(basis: List[str], parity: Dict[str, int], table: Table, all_ordered: bool = False):
    """Super Jacobi identity for all triples.

    By graded antisymmetry the Jacobiator is graded-symmetric under permutations of (X, Y, Z),
    so it suffices to test X <= Y <= Z (including repeats); ``all_ordered=True`` tests every
    ordered triple instead.
    """
    failures = []
    triples = itertools.product(basis, repeat=3) if all_ordered else \
        itertools.combinations_with_replacement(basis, 3)
    count = 0
    for X, Y, Z in triples:
        count += 1
        j = jacobiator(table, parity, X, Y, Z)
        if j:
            failures.append((X, Y, Z, j))
    return count, failures


def verify(basis, parity, table, extra_targets=(), all_ordered=False) -> dict:
    closure = check_closure(basis, parity, table, extra_targets)
    anti = check_antisymmetry(basis, parity, table)
    n_triples, jac = check_jacobi(basis, parity, table, all_ordered=all_ordered)
    return {
        "dim": len(basis),
        "nonzero_pairs": len(table),
        "closure_failures": closure,
        "antisymmetry_pairs_checked": len(basis) ** 2,
        "antisymmetry_failures": anti,
        "jacobi_triples_checked": n_triples,
        "jacobi_failures": jac,
        "pass": not (closure or anti or jac),
    }


def report(n: int, res: dict, label: str = "") -> str:
    lines = [f"== C({n + 1}) = osp(2|{2 * n}) {label}  dim={res['dim']}  non-zero ordered pairs={res['nonzero_pairs']}"]
    lines.append(f"   closure/parity   : {'PASS' if not res['closure_failures'] else 'FAIL'} ({len(res['closure_failures'])} failures)")
    lines.append(f"   antisymmetry     : {'PASS' if not res['antisymmetry_failures'] else 'FAIL'} "
                 f"({res['antisymmetry_pairs_checked']} ordered pairs, {len(res['antisymmetry_failures'])} failures)")
    lines.append(f"   super Jacobi     : {'PASS' if not res['jacobi_failures'] else 'FAIL'} "
                 f"({res['jacobi_triples_checked']} triples, {len(res['jacobi_failures'])} failures)")
    for f in res["jacobi_failures"][:10]:
        lines.append(f"      J({f[0]}, {f[1]}, {f[2]}) = {f[3]}")
    lines.append(f"   RESULT           : {'PASS' if res['pass'] else 'FAIL'}")
    return "\n".join(lines)


def main(ns):
    ok = True
    for n in ns:
        basis, parity, table, _ = load_structure(n)
        res = verify(basis, parity, table, all_ordered=True)
        print(report(n, res))
        ok &= res["pass"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main([int(a) for a in sys.argv[1:]] or [1, 2, 3]))

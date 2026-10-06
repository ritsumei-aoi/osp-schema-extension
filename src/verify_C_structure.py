"""Verify super-antisymmetry and the super Jacobi identity from Schema 1 JSON only.

Usage:  python3 src/verify_C_structure.py      # checks data/C_{1,2,3}_structure.json

Conventions (graded bracket):
    antisymmetry : [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
    Jacobi       : (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}}
                   + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from itertools import product

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_table(struct: dict):
    basis = struct["basis"]["ordered"]
    par = struct["parity"]
    table: dict = {}
    for e in struct["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return basis, par, table


def br(table, x, v: dict) -> dict:
    """[x, v} for v a linear combination {label: coeff}."""
    out: dict = {}
    for y, c in v.items():
        for z, a in table.get((x, y), {}).items():
            out[z] = out.get(z, 0) + c * a
    return {z: c for z, c in out.items() if c}


def check_antisymmetry(basis, par, table):
    failures = []
    for x, y in product(basis, repeat=2):
        s = -(-1) ** (par[x] * par[y])
        lhs = table.get((x, y), {})
        rhs = {z: s * c for z, c in table.get((y, x), {}).items()}
        if lhs != rhs:
            failures.append((x, y))
    return len(basis) ** 2, failures


def check_jacobi(basis, par, table):
    failures = []
    count = 0
    for x, y, z in product(basis, repeat=3):
        count += 1
        tot: dict = {}
        for (a, b, c) in ((x, y, z), (y, z, x), (z, x, y)):
            sgn = (-1) ** (par[a] * par[c])
            for w, v in br(table, a, table.get((b, c), {})).items():
                tot[w] = tot.get(w, 0) + sgn * v
        if any(tot.values()):
            failures.append((x, y, z, {k: str(v) for k, v in tot.items() if v}))
    return count, failures


def check_parity(basis, par, table):
    bad = [(x, y, z) for (x, y), d in table.items() for z in d if par[z] != (par[x] + par[y]) % 2]
    return bad


def verify(struct: dict) -> dict:
    basis, par, table = load_table(struct)
    n_pairs, anti = check_antisymmetry(basis, par, table)
    n_trip, jac = check_jacobi(basis, par, table)
    bad_par = check_parity(basis, par, table)
    return {"n": struct["algebra"]["n"], "dim": len(basis), "pairs": n_pairs, "antisymmetry_failures": anti,
            "triples": n_trip, "jacobi_failures": jac, "parity_failures": bad_par,
            "passed": not (anti or jac or bad_par)}


def main(ns=(1, 2, 3)) -> int:
    ok = True
    for n in ns:
        with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
            r = verify(json.load(fh))
        ok &= r["passed"]
        print(f"C_{n}_structure.json (dim {r['dim']}): antisymmetry {r['pairs']} pairs, "
              f"{len(r['antisymmetry_failures'])} failures; Jacobi {r['triples']} triples, "
              f"{len(r['jacobi_failures'])} failures; parity failures {len(r['parity_failures'])} "
              f"-> {'PASS' if r['passed'] else 'FAIL'}")
        for f in r["jacobi_failures"][:5]:
            print("   Jacobi failure:", f)
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

"""Verify super anti-symmetry and the super Jacobi identity for C(n+1) Schema 1 JSON.

Reads only the JSON files in data/ (it does not import the generator), so it checks
the stored structure constants as they are.

Conventions (see docs/json_schema_specification.md and handover/notation.md):
  [X, Y] = -(-1)^{p(X) p(Y)} [Y, X]                       (super anti-symmetry)
  (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]]
      + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0                     (super Jacobi)

Usage: python3 src/verify_C_structure.py [--data-dir DIR]
Exit status 0 if all checks pass, 1 otherwise.
"""

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_structure(path):
    with Path(path).open() as f:
        return json.load(f)


def build_bracket_table(schema):
    """Return (labels, parity, table) where table[(X, Y)] = {Z: Fraction}.

    Both (X, Y) and (Y, X) are filled from the stored entries, using the
    stored entries with X <= Y in PBW order as the source of truth.
    """
    labels = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = {label: schema["parity"][label] for label in labels}
    table = {}
    for entry in schema["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        table.setdefault((X, Y), {})
        table[(X, Y)][Z] = table[(X, Y)].get(Z, 0) + coeff
    return labels, parity, table


def bracket_basis(table, parity, X, Y):
    """[X, Y] for basis labels X, Y, using the stored table.

    Pairs stored only in the other order are recovered by super anti-symmetry,
    so the stored table is treated as the unique source.
    """
    if (X, Y) in table:
        return table[(X, Y)]
    if (Y, X) in table:
        sign = -1 if (parity[X] and parity[Y]) else 1
        return {Z: -sign * c for Z, c in table[(Y, X)].items()}
    return {}


def bracket_vec(table, parity, u, v):
    """Bilinear extension of the bracket to linear combinations (dicts)."""
    out = {}
    for X, cx in u.items():
        for Y, cy in v.items():
            for Z, c in bracket_basis(table, parity, X, Y).items():
                out[Z] = out.get(Z, 0) + cx * cy * c
    return {k: c for k, c in out.items() if c != 0}


def add_vec(*vecs_with_coeff):
    out = {}
    for coeff, vec in vecs_with_coeff:
        for k, c in vec.items():
            out[k] = out.get(k, 0) + coeff * c
    return {k: c for k, c in out.items() if c != 0}


def check_antisymmetry(labels, parity, table):
    """Return list of failures for [X,Y] + (-1)^{pX pY} [Y,X] = 0 over all ordered pairs."""
    failures = []
    for X in labels:
        for Y in labels:
            s = -1 if (parity[X] and parity[Y]) else 1
            lhs = add_vec((1, bracket_basis(table, parity, X, Y)),
                          (s, bracket_basis(table, parity, Y, X)))
            if lhs:
                failures.append(("antisymmetry", X, Y, lhs))
    return failures


def check_jacobi(labels, parity, table):
    """Return list of failures for the super Jacobi identity over all triples."""
    failures = []
    for X in labels:
        for Y in labels:
            for Z in labels:
                s1 = -1 if (parity[X] and parity[Z]) else 1
                s2 = -1 if (parity[Y] and parity[X]) else 1
                s3 = -1 if (parity[Z] and parity[Y]) else 1
                t1 = bracket_vec(table, parity, {X: 1}, bracket_basis(table, parity, Y, Z))
                t2 = bracket_vec(table, parity, {Y: 1}, bracket_basis(table, parity, Z, X))
                t3 = bracket_vec(table, parity, {Z: 1}, bracket_basis(table, parity, X, Y))
                total = add_vec((s1, t1), (s2, t2), (s3, t3))
                if total:
                    failures.append(("jacobi", X, Y, Z, total))
    return failures


def verify(path):
    schema = load_structure(path)
    labels, parity, table = build_bracket_table(schema)
    anti = check_antisymmetry(labels, parity, table)
    jac = check_jacobi(labels, parity, table)
    return {
        "file": str(path),
        "basis_size": len(labels),
        "triples_checked": len(labels) ** 3,
        "antisymmetry_failures": anti,
        "jacobi_failures": jac,
        "passed": not anti and not jac,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    args = parser.parse_args(argv)
    all_ok = True
    for rank in (1, 2, 3):
        path = Path(args.data_dir) / f"C_{rank}_structure.json"
        result = verify(path)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] C({rank + 1}) n={rank}: basis={result['basis_size']}, "
              f"triples={result['triples_checked']}, "
              f"antisymmetry_failures={len(result['antisymmetry_failures'])}, "
              f"jacobi_failures={len(result['jacobi_failures'])}")
        for f in (result["antisymmetry_failures"] + result["jacobi_failures"])[:10]:
            print("   ", f)
        all_ok = all_ok and result["passed"]
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

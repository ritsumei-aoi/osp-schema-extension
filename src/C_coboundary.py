"""Layer 4: coboundary structure delta f for C(n+1) (Issue I07).

Odd linear map (docs/math/C_coboundary_definition.md):
    f(Z_j) = sum_i phi_{i,j} Z_i,   phi_{i,j} != 0 only if p(Z_i) != p(Z_j)
so f reverses parity. The coboundary is
    (delta f)(X, Y) = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1) pY} [Y, f(X)] - f([X, Y]).
The result is linear in the phi parameters and is stored symbolically.

Brackets are read from data/C_{n}_structure.json (Schema 1) through
src/verify_C_structure.py, so the coboundary is computed from the stored data.

Usage: python3 src/C_coboundary.py
"""

import json
import sys
from pathlib import Path

import sympy

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_C_structure import (  # noqa: E402
    bracket_basis,
    bracket_vec,
    build_bracket_table,
    load_structure,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def phi_symbol(i, j):
    """Symbol for the coefficient of Z_i in f(Z_j); i, j are 1-based PBW positions."""
    return sympy.Symbol(f"phi_{i}_{j}")


def to_sympy_table(table):
    """Convert Fraction coefficients of the Schema 1 table to sympy Rationals."""
    return {
        key: {z: sympy.Rational(c.numerator, c.denominator) for z, c in val.items()}
        for key, val in table.items()
    }


def make_f(labels, parity):
    """Return f as {label_j: {label_i: phi symbol}} with parity reversed."""
    f = {}
    for j, lj in enumerate(labels):
        for i, li in enumerate(labels):
            if parity[li] != parity[lj]:
                f.setdefault(lj, {})[li] = phi_symbol(i + 1, j + 1)
    return f


def parameter_list(labels, parity):
    """List of (symbol, label_i, label_j) for every free parameter of f."""
    out = []
    for j, lj in enumerate(labels):
        for i, li in enumerate(labels):
            if parity[li] != parity[lj]:
                out.append((phi_symbol(i + 1, j + 1), li, lj))
    return out


def apply_f(f, vec):
    out = {}
    for lab, c in vec.items():
        for lab2, s in f.get(lab, {}).items():
            out[lab2] = out.get(lab2, 0) + c * s
    return {k: sympy.expand(v) for k, v in out.items() if sympy.expand(v) != 0}


def _add(out, vec, coeff):
    for k, v in vec.items():
        out[k] = out.get(k, 0) + coeff * v


def coboundary_pair(X, Y, labels, parity, table, f):
    """(delta f)(X, Y) for basis labels X, Y."""
    pX, pY = parity[X], parity[Y]
    out = {}
    _add(out, bracket_vec(table, parity, {X: 1}, apply_f(f, {Y: 1})), (-1) ** pX)
    _add(out, bracket_vec(table, parity, {Y: 1}, apply_f(f, {X: 1})), -((-1) ** ((pX + 1) * pY)))
    _add(out, apply_f(f, bracket_basis(table, parity, X, Y)), -1)
    return {k: sympy.expand(v) for k, v in out.items() if sympy.expand(v) != 0}


def build_coboundary(n, data_dir=DATA_DIR):
    structure = load_structure(Path(data_dir) / f"C_{n}_structure.json")
    labels, parity, table = build_bracket_table(structure)
    table = to_sympy_table(table)
    f = make_f(labels, parity)
    entries = []
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            d = coboundary_pair(X, Y, labels, parity, table, f)
            for z in labels:
                if z in d:
                    entries.append({"X": X, "Y": Y, "Z": z, "coeff": str(d[z]), "sign_rule": "graded"})
    return {
        "schema_version": "5.0",
        "schema": "coboundary",
        "algebra_ref": f"C_{n}_structure.json",
        "map": {
            "definition": "f(Z_j) = sum_i phi_{i,j} Z_i with p(Z_i) != p(Z_j) (odd linear map)",
            "parameters": [{"symbol": str(s), "i": li, "j": lj} for s, li, lj in parameter_list(labels, parity)],
        },
        "coboundary": {
            "convention": "(delta f)(X,Y) = (-1)^{pX}[X,f(Y)] - (-1)^{(pX+1)pY}[Y,f(X)] - f([X,Y])",
            "entries": entries,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-08",
        },
    }


def consistency_check(n, data_dir=DATA_DIR):
    """Checks of delta f against Layer 1 (Schema 1). Returns a dict of counts."""
    structure = load_structure(Path(data_dir) / f"C_{n}_structure.json")
    labels, parity, table = build_bracket_table(structure)
    table = to_sympy_table(table)
    f = make_f(labels, parity)
    params = [s for s, _, _ in parameter_list(labels, parity)]
    report = {"label_errors": 0, "parity_violations": 0, "nonlinear_in_phi": 0,
              "symmetry_violations": 0}
    for X in labels:
        for Y in labels:
            d = coboundary_pair(X, Y, labels, parity, table, f)
            for z, c in d.items():
                if z not in parity:
                    report["label_errors"] += 1
                if parity[z] != (parity[X] + parity[Y] + 1) % 2:
                    report["parity_violations"] += 1
                if params and sympy.Poly(c, *params).total_degree() != 1:
                    report["nonlinear_in_phi"] += 1
    for i, X in enumerate(labels):
        for Y in labels[i + 1:]:
            s = -1 if (parity[X] and parity[Y]) else 1
            d_xy = coboundary_pair(X, Y, labels, parity, table, f)
            d_yx = coboundary_pair(Y, X, labels, parity, table, f)
            for z in set(d_xy) | set(d_yx):
                if sympy.expand(d_yx.get(z, 0) + s * d_xy.get(z, 0)) != 0:
                    report["symmetry_violations"] += 1
    return report


def main():
    for rank in (1, 2, 3):
        out = build_coboundary(rank)
        path = DATA_DIR / f"C_{rank}_coboundary.json"
        with path.open("w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
        print(path, "parameters:", len(out["map"]["parameters"]),
              "entries:", len(out["coboundary"]["entries"]))
        print("consistency", rank, consistency_check(rank))


if __name__ == "__main__":
    main()

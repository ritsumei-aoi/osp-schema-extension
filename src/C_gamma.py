"""
I05: Schema 2 (gamma structure) for C(n+1).

Deformed oscillator relation   [b_k^s, a_1^sigma] = - gb_{sigma,k,s} kappa
Deformed bracket               [X,Y}_gamma = [X,Y}_0 + kappa * gamma(X,Y)

gamma(X,Y) is the kappa-coefficient of the deformed bracket, decomposed in the basis; constant (K)
terms are dropped from gamma but recorded in `dropped_constant_terms` for transparency.

Usage:  python src/C_gamma.py [n ...]      -> data/C_{n}_gamma.json
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from fractions import Fraction
from typing import Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR, algebra_block, compute_brackets, parity_of, pbw_order  # noqa: E402
from oscillator import LinPoly  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402

GVec = Dict[str, LinPoly]  # vector in g with LinPoly coefficients


def gb_labels(n: int):
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
    entries = [[f"gb_{r}_{c}" for c in cols] for r in rows]
    return rows, cols, entries


def compute_gamma(n: int):
    """Return (gamma: {(X,Y): {Z: LinPoly}}, consts: {(X,Y): LinPoly}, base: {(X,Y): {Z: Fraction}})."""
    _, _, _, table = compute_brackets(n, deformed=True)
    gamma, consts, base = {}, {}, {}
    for (x, y), (c0, ck, constk) in table.items():
        base[(x, y)] = {z: c.scalar_value() for z, c in c0.items()}
        if ck:
            gamma[(x, y)] = ck
        if not constk.is_zero():
            consts[(x, y)] = constk
    return gamma, consts, base


# --------------------------------------------------------------------------- #
# Consistency checks
# --------------------------------------------------------------------------- #
def _vadd(u: GVec, v: GVec, c=1) -> GVec:
    out = dict(u)
    for k, val in v.items():
        out[k] = out.get(k, LinPoly()) + val * c
    return {k: v for k, v in out.items() if not v.is_zero()}


def _bracket_lin(bt: BracketTable, u: GVec, v: GVec) -> GVec:
    """[u, v} for vectors with LinPoly coefficients, using Schema 1 constants."""
    out: GVec = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, cz in bt.bracket_basis(x, y).items():
                out[z] = out.get(z, LinPoly()) + cx * cy * cz
    return {k: v for k, v in out.items() if not v.is_zero()}


def _gamma_lin(gamma, u: GVec, v: GVec) -> GVec:
    out: GVec = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, cz in gamma.get((x, y), {}).items():
                out[z] = out.get(z, LinPoly()) + cx * cy * cz
    return {k: v for k, v in out.items() if not v.is_zero()}


def cocycle_defect(bt: BracketTable, gamma, x: str, y: str, z: str) -> GVec:
    """Order-kappa part of the super Jacobi identity of g (+) kappa g:
    gamma(X,[Y,Z]) + (-1)^{p(X)}[X,gamma(Y,Z)] - gamma([X,Y],Z) - [gamma(X,Y),Z]
      - (-1)^{p(X)p(Y)} gamma(Y,[X,Z]) - (-1)^{p(X)p(Y)+p(Y)} [Y,gamma(X,Z)]   (must vanish)."""
    p = bt.parity
    one = lambda l: {l: LinPoly(1)}  # noqa: E731
    lin = lambda vec: {k: LinPoly(v) for k, v in vec.items()}  # noqa: E731
    t = _gamma_lin(gamma, one(x), lin(bt.bracket_basis(y, z)))
    t = _vadd(t, _bracket_lin(bt, one(x), gamma.get((y, z), {})), (-1) ** p[x])
    t = _vadd(t, _gamma_lin(gamma, lin(bt.bracket_basis(x, y)), one(z)), -1)
    t = _vadd(t, _bracket_lin(bt, gamma.get((x, y), {}), one(z)), -1)
    t = _vadd(t, _gamma_lin(gamma, one(y), lin(bt.bracket_basis(x, z))), -((-1) ** (p[x] * p[y])))
    t = _vadd(t, _bracket_lin(bt, one(y), gamma.get((x, z), {})), -((-1) ** (p[x] * p[y] + p[y])))
    return t


def check_consistency(n: int, gamma, consts, base, bt: BracketTable, verbose=True) -> dict:
    order = bt.order
    rep = {"base_matches_schema1": True, "parity_rule_failures": [], "nonlinear": [],
           "unknown_symbols": [], "cocycle_failures": [], "triples_checked": 0}
    # (a) kappa-free part of the deformed bracket == Schema 1
    for x in order:
        for y in order:
            if base[(x, y)] != bt.bracket_basis(x, y):
                rep["base_matches_schema1"] = False
    # (b) parity rule, (c) linearity, symbols
    _, _, entries = gb_labels(n)
    allowed = {e for row in entries for e in row}
    for (x, y), vec in gamma.items():
        for z, c in vec.items():
            if parity_of(z) != (parity_of(x) + parity_of(y) + 1) % 2:
                rep["parity_rule_failures"].append((x, y, z))
            if c.degree() != 1 or () in c.terms:
                rep["nonlinear"].append((x, y, z, c.expr()))
            for s in c.symbols():
                if s not in allowed:
                    rep["unknown_symbols"].append(s)
    # (d) cocycle identity for all ordered triples
    for x in order:
        for y in order:
            for z in order:
                rep["triples_checked"] += 1
                d = cocycle_defect(bt, gamma, x, y, z)
                if d:
                    rep["cocycle_failures"].append((x, y, z, {k: v.expr() for k, v in d.items()}))
    rep["pass"] = (rep["base_matches_schema1"] and not rep["parity_rule_failures"] and not rep["nonlinear"]
                   and not rep["unknown_symbols"] and not rep["cocycle_failures"])
    if verbose:
        print(f"[C({n+1}), n={n}] gamma: {len(gamma)} ordered pairs with non-zero gamma, "
              f"{sum(len(v) for v in gamma.values())} coefficients, {len(consts)} pairs with dropped constant terms")
        print(f"  kappa-free part == Schema 1 : {rep['base_matches_schema1']}")
        print(f"  parity rule p(Z)=p(X)+p(Y)+1: failures={len(rep['parity_rule_failures'])}")
        print(f"  linear in gb, known symbols : nonlinear={len(rep['nonlinear'])}, unknown={len(rep['unknown_symbols'])}")
        print(f"  cocycle identity (order kappa Jacobi): {rep['triples_checked']} triples, failures={len(rep['cocycle_failures'])}")
        print(f"  RESULT: {'PASS' if rep['pass'] else 'FAIL'}")
        for f in rep["cocycle_failures"][:5]:
            print("   cocycle failure:", f)
    return rep


# --------------------------------------------------------------------------- #
# Schema 2 JSON
# --------------------------------------------------------------------------- #
def build_gamma_json(n: int) -> Tuple[dict, dict]:
    gamma, consts, base = compute_gamma(n)
    bt = BracketTable.load(n)
    rep = check_consistency(n, gamma, consts, base, bt, verbose=False)
    order = pbw_order(n)
    idx = {l: i for i, l in enumerate(order)}
    rows, cols, entries = gb_labels(n)

    gamma_list = []
    for x in order:
        for y in order:
            vec = gamma.get((x, y))
            if not vec:
                continue
            for z, c in sorted(vec.items(), key=lambda kv: idx[kv[0]]):
                gamma_list.append({"X": x, "Y": y, "Z": z, "coeff": c.to_json(), "expr": c.expr()})
    const_list = [{"X": x, "Y": y, "Z": "K", "coeff": c.to_json(), "expr": c.expr()}
                  for (x, y), c in sorted(consts.items(), key=lambda kv: (idx[kv[0][0]], idx[kv[0][1]]))]
    rel = []
    for sigma in ("p", "m"):
        for k in range(1, n + 1):
            for s in ("p", "m"):
                rel.append({"relation": f"[b_{k}_{s}, a_1_{sigma}] = -gb_a_1_{sigma}_b_{k}_{s} * kappa"})
    doc = {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {k: algebra_block(n)[k] for k in ("family", "m", "n", "cartan_type")},
        "source_structure": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa ; [X,Y}_gamma = [X,Y}_0 + kappa * gamma(X,Y) (kappa on the left)",
            "kappa": {"parity": 1, "nilpotent": True, "supercentral": True, "position": "left"},
            "gb_matrix": {
                "shape": [2, 2 * n], "rows": rows, "columns": cols, "entries": entries,
                "parameter_count": 4 * n,
                "parameter_parity_note": "scalars; the odd parity of the deformation is carried by kappa",
            },
            "deformed_oscillator_relations": rel,
            "gamma_parity_rule": "p(gamma(X,Y)) = p(X) + p(Y) + 1 (mod 2); constant (K) terms dropped",
            "gamma": gamma_list,
            "dropped_constant_terms": const_list,
        },
        "consistency": {
            "kappa_free_part_equals_schema1": rep["base_matches_schema1"],
            "parity_rule_ok": not rep["parity_rule_failures"],
            "linear_in_gb": not rep["nonlinear"],
            "cocycle_identity_ok": not rep["cocycle_failures"],
            "triples_checked": rep["triples_checked"],
        },
        "metadata": {"generated_by": "src/C_gamma.py", "generation_date": date.today().isoformat(),
                     "notation": "handover/notation.md",
                     "definition": "docs/math/C_inhomogeneous_definition.md"},
    }
    return doc, rep


def write_gamma(n: int, data_dir: str = DATA_DIR):
    doc, rep = build_gamma_json(n)
    path = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path, rep


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        gamma, consts, base = compute_gamma(n)
        rep = check_consistency(n, gamma, consts, base, BracketTable.load(n))
        ok &= rep["pass"]
        path, _ = write_gamma(n)
        print(f"  wrote {path}")
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)

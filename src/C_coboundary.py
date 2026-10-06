"""Schema 4 (coboundary structure) for C(n+1).

Odd linear map  f(Z_j) = sum_i phi_i_j Z_i   (only p(Z_i) != p(Z_j)),
optionally with a central component  f(Z_j) += phi_K_j K  for odd Z_j  (K even, = 1).
Coboundary (docs/math/C_coboundary_definition.md):
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])
Indices i, j are 1-based positions in the PBW-ordered basis (`basis.ordered` of Schema 1).

Usage:  python3 src/C_coboundary.py     # writes data/C_{1,2,3}_coboundary.json and checks them
"""
from __future__ import annotations

import datetime
import json
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import _parse_lin, extended_structure  # noqa: E402
from C_generators import DATA_DIR, K_LABEL, SCHEMA_VERSION, write_json  # noqa: E402
from C_osc import Lin  # noqa: E402
from verify_C_structure import load_table, verify  # noqa: E402


def phi_name(i: int, j: int) -> str:
    return f"phi_{i}_{j}"


def phiK_name(j: int) -> str:
    return f"phi_K_{j}"


def odd_map(basis: list, par: dict, central: bool = True) -> dict:
    """f as {Z_j: {Z_i or 'K': Lin(phi symbol)}}."""
    f = {}
    for j, zj in enumerate(basis, 1):
        img = {zi: Lin.sym(phi_name(i, j)) for i, zi in enumerate(basis, 1) if par[zi] != par[zj]}
        if central and par[zj] == 1:
            img[K_LABEL] = Lin.sym(phiK_name(j))
        f[zj] = img
    return f


def _add(out: dict, z: str, c: Lin) -> None:
    v = out.get(z, Lin()) + c
    if v:
        out[z] = v
    else:
        out.pop(z, None)


def coboundary(struct: dict, central: bool = True) -> tuple[dict, dict]:
    """Return (f, delta_f) with delta_f = {(X,Y): {Z: Lin}} for all ordered pairs."""
    basis, par, table = load_table(struct)
    f = odd_map(basis, par, central)

    def br(x, v: dict) -> dict:  # [x, v] with v = {label: Lin}; K is central
        out: dict = {}
        for y, c in v.items():
            if y == K_LABEL:
                continue
            for z, a in table.get((x, y), {}).items():
                _add(out, z, c.scale(a))
        return out

    def fmap(v: dict) -> dict:  # f(v) for v = {label: Fraction}
        out: dict = {}
        for y, a in v.items():
            for z, c in f[y].items():
                _add(out, z, c.scale(a))
        return out

    df = {}
    for x in basis:
        for y in basis:
            px, py = par[x], par[y]
            out: dict = {}
            for z, c in br(x, f[y]).items():
                _add(out, z, c.scale((-1) ** px))
            for z, c in br(y, f[x]).items():
                _add(out, z, c.scale(-((-1) ** ((px + 1) * py))))
            for z, c in fmap(table.get((x, y), {})).items():
                _add(out, z, -c)
            if out:
                df[(x, y)] = out
    return f, df


def build_coboundary(n: int, struct: dict) -> dict:
    basis = struct["basis"]["ordered"]
    f, df = coboundary(struct)
    entries = []
    for x in basis:
        for y in basis:
            d = df.get((x, y), {})
            for z in basis + [K_LABEL]:
                if z in d:
                    entries.append({"X": x, "Y": y, "Z": z, "coeff": d[z].to_str()})
    n_phi = sum(1 for zj in basis for zi in f[zj] if zi != K_LABEL)
    n_phiK = sum(1 for zj in basis if K_LABEL in f[zj])
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": struct["algebra"],
        "basis_ref": {"file": f"C_{n}_structure.json", "ordered": basis},
        "central_elements": struct["central_elements"],
        "odd_map": {
            "definition": "f(Z_j) = sum_i phi_i_j Z_i  with p(Z_i) != p(Z_j);  i, j = 1-based index in basis_ref.ordered",
            "central_component": "for odd Z_j additionally phi_K_j * K (K = 1 even central); set phi_K_j = 0 for f: g -> g",
            "parity": 1,
            "parameter_count": {"phi": n_phi, "phi_K": n_phiK},
            "index": {str(i): b for i, b in enumerate(basis, 1)},
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
        "coboundary": entries,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_coboundary_definition.md"],
            "notation": "handover/notation.md",
        },
    }


def check(n: int, cob: dict, struct: dict, trials: int = 3) -> dict:
    basis = struct["basis"]["ordered"]
    par = struct["parity"]
    res = {"basis_match": cob["basis_ref"]["ordered"] == basis, "labels_known": True, "parity_ok": True,
           "antisymmetry_ok": True, "cocycle_ok": True,
           "param_count_ok": cob["odd_map"]["parameter_count"]["phi"] == 2 * sum(1 - par[b] for b in basis) * sum(par[b] for b in basis)}
    table = {}
    syms = set()
    for e in cob["coboundary"]:
        x, y, z = e["X"], e["Y"], e["Z"]
        if x not in par or y not in par or (z != K_LABEL and z not in par):
            res["labels_known"] = False
            continue
        pz = 0 if z == K_LABEL else par[z]
        if pz != (par[x] + par[y] + 1) % 2:
            res["parity_ok"] = False
        lin = _parse_lin(e["coeff"])
        syms |= set(lin)
        table[(x, y, z)] = lin
    for (x, y, z), v in table.items():
        if v + table.get((y, x, z), Lin()).scale((-1) ** (par[x] * par[y])):
            res["antisymmetry_ok"] = False
    # delta f must be a 2-cocycle with the same conventions as gamma (Jacobi of the extended algebra)
    rng = random.Random(7 + n)
    syms.discard("1")
    for _ in range(trials):
        vals = {s: rng.randint(-3, 3) for s in syms}
        ent = cob["coboundary"]
        if not verify(extended_structure(struct, ent, vals))["passed"]:
            res["cocycle_ok"] = False
    res["passed"] = all(res.values())
    return res


def main(ns=(1, 2, 3)) -> int:
    ok = True
    for n in ns:
        with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
            struct = json.load(fh)
        cob = build_coboundary(n, struct)
        write_json(cob, f"C_{n}_coboundary.json")
        res = check(n, cob, struct, trials=3 if n < 3 else 1)
        pc = cob["odd_map"]["parameter_count"]
        print(f"n={n}: phi={pc['phi']}, phi_K={pc['phi_K']}, {len(cob['coboundary'])} coboundary entries; checks {res}")
        ok &= res["passed"]
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

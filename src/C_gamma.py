"""Schema 2 (gamma structure) for the inhomogeneous deformation of C(n+1)  (Issue I05).

Deformed oscillator relation (docs/math/C_inhomogeneous_definition.md):
    [b_k^s, a_1^sigma] = - gb_{a_1^sigma, b_k^s} * kappa,
with kappa odd, super-central, kappa^2 = 0 and gb_* commuting scalar parameters.
For basis generators X, Y the engine gives
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),
and gamma(X,Y) is decomposed in the basis of g plus the even central element K.

Consistency checks performed (see check_schema2):
  1. kappa^0 part == Schema 1 structure constants
  2. graded antisymmetry of gamma
  3. parity rule p(gamma(X,Y)) = p(X)+p(Y)+1   (K counts as even)
  4. first-order cocycle identity (kappa-part of the Jacobi identity in U(A)):
     gamma(X,[Y,Z]) + (-1)^{p(X)} [X,gamma(Y,Z)]
       = gamma([X,Y],Z) + [gamma(X,Y),Z]
         + (-1)^{p(X)p(Y)} ( gamma(Y,[X,Z]) + (-1)^{p(Y)} [Y,gamma(X,Z)] )

Usage: python src/C_gamma.py [--n 1 2 3] [--datadir data]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import itertools
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import CAlgebra, algebra_block, central_elements_block, write_json  # noqa: E402
from osc_algebra import Poly, frac_str, poly_terms_json  # noqa: E402

PVec = Dict[str, Poly]          # vector in g + C K with Poly coefficients
Table = Dict[Tuple[str, str], PVec]


# --------------------------------------------------------------------------- computation


def compute_gamma(n: int, deformation="symbolic") -> Tuple[CAlgebra, Table, Table]:
    """Return (C, bracket0, gamma): kappa^0 and kappa^1 parts of all brackets."""
    C = CAlgebra(n, deformation=deformation)
    br0: Table = {}
    gam: Table = {}
    for x in C.labels:
        for y in C.labels:
            z0, z1 = C.bracket(x, y)
            if z0:
                br0[(x, y)] = z0
            if z1:
                gam[(x, y)] = z1
    return C, br0, gam


def gb_matrix_block(n: int) -> dict:
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    labels = [[f"gb_a1{sig}_b{k}{s}" for k in range(1, n + 1) for s in "pm"] for sig in "pm"]
    return {"shape": [2, 2 * n], "rows": rows, "columns": cols, "labels": labels,
            "count": 4 * n, "parameter_type": "commuting scalar",
            "index_convention": "gb_a1{sigma}_b{k}{s} = gb_{a_1^sigma, b_k^s}; sigma = sign of the fermion, s = sign of the boson"}


def gamma_records(C: CAlgebra, gam: Table) -> List[dict]:
    recs = []
    for (x, y), comps in sorted(gam.items(), key=lambda kv: (C.index[kv[0][0]], C.index[kv[0][1]])):
        for z, p in sorted(comps.items(), key=lambda kv: C.sort_key(kv[0])):
            recs.append({"X": x, "Y": y, "Z": z, "terms": poly_terms_json(p)})
    return recs


def build_schema2(n: int, today=None) -> dict:
    C, br0, gam = compute_gamma(n)
    return {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": algebra_block(n),
        "source_structure": f"C_{n}_structure.json",
        "central_elements": central_elements_block(),
        "inhomogeneous_deformation": {
            "type": "inhomogeneous",
            "definition": "[b_k^s, a_1^sigma] = - gb_{a_1^sigma, b_k^s} * kappa   (kappa odd, central, kappa^2 = 0)",
            "bracket_form": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)   (kappa written on the left)",
            "gb_matrix": gb_matrix_block(n),
            "gamma_parity_rule": "p(gamma(X,Y)) = p(X) + p(Y) + 1 (mod 2); K counts as even",
            "target_space": "g + C K  (K = 1: constant terms produced by the deformed bracket)",
            "linearity": "gamma is linear homogeneous in the gb parameters (kappa^2 = 0)",
        },
        "gamma": gamma_records(C, gam),
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": today or _dt.date.today().isoformat(),
            "schema_specification": "docs/json_schema_specification.md",
            "notation": "handover/notation.md",
            "references": ["docs/math/C_inhomogeneous_definition.md", "docs/math/Cn1_definition.md"],
        },
    }


# --------------------------------------------------------------------------- loading / checks


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def bracket_table_from_schema1(doc1: dict) -> Dict[Tuple[str, str], Dict[str, Fraction]]:
    t: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for r in doc1["structure_constants"]:
        t.setdefault((r["X"], r["Y"]), {})[r["Z"]] = Fraction(r["coeff"])
    return t


def gamma_table_from_records(records: List[dict], key="terms") -> Table:
    """Schema 2 records -> {(X,Y): {Z: Poly}};  Schema 3 records (key='coeff') -> constants."""
    t: Table = {}
    for r in records:
        if key == "terms":
            p = Poly()
            for term in r["terms"]:
                p = p + (Poly.const(Fraction(term["coeff"])) if term["gb"] == "1"
                         else Poly.symbol(term["gb"], Fraction(term["coeff"])))
        else:
            p = Poly.const(Fraction(r["coeff"]))
        t.setdefault((r["X"], r["Y"]), {})[r["Z"]] = p
    return t


def _padd(*vs: PVec) -> PVec:
    out: PVec = {}
    for v in vs:
        for k, c in v.items():
            out[k] = out[k] + c if k in out else c
    return {k: c for k, c in out.items() if not c.is_zero()}


def _pscale(v: PVec, s) -> PVec:
    return {k: c.scale(s) for k, c in v.items() if not c.scale(s).is_zero()}


def cocycle_residuals(labels: List[str], parity: Dict[str, int],
                      br: Dict[Tuple[str, str], Dict[str, Fraction]], gam: Table) -> List[str]:
    """Residuals of the first-order cocycle identity for all ordered triples."""
    def br_x_vec(x: str, v: PVec) -> PVec:            # [x, v], v with Poly coeffs; [x,K]=0
        out: PVec = {}
        for z, c in v.items():
            if z == "K":
                continue
            for w, d in br.get((x, z), {}).items():
                out[w] = out[w] + c.scale(d) if w in out else c.scale(d)
        return {k: c for k, c in out.items() if not c.is_zero()}

    def vec_br_y(v: PVec, y: str) -> PVec:            # [v, y]
        out: PVec = {}
        for z, c in v.items():
            if z == "K":
                continue
            for w, d in br.get((z, y), {}).items():
                out[w] = out[w] + c.scale(d) if w in out else c.scale(d)
        return {k: c for k, c in out.items() if not c.is_zero()}

    def gam_x_vec(x: str, v: Dict[str, Fraction]) -> PVec:   # gamma(x, v), v in g
        out: PVec = {}
        for z, c in v.items():
            for w, p in gam.get((x, z), {}).items():
                out[w] = out[w] + p.scale(c) if w in out else p.scale(c)
        return {k: c for k, c in out.items() if not c.is_zero()}

    def gam_vec_y(v: Dict[str, Fraction], y: str) -> PVec:
        out: PVec = {}
        for z, c in v.items():
            for w, p in gam.get((z, y), {}).items():
                out[w] = out[w] + p.scale(c) if w in out else p.scale(c)
        return {k: c for k, c in out.items() if not c.is_zero()}

    fails = []
    for x, y, z in itertools.product(labels, repeat=3):
        sx = -1 if parity[x] else 1
        sy = -1 if parity[y] else 1
        sxy = -1 if (parity[x] and parity[y]) else 1
        lhs = _padd(gam_x_vec(x, br.get((y, z), {})), _pscale(br_x_vec(x, gam.get((y, z), {})), sx))
        rhs = _padd(gam_vec_y(br.get((x, y), {}), z),
                    vec_br_y(gam.get((x, y), {}), z),
                    _pscale(_padd(gam_x_vec(y, br.get((x, z), {})),
                                  _pscale(br_x_vec(y, gam.get((x, z), {})), sy)), sxy))
        diff = _padd(lhs, _pscale(rhs, -1))
        if diff:
            fails.append(f"cocycle({x},{y},{z}): residual {diff}")
    return fails


def check_schema2(doc2: dict, doc1: dict, br0: Table | None = None) -> dict:
    """Consistency checks of a Schema 2 document against its Schema 1 source."""
    labels = doc1["basis"]["pbw_order"]
    parity = doc1["parity"]
    br = bracket_table_from_schema1(doc1)
    gam = gamma_table_from_records(doc2["gamma"])
    rep = {"n": doc1["algebra"]["n"], "failures": {}, "counts": {}}

    # 1. kappa^0 part equals Schema 1 (recomputed with the deformation switched on)
    fails = []
    if br0 is not None:
        for key in set(br) | set(br0):
            a = {z: Poly.const(c) for z, c in br.get(key, {}).items()}
            b = br0.get(key, {})
            if _padd(a, _pscale(b, -1)):
                fails.append(f"kappa^0 part of [{key[0]},{key[1]}] differs from Schema 1")
    rep["failures"]["kappa0_equals_schema1"] = fails

    # 2. graded antisymmetry of gamma
    fails = []
    for x in labels:
        for y in labels:
            sign = -1 if (parity[x] and parity[y]) else 1
            lhs = gam.get((y, x), {})
            rhs = _pscale(gam.get((x, y), {}), -sign)
            if _padd(lhs, _pscale(rhs, -1)):
                fails.append(f"gamma({y},{x}) != -(-1)^(pp) gamma({x},{y})")
    rep["failures"]["antisymmetry"] = fails

    # 3. parity rule and linearity in gb
    fails = []
    for (x, y), comps in gam.items():
        for z, p in comps.items():
            pz = 0 if z == "K" else parity[z]
            if pz != (parity[x] + parity[y] + 1) % 2:
                fails.append(f"gamma({x},{y}) has component {z} of wrong parity")
            if any(len(m) != 1 for m in p.terms):
                fails.append(f"gamma({x},{y})_{z} = {p} is not linear homogeneous in gb")
    rep["failures"]["parity_linearity"] = fails

    # 4. cocycle identity
    rep["failures"]["cocycle"] = cocycle_residuals(labels, parity, br, gam)
    rep["counts"]["gamma_records"] = len(doc2["gamma"])
    rep["counts"]["nonzero_pairs"] = len(gam)
    rep["counts"]["pairs_with_K_component"] = sum(1 for comps in gam.values() if "K" in comps)
    rep["counts"]["triples_checked"] = len(labels) ** 3
    rep["passed"] = all(not v for v in rep["failures"].values())
    return rep


def print_report(rep: dict, title: str) -> None:
    print(f"== {title} (n={rep['n']}) ==")
    for k, v in rep["counts"].items():
        print(f"  {k}: {v}")
    for name, fails in rep["failures"].items():
        print(f"  {name:26s}: {'PASS' if not fails else f'FAIL ({len(fails)})'}")
        for line in fails[:5]:
            print("     ", line)
    print(f"  overall: {'PASS' if rep['passed'] else 'FAIL'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args(argv)
    ok = True
    for n in args.n:
        doc2 = build_schema2(n)
        path = os.path.join(args.datadir, f"C_{n}_gamma.json")
        write_json(doc2, path)
        print(f"wrote {path}: {len(doc2['gamma'])} gamma records")
        if not args.no_check:
            doc1 = load_json(os.path.join(args.datadir, f"C_{n}_structure.json"))
            _, br0, _ = compute_gamma(n)
            rep = check_schema2(doc2, doc1, br0)
            print_report(rep, "Schema 2 consistency")
            ok = ok and rep["passed"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

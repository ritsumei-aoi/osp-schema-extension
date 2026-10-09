"""Schema 4 (coboundary structure) for C(n+1)  (Issue I07).

Odd linear map f: g -> g + C K  (parity reversing), parameterised by
    f(Z_j) = sum_i phi_<i>_<j> Z_i  (+ phiK_<j> K for odd Z_j),
and its coboundary (docs/math/C_coboundary_definition.md)
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y]),
with [X, K] = 0.

Reference (canonical) map.  In U(A) with the deformed relation [b_k^s, a_1^sigma] = -gb kappa,
the shifted fermions
    a~_1^sigma = a_1^sigma - kappa * c^sigma,
    c^sigma    = sum_k ( gb_{a_1^sigma, b_k^-} b_k^+ - gb_{a_1^sigma, b_k^+} b_k^- )
satisfy the *undeformed* relations ([b_k^s, a~^sigma] = 0, {a~^-, a~^+} = 1, (a~^±)^2 = 0).
Writing every generator in terms of (a~, b),  X(a~, b) = X(a, b) + kappa f_can(X),
one obtains gamma = delta f_can exactly (proof in the I07/I08 Response).  f_can is computed
here by the oscillator engine (substitute, normal-order, take the kappa-coefficient,
decompose in basis + K) -- not typed in by hand.

Usage: python src/C_coboundary.py [--n 1 2 3] [--profile all_plus_one] [--suffix ""]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_evaluate import DATADIR, gb_profile  # noqa: E402
from C_gamma import (PVec, Table, bracket_table_from_schema1, gamma_table_from_records,  # noqa: E402
                     load_json, _padd, _pscale)
from C_generators import CAlgebra, write_json  # noqa: E402
from osc_algebra import Element, OscillatorAlgebra, Poly, el_add, el_scale, frac_str  # noqa: E402

FMap = Dict[str, PVec]        # f: source label -> {target label (basis or "K"): Poly}


# --------------------------------------------------------------------------- coboundary of an odd map


def delta_f(f: FMap, br: Dict[Tuple[str, str], Dict[str, Fraction]], labels: List[str],
            parity: Dict[str, int]) -> Table:
    """(delta f)(X,Y) for all ordered pairs; returns {(X,Y): {Z: Poly}} (zeros dropped)."""
    def br_x_vec(x: str, v: PVec) -> PVec:
        out: PVec = {}
        for z, c in v.items():
            if z == "K":
                continue
            for w, d in br.get((x, z), {}).items():
                out[w] = out[w] + c.scale(d) if w in out else c.scale(d)
        return {k: c for k, c in out.items() if not c.is_zero()}

    def f_vec(v: Dict[str, Fraction]) -> PVec:
        out: PVec = {}
        for z, c in v.items():
            for w, p in f.get(z, {}).items():
                out[w] = out[w] + p.scale(c) if w in out else p.scale(c)
        return {k: c for k, c in out.items() if not c.is_zero()}

    out: Table = {}
    for x in labels:
        for y in labels:
            sx = -1 if parity[x] else 1
            sxy = -1 if ((parity[x] + 1) % 2 and parity[y]) else 1
            val = _padd(_pscale(br_x_vec(x, f.get(y, {})), sx),
                        _pscale(br_x_vec(y, f.get(x, {})), -sxy),
                        _pscale(f_vec(br.get((x, y), {})), -1))
            if val:
                out[(x, y)] = val
    return out


def check_odd_map(f: FMap, parity: Dict[str, int]) -> List[str]:
    fails = []
    for src, comps in f.items():
        for tgt in comps:
            pt = 0 if tgt == "K" else parity[tgt]
            if pt != (parity[src] + 1) % 2:
                fails.append(f"f({src}) has component {tgt} of the same parity")
    return fails


# --------------------------------------------------------------------------- canonical map


def canonical_f(n: int, gb) -> FMap:
    """f_can for gb = dict {label: Fraction} or 'symbolic'.  Computed by the engine."""
    C = CAlgebra(n)                                   # undeformed relations (kappa symbol present)
    A: OscillatorAlgebra = C.alg
    sym = gb == "symbolic"

    def g(sig: str, k: int, s: str) -> Poly:
        lab = A.gb_label(sig, k, s)
        return Poly.symbol(lab) if sym else Poly.const(Fraction(gb.get(lab, 0)))

    # c^sigma = sum_k ( gb_{sigma,k,-} b_k^+ - gb_{sigma,k,+} b_k^- )
    c: Dict[str, Element] = {}
    for sig in "pm":
        el: Element = {}
        for k in range(1, n + 1):
            el = el_add(el, el_scale({(f"b_{k}_p",): Poly.const(1)}, g(sig, k, "m")))
            el = el_add(el, el_scale({(f"b_{k}_m",): Poly.const(1)}, -g(sig, k, "p")))
        c[sig] = el
    # a~^sigma = a^sigma - kappa c^sigma
    shifted = {f"a_1_{sig}": el_add({(f"a_1_{sig}",): Poly.const(1)}, el_scale(A.mul({("kappa",): Poly.const(1)}, c[sig]), -1))
               for sig in "pm"}

    f: FMap = {}
    for lab in C.labels:
        total: Element = {}
        for word, coeff in C.real[lab].items():
            prod: Element = {(): Poly.const(1)}
            for s in word:
                factor = shifted[s] if s in shifted else {(s,): Poly.const(1)}
                prod = A.mul(prod, factor)
            total = el_add(total, el_scale(prod, coeff))
        z0, z1 = A.split_kappa(total)
        # sanity: kappa^0 part is the original realization
        assert el_add(z0, el_scale(C.real[lab], -1)) == {}, lab
        comps = C.decomposer.decompose(z1)
        if comps:
            f[lab] = comps
    return f


# --------------------------------------------------------------------------- Schema 4


def f_records(f: FMap, labels: List[str]) -> List[dict]:
    idx = {l: i for i, l in enumerate(labels)}
    key = lambda lab: idx.get(lab, len(labels))
    recs = []
    for src in sorted(f, key=key):
        for tgt, p in sorted(f[src].items(), key=lambda kv: key(kv[0])):
            recs.append({"source": src, "target": tgt, "coeff": frac_str(p.const_value())})
    return recs


def phi_values(f: FMap, labels: List[str]) -> Dict[str, str]:
    idx = {l: i for i, l in enumerate(labels)}
    out = {}
    for src, comps in f.items():
        for tgt, p in comps.items():
            name = f"phiK_{idx[src]}" if tgt == "K" else f"phi_{idx[tgt]}_{idx[src]}"
            out[name] = frac_str(p.const_value())
    return dict(sorted(out.items()))


def build_schema4(n: int, profile: str = "all_plus_one", values=None, today=None,
                  doc1: dict | None = None) -> dict:
    doc1 = doc1 or load_json(os.path.join(DATADIR, f"C_{n}_structure.json"))
    labels, parity = doc1["basis"]["pbw_order"], doc1["parity"]
    idx = {l: i for i, l in enumerate(labels)}
    key = lambda lab: idx.get(lab, len(labels))
    br = bracket_table_from_schema1(doc1)
    gb = gb_profile(n, profile, values)
    f = canonical_f(n, gb)
    assert not check_odd_map(f, parity)
    df = delta_f(f, br, labels, parity)
    cob = []
    for (x, y), comps in sorted(df.items(), key=lambda kv: (idx[kv[0][0]], idx[kv[0][1]])):
        for z, p in sorted(comps.items(), key=lambda kv: key(kv[0])):
            cob.append({"X": x, "Y": y, "Z": z, "coeff": frac_str(p.const_value())})
    n_even, n_odd = len(doc1["basis"]["even"]), len(doc1["basis"]["odd"])
    return {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": doc1["algebra"],
        "source_structure": f"C_{n}_structure.json",
        "source_evaluated": f"C_{n}_evaluated{'' if profile == 'all_plus_one' else '_' + profile.replace(':', '_')}.json",
        "central_elements": doc1["central_elements"],
        "odd_map_f": {
            "parameterization": "f(Z_j) = sum_i phi_<i>_<j> Z_i with p(Z_i) != p(Z_j), plus phiK_<j> K for odd Z_j; "
                                "indices are basis indices in basis.pbw_order (odd first, 0-based)",
            "parity_rule": "p(f(X)) = p(X) + 1 (K counts as even)",
            "phi_count": 2 * n_even * n_odd,
            "phiK_count": n_odd,
            "reference": {
                "name": "canonical_gb",
                "gb_assignment": {"profile": profile, "values": {k: frac_str(v) for k, v in gb.items()}},
                "definition": "f_can(X) = kappa-coefficient of X(a~, b) where a~_1^sigma = a_1^sigma - kappa c^sigma, "
                              "c^sigma = sum_k ( gb_{a_1^sigma,b_k^-} b_k^+ - gb_{a_1^sigma,b_k^+} b_k^- )",
                "closed_form": {
                    "odd generators": "f_can(a_1^sigma b_k^u) = - c^sigma b_k^u   (normal-ordered; constants -> K)",
                    "H_1": "f_can(H_1) = a_1^+ c^- - c^+ a_1^-",
                    "sp(2n) generators and H_2..H_{n+1}": "0",
                },
                "property": "gamma = delta f_can for every gb (see I07/I08 Response)",
                "values": phi_values(f, labels),
            },
            "f_matrix": f_records(f, labels),
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y]),  [X,K] = 0",
        "coboundary": cob,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": today or _dt.date.today().isoformat(),
            "schema_specification": "docs/json_schema_specification.md",
            "notation": "handover/notation.md",
            "references": ["docs/math/C_coboundary_definition.md", "docs/math/C_inhomogeneous_definition.md"],
        },
    }


# --------------------------------------------------------------------------- checks


def check_schema4(doc4: dict, doc1: dict, doc3: dict | None = None) -> dict:
    labels, parity = doc1["basis"]["pbw_order"], doc1["parity"]
    basis = set(labels)
    br = bracket_table_from_schema1(doc1)
    rep = {"n": doc1["algebra"]["n"], "failures": {}, "counts": {}}

    # labels consistent with Layer 1
    fails = []
    f: FMap = {}
    for r in doc4["odd_map_f"]["f_matrix"]:
        if r["source"] not in basis or (r["target"] not in basis and r["target"] != "K"):
            fails.append(f"f record with unknown label: {r}")
        f.setdefault(r["source"], {})[r["target"]] = Poly.const(Fraction(r["coeff"]))
    for r in doc4["coboundary"]:
        if r["X"] not in basis or r["Y"] not in basis or (r["Z"] not in basis and r["Z"] != "K"):
            fails.append(f"coboundary record with unknown label: {r}")
    rep["failures"]["labels_in_layer1_basis"] = fails
    rep["failures"]["f_is_odd"] = check_odd_map(f, parity)

    # stored coboundary == recomputed delta f from the stored f and Schema 1 brackets
    stored = gamma_table_from_records(doc4["coboundary"], key="coeff")
    recomputed = delta_f(f, br, labels, parity)
    fails = []
    for key in set(stored) | set(recomputed):
        if _padd(stored.get(key, {}), _pscale(recomputed.get(key, {}), -1)):
            fails.append(f"delta f{key} stored != recomputed")
    rep["failures"]["coboundary_recomputed"] = fails

    # graded antisymmetry of delta f
    fails = []
    for x in labels:
        for y in labels:
            sign = -1 if (parity[x] and parity[y]) else 1
            if _padd(stored.get((y, x), {}), _pscale(stored.get((x, y), {}), sign)):
                fails.append(f"delta f({y},{x}) not graded-antisymmetric")
    rep["failures"]["antisymmetry"] = fails

    # optional: comparison with Layer 3
    if doc3 is not None:
        gam = gamma_table_from_records(doc3["evaluated_gamma"], key="coeff")
        mism = [key for key in set(stored) | set(gam) if _padd(stored.get(key, {}), _pscale(gam.get(key, {}), -1))]
        rep["counts"]["layer3_pairs_compared"] = len(set(stored) | set(gam))
        rep["counts"]["layer3_mismatching_pairs"] = len(mism)
        rep["failures"]["equals_layer3_gamma"] = [f"gamma != delta f at {k}" for k in sorted(mism)]
    rep["counts"]["f_records"] = len(doc4["odd_map_f"]["f_matrix"])
    rep["counts"]["f_K_components"] = sum(1 for r in doc4["odd_map_f"]["f_matrix"] if r["target"] == "K")
    rep["counts"]["coboundary_records"] = len(doc4["coboundary"])
    rep["counts"]["nonzero_pairs"] = len(stored)
    rep["passed"] = all(not v for v in rep["failures"].values())
    return rep


def print_report(rep: dict, title: str) -> None:
    print(f"== {title} (n={rep['n']}) ==")
    for k, v in rep["counts"].items():
        print(f"  {k}: {v}")
    for name, fails in rep["failures"].items():
        print(f"  {name:28s}: {'PASS' if not fails else f'FAIL ({len(fails)})'}")
        for line in fails[:5]:
            print("     ", line)
    print(f"  overall: {'PASS' if rep['passed'] else 'FAIL'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--profile", default="all_plus_one")
    ap.add_argument("--values", default=None)
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--datadir", default=DATADIR)
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args(argv)
    values = json.loads(args.values) if args.values else None
    suffix = args.suffix if args.suffix is not None else ("" if args.profile == "all_plus_one" else "_" + args.profile.replace(":", "_"))
    ok = True
    for n in args.n:
        doc1 = load_json(os.path.join(args.datadir, f"C_{n}_structure.json"))
        doc4 = build_schema4(n, args.profile, values, doc1=doc1)
        path = os.path.join(args.datadir, f"C_{n}_coboundary{suffix}.json")
        write_json(doc4, path)
        print(f"wrote {path}: {len(doc4['odd_map_f']['f_matrix'])} f records, {len(doc4['coboundary'])} coboundary records")
        if not args.no_check:
            p3 = os.path.join(args.datadir, doc4["source_evaluated"])
            doc3 = load_json(p3) if os.path.exists(p3) else None
            rep = check_schema4(doc4, doc1, doc3)
            print_report(rep, "Schema 4 consistency")
            ok = ok and rep["passed"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

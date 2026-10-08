"""
I07: Schema 4 (coboundary structure) for C(n+1).

Coboundary of an odd linear map f: g -> g (docs/math/C_coboundary_definition.md):
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)} - (-1)^{(p(X)+1) p(Y)} [Y, f(X)} - f([X,Y})

The reference map f stored in Layer 4 is the *canonical* odd map induced by the oscillator change of
variables that removes the deformation:
    a_1^sigma  ->  a_1^sigma + kappa * S^sigma,
    S^sigma = sum_l ( gb_{sigma,l,-} b_l^+  -  gb_{sigma,l,+} b_l^- ),
which satisfies [b_k^s, a_1^sigma + kappa S^sigma] = 0 in the deformed algebra.
For every basis element X(a,b):  X(a + kappa S, b) = X(a,b) + kappa f(X)   (kappa^2 = 0),
and f(X) is decomposed in the Layer 1 basis (constant terms dropped and recorded).

Outputs:
    data/C_{n}_coboundary.json                 symbolic (linear forms in gb)
    data/C_{n}_coboundary_{profile}.json       numeric, for every profile of C_evaluate.PROFILES

Usage:  python src/C_coboundary.py [n ...]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from fractions import Fraction
from typing import Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_evaluate import PROFILES, profile_values  # noqa: E402
from C_gamma import compute_gamma  # noqa: E402
from C_generators import DATA_DIR, algebra_block, build_basis, parity_of, pbw_order, realization_words  # noqa: E402
from oscillator import Decomposer, Element, LinPoly  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402

GVec = Dict[str, LinPoly]
OddMap = Dict[str, GVec]  # f[Z_j] = {Z_i: phi_ij}


# --------------------------------------------------------------------------- #
# Generic coboundary operator on the Layer 1 bracket table
# --------------------------------------------------------------------------- #
def _bracket_lin(bt: BracketTable, u: GVec, v: GVec) -> GVec:
    out: GVec = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, cz in bt.bracket_basis(x, y).items():
                out[z] = out.get(z, LinPoly()) + cx * cy * cz
    return {k: v for k, v in out.items() if not v.is_zero()}


def _apply(f: OddMap, u: GVec) -> GVec:
    out: GVec = {}
    for x, cx in u.items():
        for z, cz in f.get(x, {}).items():
            out[z] = out.get(z, LinPoly()) + cx * cz
    return {k: v for k, v in out.items() if not v.is_zero()}


def _vadd(u: GVec, v: GVec, c=1) -> GVec:
    out = dict(u)
    for k, val in v.items():
        out[k] = out.get(k, LinPoly()) + val * c
    return {k: v for k, v in out.items() if not v.is_zero()}


def delta_f_pair(bt: BracketTable, f: OddMap, x: str, y: str) -> GVec:
    p = bt.parity
    one = lambda l: {l: LinPoly(1)}  # noqa: E731
    t = _bracket_lin(bt, one(x), f.get(y, {}))
    t = {k: v * ((-1) ** p[x]) for k, v in t.items()}
    t = _vadd(t, _bracket_lin(bt, one(y), f.get(x, {})), -((-1) ** ((p[x] + 1) * p[y])))
    t = _vadd(t, _apply(f, {z: LinPoly(c) for z, c in bt.bracket_basis(x, y).items()}), -1)
    return t


def coboundary(bt: BracketTable, f: OddMap) -> Dict[Tuple[str, str], GVec]:
    out = {}
    for x in bt.order:
        for y in bt.order:
            d = delta_f_pair(bt, f, x, y)
            if d:
                out[(x, y)] = d
    return out


# --------------------------------------------------------------------------- #
# Canonical odd map f from the oscillator change of variables
# --------------------------------------------------------------------------- #
def canonical_f(n: int):
    """Return (f: OddMap, dropped_constants: {X: LinPoly}, shift description)."""
    alg, basis = build_basis(n, deformed=False)
    dec = Decomposer(alg, basis)
    kappa = Element.word(alg, "kappa")
    shift = {}
    for sigma in ("p", "m"):
        S = Element(alg)
        for l in range(1, n + 1):
            S = S + Element.word(alg, f"b_{l}_p", coeff=LinPoly.symbol(f"gb_a_1_{sigma}_b_{l}_m"))
            S = S - Element.word(alg, f"b_{l}_m", coeff=LinPoly.symbol(f"gb_a_1_{sigma}_b_{l}_p"))
        shift[sigma] = S
    letter_elem = {x: Element.word(alg, x) for x in alg.letters}
    primed = dict(letter_elem)
    for sigma in ("p", "m"):
        primed[f"a_1_{sigma}"] = letter_elem[f"a_1_{sigma}"] + kappa * shift[sigma]

    f: OddMap = {}
    consts = {}
    for lab in pbw_order(n):
        words, _, _ = realization_words(n, lab)
        new = Element(alg)
        for w, c in words:
            term = Element.scalar(alg, c)
            for letter in w:
                term = term * primed[letter]
            new = new + term
        diff = new - basis[lab]
        base, kap = diff.split_kappa()
        if not base.is_zero():
            raise RuntimeError("unexpected kappa-free difference")
        coeffs, const = dec.decompose(kap)
        if coeffs:
            f[lab] = coeffs
        if not const.is_zero():
            consts[lab] = const
    return f, consts, shift


# --------------------------------------------------------------------------- #
# Checks and JSON
# --------------------------------------------------------------------------- #
def check_layer4(n: int, bt: BracketTable, f: OddMap, df, verbose=True) -> dict:
    labels = set(bt.order)
    rep = {"f_parity_reversing": True, "df_parity_rule": True, "labels_in_basis": True,
           "gamma_plus_delta_f_zero": True, "mismatches": []}
    for zj, vec in f.items():
        for zi in vec:
            if zi not in labels:
                rep["labels_in_basis"] = False
            if parity_of(zi) == parity_of(zj):
                rep["f_parity_reversing"] = False
    for (x, y), vec in df.items():
        for z in vec:
            if z not in labels:
                rep["labels_in_basis"] = False
            if parity_of(z) != (parity_of(x) + parity_of(y) + 1) % 2:
                rep["df_parity_rule"] = False
    gamma, _, _ = compute_gamma(n)
    for x in bt.order:
        for y in bt.order:
            s = _vadd(gamma.get((x, y), {}), df.get((x, y), {}), 1)
            if s:
                rep["gamma_plus_delta_f_zero"] = False
                rep["mismatches"].append((x, y, {k: v.expr() for k, v in s.items()}))
    rep["pass"] = all(rep[k] for k in ("f_parity_reversing", "df_parity_rule", "labels_in_basis", "gamma_plus_delta_f_zero"))
    if verbose:
        print(f"[C({n+1}), n={n}] canonical f: {sum(len(v) for v in f.values())} non-zero phi_ij on {len(f)} generators; "
              f"delta f: {len(df)} pairs, {sum(len(v) for v in df.values())} coefficients")
        print(f"  f parity-reversing={rep['f_parity_reversing']}  delta f parity rule={rep['df_parity_rule']}  "
              f"labels in Layer 1 basis={rep['labels_in_basis']}")
        print(f"  gamma + delta f == 0 on all pairs: {rep['gamma_plus_delta_f_zero']} (mismatches={len(rep['mismatches'])})")
        print(f"  RESULT: {'PASS' if rep['pass'] else 'FAIL'}")
    return rep


def _vec_json(vec: GVec, idx, values=None):
    out = []
    for z, c in sorted(vec.items(), key=lambda kv: idx[kv[0]]):
        if values is None:
            out.append((z, c.to_json(), c.expr()))
        else:
            v = c.substitute(values).scalar_value()
            if v != 0:
                out.append((z, str(v), str(v)))
    return out


def build_coboundary_json(n: int, profile: str | None = None):
    bt = BracketTable.load(n)
    f, consts, shift = canonical_f(n)
    df = coboundary(bt, f)
    rep = check_layer4(n, bt, f, df, verbose=False)
    order = bt.order
    idx = {l: i for i, l in enumerate(order)}
    values = profile_values(n, profile) if profile else None

    phi = []
    for zj in order:
        for zi, c, e in _vec_json(f.get(zj, {}), idx, values):
            phi.append({"j": zj, "i": zi, "coeff": c, "expr": e})
    df_list = []
    for x in order:
        for y in order:
            for z, c, e in _vec_json(df.get((x, y), {}), idx, values):
                df_list.append({"X": x, "Y": y, "Z": z, "coeff": c, "expr": e})
    const_list = [{"X": x, "Z": "K", "coeff": c.to_json(), "expr": c.expr()} for x, c in consts.items()]
    if values is not None:
        const_list = [{"X": x, "Z": "K", "coeff": str(c.substitute(values).scalar_value())} for x, c in consts.items()
                      if c.substitute(values).scalar_value() != 0]

    doc = {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {k: algebra_block(n)[k] for k in ("family", "m", "n", "cartan_type")},
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "coboundary_definition": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)} - (-1)^{(p(X)+1)p(Y)}[Y,f(X)} - f([X,Y})",
        "odd_map_f": {
            "description": ("Canonical odd map induced by the oscillator change of variables "
                            "a_1^sigma -> a_1^sigma + kappa*S^sigma, S^sigma = sum_l (gb_{sigma,l,-} b_l^+ - gb_{sigma,l,+} b_l^-); "
                            "X(a + kappa S, b) = X(a,b) + kappa f(X). Constant terms of f(X) are dropped (listed in dropped_constant_terms)."),
            "parity": "odd (parity-reversing)",
            "parameterization": "f(Z_j) = sum_i phi_ij Z_i ; records give (j, i, phi_ij)",
            "shift_S": {sigma: [{"words": list(w), "coeff": c.to_json(), "expr": c.expr()} for w, c in shift[sigma].terms.items()]
                        for sigma in ("p", "m")},
            "phi": phi,
            "dropped_constant_terms": const_list,
        },
        "delta_f": df_list,
        "consistency": {
            "f_parity_reversing": rep["f_parity_reversing"],
            "delta_f_parity_rule": rep["df_parity_rule"],
            "labels_in_layer1_basis": rep["labels_in_basis"],
            "gamma_plus_delta_f_vanishes": rep["gamma_plus_delta_f_zero"],
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": date.today().isoformat(),
                     "definition": "docs/math/C_coboundary_definition.md"},
    }
    if profile:
        doc["gb_profile"] = {"name": profile, "values": {k: str(v) for k, v in values.items()}}
    return doc, rep


def write_coboundary(n: int, profile: str | None = None, data_dir: str = DATA_DIR):
    doc, rep = build_coboundary_json(n, profile)
    name = f"C_{n}_coboundary.json" if profile is None else f"C_{n}_coboundary_{profile}.json"
    path = os.path.join(data_dir, name)
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path, rep


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        bt = BracketTable.load(n)
        f, consts, _ = canonical_f(n)
        rep = check_layer4(n, bt, f, coboundary(bt, f))
        ok &= rep["pass"]
        for m in rep["mismatches"][:5]:
            print("   mismatch:", m)
        path, _ = write_coboundary(n)
        print(f"  wrote {os.path.basename(path)}", end="")
        for prof in PROFILES:
            path, _ = write_coboundary(n, prof)
            print(f", {os.path.basename(path)}", end="")
        print()
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)

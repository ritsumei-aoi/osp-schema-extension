"""Issue I07: Schema 4 (coboundary structure) for C(n+1).

Odd linear map f: g -> g (+ C K), f(Z_j) = sum_i phi_ij Z_i, and its coboundary
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])
(docs/math/C_coboundary_definition.md).  All brackets are the Schema 1 brackets
([X, K] = 0).

Two objects are produced per n:
  * the symbolic coboundary of a *generic* odd map (unknowns phi[Z_i][Z_j]);
  * a *representative* f, obtained from the oscillator-level change of variables
        a_1^sigma  ->  a_1^sigma + sum_{j,s} d_{sigma,j,s} b_j^s kappa,
        d_{sigma,j,+} = gb_{sigma,j,-},  d_{sigma,j,-} = -gb_{sigma,j,+},
    which removes the deformation from the oscillator relations.  Writing the
    transformed generator as X + kappa * l(X), the representative is f = -l
    (so that delta f = gamma; this is verified against Schema 3).

Usage: python3 src/C_coboundary.py [n ...]  -> data/C_{n}_coboundary.json
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import (DATA_DIR, LieSuperalgebra, LinForm, frac_str, lf_add, lf_eval,  # noqa: E402
                      lf_json, lf_str)
from C_evaluate import gb_profiles, load_evaluated  # noqa: E402
from C_generators import (REFERENCES, algebra_block, central_elements_block,  # noqa: E402
                          make_decomposer, pbw_order, realization_words)
from oscillator_algebra import Element, OscillatorAlgebra, gb_name  # noqa: E402

# f : source label -> {target label: LinForm}
FMap = Dict[str, Dict[str, LinForm]]
# coboundary table : (X,Y) -> {Z: LinForm}
CobTable = Dict[Tuple[str, str], Dict[str, LinForm]]


def phi_name(target: str, source: str) -> str:
    return f"phi[{target}][{source}]"


# ---------------------------------------------------------------------------
# Generic parameterization of an odd linear map
# ---------------------------------------------------------------------------
def generic_f(g: LieSuperalgebra, allow_K: bool) -> Tuple[FMap, List[str]]:
    """Odd map with one unknown per parity-reversing pair (target, source).

    If allow_K, f(odd source) may contain K (even) as a target.
    """
    f: FMap = {}
    unknowns: List[str] = []
    targets = list(g.labels) + (["K"] if allow_K else [])
    for src in g.labels:
        f[src] = {}
        for tgt in targets:
            if g.parity[tgt] != g.parity[src]:
                name = phi_name(tgt, src)
                f[src][tgt] = {name: Fraction(1)}
                unknowns.append(name)
    return f, unknowns


# ---------------------------------------------------------------------------
# Coboundary operator
# ---------------------------------------------------------------------------
def coboundary(g: LieSuperalgebra, f: FMap, pairs=None) -> CobTable:
    """delta f on the given ordered pairs (default: all ordered pairs of basis elements)."""
    p = g.parity

    def f_of(v: Dict[str, Fraction]) -> Dict[str, LinForm]:
        out: Dict[str, LinForm] = {}
        for W, c in v.items():
            for T, lf in f.get(W, {}).items():
                out[T] = lf_add(out.get(T, {}), lf, c)
        return out

    def bracket_with_f(A: str, fv: Dict[str, LinForm]) -> Dict[str, LinForm]:
        """[A, sum_T fv[T] T]  (fv[T] linear forms)."""
        out: Dict[str, LinForm] = {}
        for T, lf in fv.items():
            for Z, c in g.bracket(A, T).items():
                out[Z] = lf_add(out.get(Z, {}), lf, c)
        return out

    if pairs is None:
        pairs = [(X, Y) for X in g.labels for Y in g.labels]
    table: CobTable = {}
    fcache = {lab: f.get(lab, {}) for lab in g.labels}
    for X, Y in pairs:
        s1 = Fraction(-1 if p[X] else 1)
        s2 = Fraction(-1 if ((p[X] + 1) * p[Y]) % 2 else 1)
        total: Dict[str, LinForm] = {}
        for Z, lf in bracket_with_f(X, fcache[Y]).items():
            total[Z] = lf_add(total.get(Z, {}), lf, s1)
        for Z, lf in bracket_with_f(Y, fcache[X]).items():
            total[Z] = lf_add(total.get(Z, {}), lf, -s2)
        for Z, lf in f_of(g.bracket(X, Y)).items():
            total[Z] = lf_add(total.get(Z, {}), lf, Fraction(-1))
        total = {Z: lf for Z, lf in total.items() if lf}
        if total:
            table[(X, Y)] = total
    return table


# ---------------------------------------------------------------------------
# Representative f from the oscillator-level change of variables
# ---------------------------------------------------------------------------
def shift_map_symbolic(n: int) -> FMap:
    """l(X) with  X(a') = X(a) + kappa * l(X),  a'^sigma = a^sigma + sum d b kappa.

    Returned as f_rep = -l, with coefficients linear forms in the gb parameters;
    targets may include K.
    """
    alg = OscillatorAlgebra(n, deformed=True)
    # substituted fermionic oscillators
    subst: Dict[str, Element] = {}
    for sigma in ("p", "m"):
        el = Element.word(alg, f"a_1_{sigma}")
        for j in range(1, n + 1):
            # d_{sigma,j,+} = gb_{sigma,j,-}   (coefficient of b_j^+ kappa)
            el = el + Element.word(alg, gb_name(sigma, j, "m"), f"b_{j}_p", "kappa", coeff=1)
            # d_{sigma,j,-} = -gb_{sigma,j,+}  (coefficient of b_j^- kappa)
            el = el + Element.word(alg, gb_name(sigma, j, "p"), f"b_{j}_m", "kappa", coeff=-1)
        subst[f"a_1_{sigma}"] = el
    from C_generators import build_elements
    elements = build_elements(OscillatorAlgebra(n, deformed=True))
    dec = make_decomposer(alg, elements, with_K=True)
    f: FMap = {}
    for label in pbw_order(n):
        words, _, _ = realization_words(label, n)
        total = Element(alg)
        for w, c in words:
            term = Element.scalar(alg, c)
            for sym in w:
                term = term * (subst[sym] if sym in subst else Element.word(alg, sym))
            total = total + term
        x0, kparts = total.split_kappa()
        assert x0 == elements[label], label
        entry: Dict[str, LinForm] = {}
        for param, el in kparts.items():
            assert param != ""
            for T, c in dec.decompose(el).items():
                entry[T] = lf_add(entry.get(T, {}), {param: -c})  # f = -l
        f[label] = {T: lf for T, lf in entry.items() if lf}
    return f


def evaluate_f(f_sym: FMap, values: Dict[str, Fraction]) -> FMap:
    out: FMap = {}
    for src, targets in f_sym.items():
        ev = {T: lf_eval(lf, values) for T, lf in targets.items()}
        out[src] = {T: {"": c} for T, c in ev.items() if c != 0}
    return out


def numeric(table: CobTable) -> Dict[Tuple[str, str], Dict[str, Fraction]]:
    out = {}
    for k, e in table.items():
        ev = {Z: lf.get("", Fraction(0)) for Z, lf in e.items()}
        ev = {Z: c for Z, c in ev.items() if c != 0}
        if ev:
            out[k] = ev
    return out


# ---------------------------------------------------------------------------
# Schema 4 document
# ---------------------------------------------------------------------------
def build_schema4(n: int, profile: str = "all_plus") -> Tuple[dict, dict]:
    g = LieSuperalgebra.load(n)
    labels = g.labels
    order = {lab: i for i, lab in enumerate(labels + ["K"])}
    # generic symbolic coboundary (pairs with index(X) <= index(Y))
    f_gen, unknowns = generic_f(g, allow_K=True)
    pairs = [(X, Y) for i, X in enumerate(labels) for Y in labels[i:]]
    cob_sym = coboundary(g, f_gen, pairs)
    sym_entries = []
    for X, Y in pairs:
        for Z in sorted(cob_sym.get((X, Y), {}), key=lambda z: order[z]):
            lf = cob_sym[(X, Y)][Z]
            sym_entries.append({"X": X, "Y": Y, "Z": Z, "coeff": lf_json(lf), "expr": lf_str(lf)})
    # representative f
    f_sym = shift_map_symbolic(n)
    values = gb_profiles(n)[profile]
    f_rep = evaluate_f(f_sym, values)
    cob_rep = numeric(coboundary(g, f_rep))
    rep_entries = []
    for X in labels:
        for Y in labels:
            for Z in sorted(cob_rep.get((X, Y), {}), key=lambda z: order[z]):
                rep_entries.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(cob_rep[(X, Y)][Z])})
    f_map = [{"source": src, "target": T, "coeff": frac_str(lf[""])}
             for src in labels for T, lf in sorted(f_rep[src].items(), key=lambda kv: order[kv[0]])]
    f_map_sym = [{"source": src, "target": T, "coeff": lf_json(lf), "expr": lf_str(lf)}
                 for src in labels for T, lf in sorted(f_sym[src].items(), key=lambda kv: order[kv[0]])]
    # comparison with Layer 3
    _, gamma_eval = load_evaluated(n, profile)
    matches = cob_rep == gamma_eval
    doc = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": algebra_block(n),
        "central_elements": central_elements_block(),
        "basis_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "evaluated_ref": os.path.basename(__import__("C_evaluate").evaluated_path(n, profile)),
        "coboundary_definition": "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])",
        "f_parameterization": {
            "description": ("odd linear map f(Z_j) = sum_i phi_ij Z_i; unknown phi[<Z_i>][<Z_j>] is the coefficient "
                            "of Z_i in f(Z_j); only parity-reversing pairs are unknowns"),
            "target": "g + C K (K allowed as a target only for odd sources; f(K) = 0)",
            "unknowns": unknowns,
            "count": len(unknowns),
            "count_without_K": sum(1 for u in unknowns if not u.startswith("phi[K]")),
        },
        "coboundary_symbolic_convention": {
            "pairs": "ordered pairs (X,Y) with index(X) <= index(Y) in pbw_order; the rest follow by super-antisymmetry",
            "coeff_encoding": "linear form {phi unknown: rational}",
        },
        "coboundary_symbolic": sym_entries,
        "coboundary_symbolic_count": len(sym_entries),
        "representative_f": {
            "description": ("f = -l where X(a') = X(a) + kappa l(X) under the oscillator change of variables "
                            "a_1^s -> a_1^s + sum_{j,t} d_{s,j,t} b_j^t kappa with d_{s,j,+} = gb_{s,j,-}, "
                            "d_{s,j,-} = -gb_{s,j,+} (which undoes the deformed relation [b_j^t, a_1^s] = -gb kappa). "
                            "Targets include K for odd sources."),
            "gb_profile": profile,
            "gb_values": {k: frac_str(v) for k, v in values.items()},
            "map": f_map,
            "map_symbolic_in_gb": f_map_sym,
            "K_components": [m for m in f_map if m["target"] == "K"],
        },
        "coboundary_evaluated": rep_entries,
        "coboundary_evaluated_count": len(rep_entries),
        "comparison_with_layer3": {
            "gamma_file": os.path.basename(__import__("C_evaluate").evaluated_path(n, profile)),
            "delta_f_equals_gamma": matches,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": _dt.date.today().isoformat(),
            "notation": "handover/notation.md",
            "references": REFERENCES,
        },
    }
    aux = {"g": g, "f_sym": f_sym, "f_rep": f_rep, "cob_rep": cob_rep, "gamma_eval": gamma_eval,
           "cob_sym": cob_sym, "unknowns": unknowns}
    return doc, aux


def write_schema4(n: int, data_dir: str = DATA_DIR) -> Tuple[str, dict]:
    doc, aux = build_schema4(n)
    path = os.path.join(data_dir, f"C_{n}_coboundary.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path, aux


def load_coboundary(n: int, data_dir: str = DATA_DIR) -> dict:
    with open(os.path.join(data_dir, f"C_{n}_coboundary.json")) as fh:
        return json.load(fh)


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok_all = True
    for n in ns:
        path, aux = write_schema4(n)
        doc = load_coboundary(n)
        g = aux["g"]
        # consistency with Layer 1 basis: every label used is a basis label or K
        labs = set(g.labels) | {"K"}
        ok_labels = all(e["X"] in g.labels and e["Y"] in g.labels and e["Z"] in labs
                        for e in doc["coboundary_symbolic"] + doc["coboundary_evaluated"])
        ok_labels &= all(m["source"] in g.labels and m["target"] in labs for m in doc["representative_f"]["map"])
        # parity: f reverses parity
        ok_par = all(g.parity[m["source"]] != g.parity[m["target"]] for m in doc["representative_f"]["map"])
        match = doc["comparison_with_layer3"]["delta_f_equals_gamma"]
        nK = len(doc["representative_f"]["K_components"])
        print(f"C({n+1}) {os.path.basename(path)}: unknowns={doc['f_parameterization']['count']} "
              f"(without K: {doc['f_parameterization']['count_without_K']}), "
              f"symbolic entries={doc['coboundary_symbolic_count']}, "
              f"evaluated entries={doc['coboundary_evaluated_count']}, f_rep K-components={nK}")
        print(f"   labels in Layer 1 basis: {'PASS' if ok_labels else 'FAIL'};  f_rep parity-reversing: "
              f"{'PASS' if ok_par else 'FAIL'};  delta(f_rep) == Layer 3 gamma (all_plus): {'PASS' if match else 'FAIL'}")
        ok_all &= ok_labels and ok_par and match
    print("SUMMARY:", "ALL PASS" if ok_all else "FAILURES")
    sys.exit(0 if ok_all else 1)

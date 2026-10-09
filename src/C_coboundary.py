"""Schema 4 (coboundary structure) for C(n+1)  (Issue I07).

Odd linear map  f(Z_j) = sum_i phi_ij Z_i  (p(Z_i) = p(Z_j) + 1; Z_i may be K for odd Z_j)
and its coboundary (docs/math/C_coboundary_definition.md):

    (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)} - (-1)^{(p(X)+1) p(Y)} [Y, f(X)} - f([X,Y}).

Everything is computed from the Schema 1 structure constants (Layer 1 basis), never from
the oscillator realization, except for the construction of the *candidate map* f_shift,
which is read off from the oscillator shift
    b_k^s -> b_k^s - kappa * sum_tau gb_{a_1^{-tau}, b_k^s} a_1^tau
(the change of oscillator variables that undoes the deformed relation).

Outputs data/C_{n}_coboundary.json containing
  * elementary_coboundaries: δ(f_ij) for every elementary odd map (matrix of δ),
  * candidate_map: f_shift (linear in gb) and δ f_shift (linear in gb).

Usage: python3 src/C_coboundary.py [--datadir data] [n ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import Decomposer, OscillatorAlgebra, algebra_block, build_basis, fr, metadata_block  # noqa: E402
from C_gamma import gb_labels, linear_form_str  # noqa: E402


# ---------------------------------------------------------------------- Layer 1 tables

def load_structure(path):
    with open(path) as fh:
        d = json.load(fh)
    order = d["basis"]["pbw_order"]
    par = dict(d["parity"])
    par["K"] = 0
    sc = {(X, Y): {} for X in order for Y in order}
    for e in d["structure_constants"]:
        sc[(e["X"], e["Y"])][e["Z"]] = Fraction(e["coeff"])
    return d, order, par, sc


def bracket_vec(sc, X, vec: dict) -> dict:
    """[X, vec} for vec = {label: coeff}; K components are central and drop out."""
    out: dict = {}
    for Y, cy in vec.items():
        if Y == "K":
            continue
        for Z, cz in sc[(X, Y)].items():
            out[Z] = out.get(Z, Fraction(0)) + cy * cz
    return {k: v for k, v in out.items() if v != 0}


def apply_f(f: dict, vec: dict) -> dict:
    """f(vec) for f = {source: {target: coeff}}."""
    out: dict = {}
    for Y, cy in vec.items():
        for Z, cz in f.get(Y, {}).items():
            out[Z] = out.get(Z, Fraction(0)) + cy * cz
    return {k: v for k, v in out.items() if v != 0}


def coboundary(sc, par, f: dict, X: str, Y: str) -> dict:
    """(δf)(X,Y) as {label: coeff} (label may be K)."""
    sX = -1 if par[X] else 1
    sYX = -1 if ((par[X] + 1) * par[Y]) % 2 else 1
    out: dict = {}
    for Z, c in bracket_vec(sc, X, f.get(Y, {})).items():
        out[Z] = out.get(Z, Fraction(0)) + sX * c
    for Z, c in bracket_vec(sc, Y, f.get(X, {})).items():
        out[Z] = out.get(Z, Fraction(0)) - sYX * c
    for Z, c in apply_f(f, sc[(X, Y)]).items():
        out[Z] = out.get(Z, Fraction(0)) - c
    return {k: v for k, v in out.items() if v != 0}


def coboundary_table(sc, par, order, f: dict, all_pairs=True) -> dict:
    """{(X,Y): {Z: coeff}} for all ordered pairs (or index(X) <= index(Y))."""
    out = {}
    for i, X in enumerate(order):
        for j, Y in enumerate(order):
            if not all_pairs and j < i:
                continue
            d = coboundary(sc, par, f, X, Y)
            if d:
                out[(X, Y)] = d
    return out


# ---------------------------------------------------------------------- elementary odd maps

def phi_labels(order, par, include_K=True):
    """All (target, source) pairs of elementary odd maps f: source -> target."""
    labs = []
    for src in order:
        for tgt in order:
            if par[tgt] != par[src]:
                labs.append((tgt, src))
        if include_K and par[src] == 1:
            labs.append(("K", src))
    return labs


def phi_name(tgt, src):
    return f"phi[{tgt}][{src}]"


# ---------------------------------------------------------------------- candidate map f_shift

def candidate_map(n: int, order, par) -> dict:
    """f_shift as {source: {target: {gb_label: coeff}}}, computed per gb parameter from the
    oscillator shift  b_k^s -> b_k^s - kappa * sum_tau gb_{a_1^{-tau}, b_k^s} a_1^tau."""
    odd, even, real, roots = build_basis(n)
    alg = OscillatorAlgebra(n)  # undeformed algebra with kappa available
    elements = {lab: alg.element(terms) for lab, terms in real.items()}
    dec = Decomposer(alg, order, elements, include_K=True)
    f: dict = {}
    for lab, (sigma, k, s) in gb_labels(n):
        # shift for this single parameter: b_k^s -> b_k^s - kappa * a_1^{-sigma}
        tau = "m" if sigma == "p" else "p"
        shifted = {
            f"b_{k}_{s}": alg.add(alg.element([([f"b_{k}_{s}"], 1)]), alg.element([(["kappa", f"a_1_{tau}"], 1)]), Fraction(-1))
        }
        for X in order:
            total: dict = {}
            for words, c in real[X]:
                prod = {(): Fraction(c)}
                for w in words:
                    factor = shifted.get(w, alg.element([([w], 1)]))
                    prod = alg.multiply(prod, factor)
                total = alg.add(total, prod)
            A0, A1 = alg.split_kappa(total)
            assert A0 == elements[X]
            for Z, c in dec.decompose(A1).items():
                f.setdefault(X, {}).setdefault(Z, {})[lab] = c
    return f


def evaluate_linear(fl: dict, values: dict) -> Fraction:
    return sum(Fraction(c) * values[l] for l, c in fl.items())


def restrict_f(f_lin: dict, lab: str) -> dict:
    """Pick the coefficient of one gb parameter: {source: {target: coeff}}."""
    out = {}
    for src, tg in f_lin.items():
        for tgt, fl in tg.items():
            if lab in fl:
                out.setdefault(src, {})[tgt] = fl[lab]
    return out


# ---------------------------------------------------------------------- Schema 4

def build_schema4(n: int, datadir: str, with_elementary=True):
    s1, order, par, sc = load_structure(os.path.join(datadir, f"C_{n}_structure.json"))
    with open(os.path.join(datadir, f"C_{n}_gamma.json")) as fh:
        s2 = json.load(fh)
    labels = gb_labels(n)
    # --- elementary coboundaries
    phis = phi_labels(order, par, include_K=True)
    elem_entries = []
    if with_elementary:
        for tgt, src in phis:
            f = {src: {tgt: Fraction(1)}}
            for (X, Y), d in coboundary_table(sc, par, order, f, all_pairs=False).items():
                for Z in order + ["K"]:
                    if Z in d:
                        elem_entries.append({"phi": phi_name(tgt, src), "X": X, "Y": Y, "Z": Z, "coeff": fr(d[Z])})
    # --- candidate map and its coboundary (linear in gb)
    f_lin = candidate_map(n, order, par)
    delta_lin: dict = {}
    for lab, _ in labels:
        f = restrict_f(f_lin, lab)
        for (X, Y), d in coboundary_table(sc, par, order, f, all_pairs=True).items():
            for Z, c in d.items():
                delta_lin.setdefault((X, Y), {}).setdefault(Z, {})[lab] = c
    # --- compare with Schema 2 gamma (exact, including K components)
    gamma = {}
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    mismatches = [(k, gamma.get(k), delta_lin.get(k)) for k in set(gamma) | set(delta_lin) if gamma.get(k) != delta_lin.get(k)]
    f_entries = []
    for src in order:
        for tgt in order + ["K"]:
            if tgt in f_lin.get(src, {}):
                coeff = {lab: fr(f_lin[src][tgt][lab]) for lab, _ in labels if lab in f_lin[src][tgt]}
                f_entries.append({"source": src, "target": tgt, "coeff": coeff, "linear_form": linear_form_str(coeff)})
    d_entries = []
    for X in order:
        for Y in order:
            for Z in order + ["K"]:
                if Z in delta_lin.get((X, Y), {}):
                    coeff = {lab: fr(delta_lin[(X, Y)][Z][lab]) for lab, _ in labels if lab in delta_lin[(X, Y)][Z]}
                    d_entries.append({"X": X, "Y": Y, "Z": Z, "coeff": coeff, "linear_form": linear_form_str(coeff)})
    schema = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": algebra_block(n),
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "coboundary_formula": "(δf)(X,Y) = (-1)^{p(X)} [X,f(Y)} - (-1)^{(p(X)+1)p(Y)} [Y,f(X)} - f([X,Y})",
        "odd_map_parameterization": {
            "description": "f(Z_j) = Σ_i φ_ij Z_i with p(Z_i) = p(Z_j)+1; Z_i = K (scalar) allowed when Z_j is odd. phi[Z_i][Z_j] is the elementary map Z_j -> Z_i.",
            "phi_labels": [phi_name(t, s) for t, s in phis],
            "count": len(phis),
            "count_without_K_targets": sum(1 for t, s in phis if t != "K"),
        },
        "elementary_coboundaries": {
            "description": "δ(f_ij) for each elementary odd map; ordered pairs stored with index(X) <= index(Y) in pbw_order (the rest follows from graded antisymmetry)",
            "included": bool(with_elementary),
            "table": elem_entries,
        },
        "candidate_map": {
            "description": "f_shift induced by the oscillator shift b_k^s -> b_k^s - kappa Σ_τ gb_{a_1^{-τ}, b_k^s} a_1^τ; f_shift(X) = kappa-part of X(b_shifted, a). Coefficients are linear in gb.",
            "f": f_entries,
            "delta_f": d_entries,
            "delta_f_equals_schema2_gamma": not mismatches,
            "delta_f_equals_schema2_gamma_modulo_K": not [m for m in mismatches if any(Z != "K" for Z in (set(m[1] or {}) | set(m[2] or {})))],
            "K_targets_of_f": [e for e in f_entries if e["target"] == "K"],
        },
        "metadata": metadata_block("src/C_coboundary.py"),
    }
    return schema, mismatches


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ns", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    args = ap.parse_args(argv)
    for n in args.ns:
        schema, mismatches = build_schema4(n, args.datadir)
        path = os.path.join(args.datadir, f"C_{n}_coboundary.json")
        with open(path, "w") as fh:
            json.dump(schema, fh, indent=1, ensure_ascii=False)
        cm = schema["candidate_map"]
        print(f"C({n+1}): {schema['odd_map_parameterization']['count']} elementary odd maps "
              f"({schema['odd_map_parameterization']['count_without_K_targets']} without K targets), "
              f"{len(schema['elementary_coboundaries']['table'])} elementary coboundary entries; "
              f"candidate f_shift: {len(cm['f'])} entries ({len(cm['K_targets_of_f'])} with target K), "
              f"delta f_shift: {len(cm['delta_f'])} entries; "
              f"delta f_shift == gamma: {cm['delta_f_equals_schema2_gamma']} "
              f"(mod K: {cm['delta_f_equals_schema2_gamma_modulo_K']}, {len(mismatches)} mismatching pairs) "
              f"-> {os.path.relpath(path)}")


if __name__ == "__main__":
    main()

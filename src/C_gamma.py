"""Schema 2: inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)  (Issue I05).

Deformed oscillator relation (C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa,     kappa odd, super-central, kappa^2 = 0.

For basis elements X, Y the deformed graded bracket computed in the enveloping algebra is
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),
and gamma(X, Y) is decomposed in the basis of g~ = g (+) C K (K = 1, central identity).
The coefficients gamma_{XY}^{Z} are linear forms in the 4n parameters gb.

Usage:
    python src/C_gamma.py          # writes data/C_{n}_gamma.json for n = 1, 2, 3
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_generators as G  # noqa: E402
from oscillator_algebra import OscillatorAlgebra, gb_label, gb_labels  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def gamma_path(n: int) -> str:
    return os.path.join(DATA_DIR, f"C_{n}_gamma.json")


def linear_form(expr: sp.Expr, symbols: List[sp.Symbol]) -> Dict[str, str]:
    """Write a sympy expression linear in ``symbols`` as {label: rational string}."""
    expr = sp.expand(expr)
    poly = sp.Poly(expr, *symbols)
    out = {}
    for monom, c in poly.terms():
        if sum(monom) != 1:
            raise ValueError(f"gamma coefficient {expr} is not linear in gb")
        lab = symbols[monom.index(1)].name
        out[lab] = str(sp.Rational(c))
    return out


def compute_gamma(n: int):
    """Return (gamma_entries, kappa0_entries) for all ordered basis pairs.

    gamma_entries: list of {X, Y, Z, coeff(str), linear_form}
    kappa0_entries: list of {X, Y, Z, coeff} = the kappa^0 part (must equal Schema 1).
    """
    syms = [sp.Symbol(lab) for lab in gb_labels(n)]
    alg = OscillatorAlgebra(n, deformed=True, gb={s.name: s for s in syms})
    dec = G.Decomposer(n)
    elems = dec.elems
    gamma, k0 = [], []
    for X in dec.basis:
        for Y in dec.basis:
            br = alg.bracket(elems[X], elems[Y])
            part0, part1 = alg.split_kappa(br)
            for Z, c in dec.decompose(part0).items():
                assert not c.free_symbols, (X, Y, Z, c)
                k0.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
            for Z, c in dec.decompose(part1).items():
                gamma.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "linear_form": linear_form(c, syms)})
    return gamma, k0


def build_schema2(n: int) -> dict:
    gamma, k0 = compute_gamma(n)
    with open(G.structure_path(n)) as fh:
        s1 = json.load(fh)
    assert k0 == s1["structure_constants"], "kappa^0 part of the deformed bracket differs from Schema 1"
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    gb_rows = [[gb_label(sg, j, s) for j in range(1, n + 1) for s in "pm"] for sg in "pm"]
    n_K = sum(1 for e in gamma if e["Z"] == "K")
    return {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": s1["algebra"],
        "source_structure": os.path.basename(G.structure_path(n)),
        "central_elements": s1["central_elements"],
        "gb_matrix": {
            "description": "Deformation parameters gb_{a_1^sigma, b_j^s}; label gb_a1{sigma}_b{j}{s}",
            "shape": [2, 2 * n],
            "count": 4 * n,
            "rows": ["a_1_p", "a_1_m"],
            "cols": boson_labels,
            "labels": gb_rows,
            "parity": 1,
            "parity_note": ("Formal parity 1 as in C_inhomogeneous_definition.md; in the computation the gb are "
                            "commuting scalar parameters. With kappa odd this makes [b_j^s, a_1^sigma] = -gb kappa "
                            "parity-consistent (both sides odd)."),
        },
        "deformed_oscillator_relations": {
            "boson_fermion": "[b_j^s, a_1^sigma] = - gb_a1{sigma}_b{j}{s} * kappa   (sigma, s in {p, m})",
            "fermion_boson": "[a_1^sigma, b_j^s] = + gb_a1{sigma}_b{j}{s} * kappa",
            "unchanged": ["{a_1^-, a_1^+} = 1", "(a_1^±)^2 = 0", "[b_i^-, b_j^+] = δ_{ij}", "[b_i^±, b_j^±] = 0"],
            "kappa": "kappa^2 = 0, [kappa, X} = 0 for all X",
        },
        "inhomogeneous_deformation": {
            "description": "Deformed graded bracket [X,Y}_gamma = [X,Y}_0 + kappa * gamma(X,Y), computed in the "
                           "enveloping algebra of the deformed oscillators. gamma is an odd 2-cocycle with values "
                           "in g~ = g (+) C K; entries with Z = 'K' are the central-identity components.",
            "bracket": "[X, Y}_gamma = [X, Y}_0 + kappa * sum_Z gamma_{XY}^Z Z",
            "gamma_parity": "p(Z) = p(X) + p(Y) + 1 (mod 2)",
            "pair_convention": "All ordered pairs (X, Y) with non-zero gamma(X, Y) are listed.",
            "coefficient_format": "coeff: printable linear form in the gb symbols; linear_form: {gb_label: rational}",
            "gamma": gamma,
            "summary": {
                "nonzero_entries": len(gamma),
                "nonzero_pairs": len({(e["X"], e["Y"]) for e in gamma}),
                "entries_with_Z_K": n_K,
            },
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": _dt.date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Bakalov and Sullivan (2017), arXiv:1612.09400",
            ],
        },
    }


# ----------------------------------------------------------- evaluation helpers
def load_schema2(n: int) -> dict:
    with open(gamma_path(n)) as fh:
        return json.load(fh)


def evaluate_linear_form(lf: Dict[str, str], gb_values: Dict[str, Fraction]) -> Fraction:
    return sum((Fraction(c) * Fraction(gb_values[lab]) for lab, c in lf.items()), Fraction(0))


def gamma_table(schema2: dict, gb_values: Dict[str, Fraction]):
    """Evaluate gamma at concrete gb values: dict (X, Y) -> {Z: Fraction}."""
    tab = {}
    for e in schema2["inhomogeneous_deformation"]["gamma"]:
        c = evaluate_linear_form(e["linear_form"], gb_values)
        if c != 0:
            tab.setdefault((e["X"], e["Y"]), {})[e["Z"]] = c
    return tab


def kappa(label: str) -> str:
    return "kappa*" + label


def extended_algebra(n: int, gb_values: Dict[str, Fraction], schema1: dict = None, schema2: dict = None):
    """The Lie superalgebra L = g~ (+) kappa g~, g~ = g (+) C K, with the deformed bracket.

    [X, Y}        = [X, Y}_0 + kappa gamma(X, Y)
    [X, kappa Y}  = (-1)^{p(X)} kappa [X, Y}_0
    [kappa X, Y}  = kappa [X, Y}_0
    [kappa X, kappa Y} = 0,   K and kappa K are central.
    Returns (basis, parity, table) in the format of verify_C_structure.
    """
    from verify_C_structure import load_table  # local import to avoid a cycle at module load

    if schema1 is None:
        with open(G.structure_path(n)) as fh:
            schema1 = json.load(fh)
    if schema2 is None:
        schema2 = load_schema2(n)
    g_basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    par = dict(schema1["parity"])
    par["K"] = 0
    t0 = load_table(schema1["structure_constants"])
    gam = gamma_table(schema2, gb_values)
    gt_basis = g_basis + ["K"]
    basis = gt_basis + [kappa(g) for g in gt_basis]
    parity = {**{g: par[g] for g in gt_basis}, **{kappa(g): 1 - par[g] for g in gt_basis}}
    table = {}
    for X in g_basis:
        for Y in g_basis:
            d = {}
            for Z, c in t0.get((X, Y), {}).items():
                d[Z] = c
            for Z, c in gam.get((X, Y), {}).items():
                d[kappa(Z)] = d.get(kappa(Z), Fraction(0)) + c
            if d:
                table[(X, Y)] = d
            d1 = {kappa(Z): (-1) ** par[X] * c for Z, c in t0.get((X, Y), {}).items()}
            if d1:
                table[(X, kappa(Y))] = d1
            d2 = {kappa(Z): c for Z, c in t0.get((X, Y), {}).items()}
            if d2:
                table[(kappa(X), Y)] = d2
    return basis, parity, table


def write_schema2(n: int) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = gamma_path(n)
    with open(path, "w") as fh:
        json.dump(build_schema2(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_schema2(n)
        d = json.load(open(p))
        s = d["inhomogeneous_deformation"]["summary"]
        print(f"n={n}: wrote {os.path.relpath(p, ROOT)}  gamma entries={s['nonzero_entries']} "
              f"pairs={s['nonzero_pairs']}  K-entries={s['entries_with_Z_K']}")

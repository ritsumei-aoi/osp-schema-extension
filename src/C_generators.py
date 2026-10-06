"""C(n+1) = osp(2|2n) Schema 1 generator.

Produces structure constants in the JSON v5.0 schema specified in
``docs/json_schema_specification.md``.  Covers n = 1, 2, 3.
"""

from __future__ import annotations

import json
import os
from datetime import date
from fractions import Fraction
from typing import Dict, Tuple

from src.C_oscillator import (
    Poly,
    graded_bracket,
    mono,
    poly_add,
)


def build_basis(n: int) -> Tuple[list, list, Dict[str, Poly], Dict[str, int]]:
    """Return (even_labels, odd_labels, realizations, parities)."""
    even = [f"H_{j}" for j in range(1, n + 2)]
    even += [f"E_2del{k}_p" for k in range(1, n + 1)]
    even += [
        f"E_del{i}_del{j}_pp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    even += [f"E_2del{k}_m" for k in range(1, n + 1)]
    even += [
        f"E_del{i}_del{j}_mm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    even += [
        f"E_del{i}_del{j}_pm"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    even += [
        f"E_del{i}_del{j}_mp"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
    ]
    odd = []
    for k in range(1, n + 1):
        for ss in ("pp", "pm", "mp", "mm"):
            odd.append(f"E_eps1_del{k}_{ss}")

    reals: Dict[str, Poly] = {}
    pars: Dict[str, int] = {}

    # Cartan
    reals["H_1"] = poly_add(
        mono(["a_1_p", "a_1_m"]), mono(["b_1_p", "b_1_m"])
    )
    pars["H_1"] = 0
    for k in range(2, n + 1):
        reals[f"H_{k}"] = poly_add(
            mono([f"b_{k - 1}_p", f"b_{k - 1}_m"]),
            mono([f"b_{k}_p", f"b_{k}_m"]),
            Fraction(-1),
        )
        pars[f"H_{k}"] = 0
    reals[f"H_{n + 1}"] = poly_add(
        mono([f"b_{n}_p", f"b_{n}_m"], coeff=-1),
        {(): Fraction(-1, 2)},
    )
    pars[f"H_{n + 1}"] = 0

    for k in range(1, n + 1):
        reals[f"E_2del{k}_p"] = mono([f"b_{k}_p", f"b_{k}_p"])
        reals[f"E_2del{k}_m"] = mono([f"b_{k}_m", f"b_{k}_m"])
        pars[f"E_2del{k}_p"] = 0
        pars[f"E_2del{k}_m"] = 0
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            reals[f"E_del{i}_del{j}_pp"] = mono([f"b_{i}_p", f"b_{j}_p"])
            reals[f"E_del{i}_del{j}_mm"] = mono([f"b_{i}_m", f"b_{j}_m"])
            reals[f"E_del{i}_del{j}_pm"] = mono([f"b_{i}_p", f"b_{j}_m"])
            reals[f"E_del{i}_del{j}_mp"] = mono([f"b_{i}_m", f"b_{j}_p"])
            for ss in ("pp", "mm", "pm", "mp"):
                pars[f"E_del{i}_del{j}_{ss}"] = 0

    for k in range(1, n + 1):
        reals[f"E_eps1_del{k}_pp"] = mono(["a_1_p", f"b_{k}_p"])
        reals[f"E_eps1_del{k}_pm"] = mono(["a_1_p", f"b_{k}_m"])
        reals[f"E_eps1_del{k}_mp"] = mono(["a_1_m", f"b_{k}_p"])
        reals[f"E_eps1_del{k}_mm"] = mono(["a_1_m", f"b_{k}_m"])
        for ss in ("pp", "pm", "mp", "mm"):
            pars[f"E_eps1_del{k}_{ss}"] = 1

    return even, odd, reals, pars


def project(P: Poly, n: int) -> Dict[str, Fraction]:
    """Express a normal-form oscillator polynomial P as a basis combination."""
    P = dict(P)
    coeffs: Dict[str, Fraction] = {}

    for k in range(1, n + 1):
        for word, label in [
            (("a_1_p", f"b_{k}_p"), f"E_eps1_del{k}_pp"),
            (("a_1_p", f"b_{k}_m"), f"E_eps1_del{k}_pm"),
            (("a_1_m", f"b_{k}_p"), f"E_eps1_del{k}_mp"),
            (("a_1_m", f"b_{k}_m"), f"E_eps1_del{k}_mm"),
        ]:
            v = P.pop(word, Fraction(0))
            if v != 0:
                coeffs[label] = v

    v_a = P.pop(("a_1_p", "a_1_m"), Fraction(0))
    if v_a != 0:
        coeffs["H_1"] = v_a
        w = ("b_1_p", "b_1_m")
        P[w] = P.get(w, Fraction(0)) - v_a
        if P[w] == 0:
            P.pop(w, None)

    for k in range(1, n + 1):
        for suff, lbl in [("p", f"E_2del{k}_p"), ("m", f"E_2del{k}_m")]:
            w = (f"b_{k}_{suff}", f"b_{k}_{suff}")
            v = P.pop(w, Fraction(0))
            if v != 0:
                coeffs[lbl] = v
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for w, lbl in [
                ((f"b_{i}_p", f"b_{j}_p"), f"E_del{i}_del{j}_pp"),
                ((f"b_{i}_m", f"b_{j}_m"), f"E_del{i}_del{j}_mm"),
                ((f"b_{i}_p", f"b_{j}_m"), f"E_del{i}_del{j}_pm"),
                ((f"b_{i}_m", f"b_{j}_p"), f"E_del{i}_del{j}_mp"),
            ]:
                v = P.pop(w, Fraction(0))
                if v != 0:
                    coeffs[lbl] = v

    v_bb = [P.pop((f"b_{k}_p", f"b_{k}_m"), Fraction(0)) for k in range(1, n + 1)]
    v_const = P.pop((), Fraction(0))

    c: Dict[int, Fraction] = {}
    if n == 1:
        c[2] = -2 * v_const
    else:
        c[n + 1] = -2 * v_const
        c[n] = -v_bb[n - 1] - c[n + 1]
        for k in range(n - 1, 1, -1):
            c[k] = c[k + 1] - v_bb[k - 1]
    for k in range(2, n + 2):
        if c[k] != 0:
            coeffs[f"H_{k}"] = coeffs.get(f"H_{k}", Fraction(0)) + c[k]
            if coeffs[f"H_{k}"] == 0:
                coeffs.pop(f"H_{k}", None)

    return coeffs


def recombine(coeffs: Dict[str, Fraction], reals: Dict[str, Poly]) -> Poly:
    out: Poly = {}
    for lbl, c in coeffs.items():
        out = poly_add(out, reals[lbl], c)
    return out


def structure_constants(n: int):
    even, odd, reals, pars = build_basis(n)
    all_labels = even + odd
    out = []
    closure_errors = []
    for i, X in enumerate(all_labels):
        for j in range(i, len(all_labels)):
            Y = all_labels[j]
            pX, pY = pars[X], pars[Y]
            br = graded_bracket(reals[X], reals[Y], pX, pY)
            if not br:
                continue
            coeffs = project(br, n)
            # Closure check: recombining must reproduce bracket up to K direction
            recom = recombine(coeffs, reals)
            residual = poly_add(br, recom, Fraction(-1))
            if residual:
                closure_errors.append((X, Y, residual))
            for Z, c in coeffs.items():
                out.append(
                    {
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coeff": str(c),
                        "sign_rule": "graded",
                    }
                )
    return out, even, odd, reals, pars, closure_errors


def serialize_poly(p: Poly):
    return [
        {"words": list(w), "coeff": str(c)}
        for w, c in sorted(p.items(), key=lambda kv: (len(kv[0]), kv[0]))
    ]


def build_structure_json(n: int) -> dict:
    sc, even, odd, reals, pars, closure_errors = structure_constants(n)
    if closure_errors:
        raise RuntimeError(
            f"Non-closing brackets detected: {closure_errors[:3]} ..."
        )
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
                "total": 2 * n * n + 5 * n + 1,
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair with CAR",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")],
                "description": "Bosonic oscillators with CCR",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "pair": "{a_1^-, a_1^+} = 1",
                "squares": "(a_1^+)^2 = 0, (a_1^-)^2 = 0",
            },
            "bosonic_commutators": {
                "same_type": "[b_i^s, b_j^s] = 0",
                "conjugate_pair": "[b_i^-, b_j^+] = delta_{ij}",
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^s, a_1^sigma] = 0 (undeformed)"
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "role": "Odd central generator for inhomogeneous (gb) deformation",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1",
                "role": "Even central identity; excluded from basis",
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]; K = 1 excluded",
        },
        "parity": {lbl: pars[lbl] for lbl in even + odd},
        "generator_realization": {
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
            "realizations": {
                lbl: {
                    "standard_form": serialize_poly(reals[lbl]),
                    "parity": pars[lbl],
                }
                for lbl in even + odd
            },
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": str(date.today()),
            "references": [
                "Frappat-Sciarrino-Sorba (2000)",
                "arXiv:hep-th/9607161",
            ],
        },
    }


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    os.makedirs(out_dir, exist_ok=True)
    for n in (1, 2, 3):
        obj = build_structure_json(n)
        path = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print(f"wrote {path} ({len(obj['structure_constants'])} brackets)")


if __name__ == "__main__":
    main()

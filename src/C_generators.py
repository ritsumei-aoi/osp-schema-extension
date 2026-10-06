"""Schema 1 generator for C(n+1) = osp(2|2n).

Builds the PBW basis, computes all graded structure constants in the
undeformed oscillator algebra, and writes ``data/C_{n}_structure.json``
following ``docs/json_schema_specification.md``.

Usage::

    python -m src.C_generators            # n = 1, 2, 3
    python src/C_generators.py 2          # just n = 2
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List

import sympy as sp

try:
    from .osc_algebra import CAlgebra, boson
except ImportError:  # run as a script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import CAlgebra, boson  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
GENERATION_DATE = "2026-10-06"

REFERENCES = [
    "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
    "docs/math/Cn1_definition.md",
    "handover/notation.md",
]


def rat(expr) -> str:
    """String-encode a rational coefficient."""
    return str(sp.nsimplify(expr))


# --------------------------------------------------------------------------
def algebra_field(n: int) -> dict:
    even = 2 * n * n + n + 1
    odd = 4 * n
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
        "alternative_notation": {
            "osp": f"osp(2|{2 * n})",
            "dimension_formula": "osp(2m|2n) with m=1",
        },
        "dimension": {"total": even + odd, "even": even, "odd": odd},
        "dimension_formulas": {
            "even": "2n^2 + n + 1",
            "odd": "4n",
            "total": "2n^2 + 5n + 1",
        },
        "even_subalgebra": "so(2) + sp(2n)",
        "rank": n + 1,
    }


def oscillator_generators(n: int) -> dict:
    return {
        "fermions": {
            "count": 2,
            "m": 1,
            "labels": ["a_1_p", "a_1_m"],
            "type": "standard_CAR_pair",
            "parity": 1,
            "description": (
                "Standard fermionic creation/annihilation pair a_1^+, a_1^- with "
                "{a_1^-, a_1^+} = 1. Replaces the B(0,n) supplementary fermion a_0."
            ),
        },
        "bosons": {
            "count": 2 * n,
            "n": n,
            "labels": [boson(k, s) for k in range(1, n + 1) for s in ("p", "m")],
            "type": "standard_CCR_pairs",
            "parity": 0,
            "description": "Bosonic oscillators b_k^+- with k = 1,...,n",
        },
    }


def oscillator_relations(n: int) -> dict:
    return {
        "standard_fermion_anticommutators": {
            "description": "Canonical anticommutation relations for the standard fermionic pair",
            "relations": {
                "conjugate_pair": "{a_1^-, a_1^+} = 1",
                "same_type": "{a_1^s, a_1^s} = 0, i.e. (a_1^s)^2 = 0",
            },
        },
        "bosonic_commutators": {
            "description": "Canonical commutation relations for bosonic oscillators",
            "relations": {
                "same_type": "[b_k^s, b_l^t] = 0 unless {s,t} = {+,-} and k = l",
                "conjugate_pair": "[b_k^-, b_l^+] = delta_{kl}",
            },
        },
        "mixed_commutators": {
            "boson_fermion": (
                "[b_k^s, a_1^sigma] = 0   (undeformed Schema 1; "
                "see Schema 2 for the gamma-deformed relation)"
            )
        },
        "normal_ordering": {
            "letter_order": ["kappa", "a_1_p", "a_1_m"]
            + [boson(k, s) for k in range(1, n + 1) for s in ("p", "m")],
            "description": "Index map kappa=0, a_1_p=1, a_1_m=2, b_k_p=2k+1, b_k_m=2k+2",
        },
    }


def central_elements() -> dict:
    return {
        "kappa": {
            "label": "kappa",
            "parity": 1,
            "relations": [
                "kappa^2 = 0",
                "kappa X = (-1)^{p(X)} X kappa  (supercentral)",
            ],
            "in_basis": False,
            "description": (
                "Odd central element carrying the inhomogeneous deformation: "
                "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)."
            ),
        },
        "K": {
            "label": "K",
            "parity": 0,
            "relations": ["K = 1", "[K, X] = 0"],
            "in_basis": False,
            "description": (
                "Even central element (Bakalov-Sullivan). Identified with the scalar 1; "
                "excluded from the PBW basis, recorded here for schema completeness."
            ),
        },
    }


def generator_realization(alg: CAlgebra) -> dict:
    n = alg.n
    realizations: Dict[str, dict] = {}
    for lab in alg.pbw_order:
        elt = alg.realization[lab]
        terms = []
        for w in sorted(elt, key=lambda w: (len(w), w)):
            terms.append({"words": list(w), "coeff": rat(elt[w])})
        terms.sort(key=lambda t: (-len(t["words"]), t["words"]))
        realizations[lab] = {
            "standard_form": terms,
            "frappat_form": frappat_form(lab, elt),
            "parity": alg.parity[lab],
            "root": alg.roots[lab],
        }
    return {
        "description": "Standard form with normal-ordered oscillator words",
        "ordering": ", ".join(
            ["a_1_p", "a_1_m"] + [boson(k, s) for k in range(1, n + 1) for s in ("p", "m")]
        ),
        "realizations": realizations,
    }


def frappat_form(label: str, elt) -> str:
    def pretty(letter: str) -> str:
        if letter.startswith("a_"):
            return "a_1^+" if letter.endswith("_p") else "a_1^-"
        _, k, s = letter.split("_")
        return f"b_{k}^{'+' if s == 'p' else '-'}"

    parts: List[str] = []
    for w in sorted(elt, key=lambda w: (-len(w), w)):
        c = elt[w]
        body = " ".join(pretty(x) for x in w)
        cs = rat(c)
        if body and cs == "1":
            parts.append(body)
        elif body and cs == "-1":
            parts.append("-" + body)
        elif body:
            parts.append(f"{cs} {body}")
        else:
            parts.append(cs)
    out = parts[0]
    for p in parts[1:]:
        out += (" - " + p[1:]) if p.startswith("-") else (" + " + p)
    return out


def structure_constants(alg: CAlgebra) -> List[dict]:
    """All non-zero brackets for ordered pairs pbw_index(X) <= pbw_index(Y)."""
    entries: List[dict] = []
    order = alg.pbw_order
    for a, x in enumerate(order):
        for y in order[a:]:
            coeffs = alg.bracket_coeffs(x, y)
            for z in order + ["K"]:
                c = coeffs.get(z)
                if c is None or sp.expand(c) == 0:
                    continue
                entries.append(
                    {"X": x, "Y": y, "Z": z, "coeff": rat(c), "sign_rule": "graded"}
                )
    return entries


def build_schema1(n: int) -> dict:
    alg = CAlgebra(n)
    return {
        "schema_version": "5.0",
        "layer": 1,
        "algebra": algebra_field(n),
        "oscillator_generators": oscillator_generators(n),
        "oscillator_relations": oscillator_relations(n),
        "central_elements": central_elements(),
        "basis": {
            "even": alg.even,
            "odd": alg.odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
            "pbw_order": alg.pbw_order,
        },
        "parity": {lab: alg.parity[lab] for lab in alg.pbw_order},
        "generator_realization": generator_realization(alg),
        "structure_constants": structure_constants(alg),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": GENERATION_DATE,
            "storage_convention": (
                "ordered pairs pbw_index(X) <= pbw_index(Y); "
                "graded antisymmetry [Y,X} = -(-1)^{p(X)p(Y)}[X,Y} implied"
            ),
            "bracket_convention": "[X,Y} = XY - (-1)^{p(X)p(Y)} YX",
            "cartan_normalization": (
                "symmetrized: H_eps1 = a_1^+a_1^- - 1/2, H_del{k} = b_k^+b_k^- + 1/2"
            ),
            "references": REFERENCES,
        },
    }


def write_schema1(n: int) -> str:
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, f"C_{n}_structure.json")
    with open(path, "w") as fh:
        json.dump(build_schema1(n), fh, indent=2)
        fh.write("\n")
    return path


def main(argv: List[str]) -> None:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    for n in ns:
        path = write_schema1(n)
        with open(path) as fh:
            doc = json.load(fh)
        d = doc["algebra"]["dimension"]
        print(
            f"n={n}  C({n + 1})  even={d['even']} odd={d['odd']} total={d['total']}  "
            f"structure_constants={len(doc['structure_constants'])}  -> {os.path.relpath(path, REPO)}"
        )


if __name__ == "__main__":
    main(sys.argv)

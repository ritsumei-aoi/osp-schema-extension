"""Basis, oscillator realization and Schema 1 (structure constants) for C(n+1) = osp(2|2n).

Conventions are fixed in ``handover/notation.md`` (Issue I01) and the JSON layout in
``docs/json_schema_specification.md`` (Issue I02).

Usage:
    python src/C_generators.py            # writes data/C_{n}_structure.json for n = 1, 2, 3
    python src/C_generators.py 2          # only n = 2
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from typing import Dict, List

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import Element, OscillatorAlgebra  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SCHEMA_VERSION = "5.0"
SIGN = {"p": "+", "m": "-"}


# ----------------------------------------------------------------------------- basis
def even_basis(n: int) -> List[str]:
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    pos = [f"E_2del{k}_p" for k in range(1, n + 1)] + [
        f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)
    ]
    neg = [f"E_2del{k}_m" for k in range(1, n + 1)] + [
        f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)
    ]
    mixed = [f"E_del{i}_del{j}_pm" for i in range(1, n + 1) for j in range(i + 1, n + 1)] + [
        f"E_del{i}_del{j}_mp" for i in range(1, n + 1) for j in range(i + 1, n + 1)
    ]
    return cartan + pos + neg + mixed


def odd_basis(n: int) -> List[str]:
    return [f"E_eps1_del{k}_{st}" for st in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def basis(n: int) -> List[str]:
    """Full basis in PBW order: [odd] < [even] (kappa, when present, precedes everything)."""
    return odd_basis(n) + even_basis(n)


def parity_table(n: int) -> Dict[str, int]:
    return {**{g: 1 for g in odd_basis(n)}, **{g: 0 for g in even_basis(n)}}


def dimensions(n: int) -> Dict[str, int]:
    return {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1, "odd": 4 * n}


# ----------------------------------------------------------------- root vectors
def root_vector(label: str, n: int) -> List[int]:
    """Root in the basis (eps, delta_1, ..., delta_n); Cartan elements have the zero root."""
    v = [0] * (n + 1)
    if label.startswith("H_"):
        return v
    if label.startswith("E_eps1_del"):
        k, st = label[len("E_eps1_del"):].split("_")
        v[0] = 1 if st[0] == "p" else -1
        v[int(k)] = 1 if st[1] == "p" else -1
        return v
    if label.startswith("E_2del"):
        k, s = label[len("E_2del"):].split("_")
        v[int(k)] = 2 if s == "p" else -2
        return v
    if label.startswith("E_del"):
        body = label[len("E_"):]
        di, dj, st = body.split("_")
        i, j = int(di[3:]), int(dj[3:])
        v[i] = 1 if st[0] == "p" else -1
        v[j] = 1 if st[1] == "p" else -1
        return v
    raise ValueError(label)


# ---------------------------------------------------------------- realizations
def realization(label: str, n: int) -> dict:
    """Return {"standard_form": [...], "frappat_form": str, "parity": int, ...}."""
    if label == "H_1":
        sf = [{"words": ["a_1_p", "a_1_m"], "coeff": "1"}, {"words": ["b_1_p", "b_1_m"], "coeff": "1"}]
        return {"standard_form": sf, "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0,
                "note": "Cartan element of the odd simple root eps - delta_1"}
    if label == f"H_{n + 1}":
        sf = [{"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"}, {"words": [], "coeff": "-1/2"}]
        return {"standard_form": sf, "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2", "parity": 0,
                "note": "Terminal Cartan element of the simple root 2 delta_n; the constant -1/2 is "
                        "forced by [E_2del{n}_p, E_2del{n}_m] = 4 H_{n+1}".replace("{n}", str(n))}
    if label.startswith("H_"):
        k = int(label[2:])
        sf = [{"words": [f"b_{k - 1}_p", f"b_{k - 1}_m"], "coeff": "1"},
              {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}]
        return {"standard_form": sf, "frappat_form": f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-",
                "parity": 0, "note": f"Cartan element of the simple root delta_{k - 1} - delta_{k}"}
    if label.startswith("E_eps1_del"):
        k, st = label[len("E_eps1_del"):].split("_")
        words = [f"a_1_{st[0]}", f"b_{k}_{st[1]}"]
        return {"standard_form": [{"words": words, "coeff": "1"}],
                "frappat_form": f"a_1^{SIGN[st[0]]} b_{k}^{SIGN[st[1]]}", "parity": 1}
    if label.startswith("E_2del"):
        k, s = label[len("E_2del"):].split("_")
        words = [f"b_{k}_{s}", f"b_{k}_{s}"]
        return {"standard_form": [{"words": words, "coeff": "1"}],
                "frappat_form": f"(b_{k}^{SIGN[s]})^2", "parity": 0}
    if label.startswith("E_del"):
        di, dj, st = label[len("E_"):].split("_")
        i, j = int(di[3:]), int(dj[3:])
        words = [f"b_{i}_{st[0]}", f"b_{j}_{st[1]}"]
        return {"standard_form": [{"words": words, "coeff": "1"}],
                "frappat_form": f"b_{i}^{SIGN[st[0]]} b_{j}^{SIGN[st[1]]}", "parity": 0}
    raise ValueError(label)


def realizations(n: int) -> Dict[str, dict]:
    return {g: realization(g, n) for g in basis(n)}


def elements(n: int) -> Dict[str, Element]:
    return {g: OscillatorAlgebra.from_standard_form(r["standard_form"]) for g, r in realizations(n).items()}


# ---------------------------------------------------------------- decomposition
class Decomposer:
    """Express a (quadratic) normal-ordered element in the basis of g~ = g (+) C K.

    Root vectors are single oscillator words.  The Cartan subalgebra together with the
    central identity K spans {a_1^+ a_1^-, b_k^+ b_k^-, 1}; that (n+2)-dimensional
    system is inverted exactly once.
    """

    def __init__(self, n: int):
        self.n = n
        self.basis = basis(n)
        self.elems = elements(n)
        self.word_to_root = {}
        for g, e in self.elems.items():
            if not g.startswith("H_"):
                (w, c), = e.items()
                assert c == 1
                self.word_to_root[w] = g
        self.cartan_words = [("a_1_p", "a_1_m")] + [(f"b_{k}_p", f"b_{k}_m") for k in range(1, n + 1)] + [()]
        self.cartan_basis = [f"H_{k}" for k in range(1, n + 2)] + ["K"]
        rows = []
        for w in self.cartan_words:
            row = []
            for g in self.cartan_basis:
                if g == "K":
                    row.append(sp.Integer(1) if w == () else sp.Integer(0))
                else:
                    row.append(self.elems[g].get(w, sp.Integer(0)))
            rows.append(row)
        self.cartan_matrix_inv = sp.Matrix(rows).inv()

    def decompose(self, elem: Element) -> Dict[str, sp.Expr]:
        """Return {basis label or 'K': coefficient}; raises if elem is not in span."""
        out: Dict[str, sp.Expr] = {}
        cvec = [sp.Integer(0)] * len(self.cartan_words)
        for w, c in elem.items():
            if w in self.word_to_root:
                out[self.word_to_root[w]] = out.get(self.word_to_root[w], 0) + c
            elif w in self.cartan_words:
                cvec[self.cartan_words.index(w)] += c
            else:
                raise ValueError(f"word {w} is not in the span of the basis")
        sol = self.cartan_matrix_inv * sp.Matrix(cvec)
        for g, c in zip(self.cartan_basis, sol):
            c = sp.expand(c)
            if c != 0:
                out[g] = c
        return {g: sp.expand(c) for g, c in out.items() if sp.expand(c) != 0}


# ------------------------------------------------------------- structure constants
def structure_constants(n: int):
    """All non-zero graded brackets [X, Y} for ordered pairs of basis elements."""
    alg = OscillatorAlgebra(n)
    dec = Decomposer(n)
    elems = dec.elems
    out = []
    for X in dec.basis:
        for Y in dec.basis:
            br = alg.bracket(elems[X], elems[Y])
            for Z, c in dec.decompose(br).items():
                assert Z != "K", f"[{X},{Y}] has a K component in the undeformed algebra"
                out.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
    return out


# ----------------------------------------------------------------------- schema
def build_schema1(n: int) -> dict:
    ev, od = even_basis(n), odd_basis(n)
    dims = dimensions(n)
    assert len(ev) == dims["even"] and len(od) == dims["odd"]
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    return {
        "schema_version": SCHEMA_VERSION,
        "schema_layer": 1,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": dims,
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
            "rank": n + 1,
            "even_subalgebra": f"so(2) + sp({2 * n})",
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^± (CAR); replaces the supplementary fermion a_0 of B(0,n)",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": boson_labels,
                "parity": 0,
                "description": "Bosonic oscillators b_k^± with k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_j^±, a_1^±] = 0  (undeformed; see Schema 2 for the gb deformation)",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0, [kappa, X} = 0 for all X",
                "description": "Odd nilpotent symbol of the inhomogeneous deformation; first in PBW order. Not a basis element of C(n+1).",
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1 (central identity)",
                "description": "Even central identity of the pre-oscillator extension A = V + CK + C kappa. Identified with the scalar 1; excluded from the basis and from PBW ordering.",
            },
        },
        "basis": {
            "even": ev,
            "odd": od,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
            "odd_label_convention": "E_eps1_del{k}_{st}: s = sign of eps (fermion a_1^s), t = sign of delta_k (boson b_k^t)",
        },
        "parity": parity_table(n),
        "roots": {
            "coordinates": ["eps"] + [f"delta_{k}" for k in range(1, n + 1)],
            "simple_roots": (["eps - delta_1"] + [f"delta_{k - 1} - delta_{k}" for k in range(2, n + 1)]
                             + [f"2 delta_{n}"]),
            "vectors": {g: root_vector(g, n) for g in basis(n)},
        },
        "generator_realization": {
            "description": "Standard form with PBW ordering of oscillator words",
            "ordering": ", ".join(["kappa", "a_1_p", "a_1_m"] + boson_labels),
            "realizations": realizations(n),
        },
        "structure_constants": structure_constants(n),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": _dt.date.today().isoformat(),
            "structure_constants_convention": "All ordered pairs (X, Y) with non-zero graded bracket [X, Y} = sum_Z coeff * Z are listed.",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras; arXiv:hep-th/9607161",
                "Bakalov and Sullivan (2017), arXiv:1612.09400",
            ],
        },
    }


def structure_path(n: int) -> str:
    return os.path.join(DATA_DIR, f"C_{n}_structure.json")


def write_schema1(n: int) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = structure_path(n)
    with open(path, "w") as fh:
        json.dump(build_schema1(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_schema1(n)
        d = json.load(open(p))
        print(f"n={n}: wrote {os.path.relpath(p, ROOT)}  dim={d['algebra']['dimension']}  "
              f"nonzero brackets={len(d['structure_constants'])}")

"""Schema 1 generator for C(n+1) = osp(2|2n): basis, realization, structure constants.

Usage:  python3 src/C_generators.py [n ...]      (default: 1 2 3)
Writes  data/C_{n}_structure.json.

Conventions: handover/notation.md; specification: docs/json_schema_specification.md.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import (Decomposer, Element, OscillatorAlgebra,  # noqa: E402
                                frac_str, graded_commutator)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")

REFERENCES = [
    "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
    "Bakalov and Sullivan (2017), arXiv:1612.09400",
]


# ---------------------------------------------------------------------------
# Basis labels (handover/notation.md section 4)
# ---------------------------------------------------------------------------
def even_labels(n: int) -> List[str]:
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labels = [f"H_{k}" for k in range(1, n + 2)]
    labels += [f"E_2del{k}_p" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    labels += [f"E_2del{k}_m" for k in range(1, n + 1)]
    labels += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    labels += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    labels += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return labels


def odd_labels(n: int) -> List[str]:
    labels = []
    for signs in ("pp", "pm", "mp", "mm"):
        labels += [f"E_eps1_del{k}_{signs}" for k in range(1, n + 1)]
    return labels


def pbw_order(n: int) -> List[str]:
    """PBW order of the basis of g: kappa < [odd] < [even] (kappa and K excluded)."""
    return odd_labels(n) + even_labels(n)


def dimensions(n: int) -> Dict[str, int]:
    return {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1, "odd": 4 * n}


# ---------------------------------------------------------------------------
# Oscillator realization
# ---------------------------------------------------------------------------
def _sgn(s: str) -> int:
    return 1 if s == "p" else -1


def realization_words(label: str, n: int) -> Tuple[List[Tuple[List[str], Fraction]], str, dict | None]:
    """Return (list of (word, coeff)), frappat string, root dict) for a basis label."""
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            words = [(["a_1_p", "a_1_m"], Fraction(1)), (["b_1_p", "b_1_m"], Fraction(1))]
            fr = "a_1^+ a_1^- + b_1^+ b_1^-"
        elif k <= n:
            words = [([f"b_{k-1}_p", f"b_{k-1}_m"], Fraction(1)), ([f"b_{k}_p", f"b_{k}_m"], Fraction(-1))]
            fr = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
        else:  # k == n+1
            words = [([f"b_{n}_p", f"b_{n}_m"], Fraction(-1)), ([], Fraction(-1, 2))]
            fr = f"-b_{n}^+ b_{n}^- - 1/2"
        return words, fr, None
    parts = label.split("_")  # E, root parts..., signs
    signs = parts[-1]
    if parts[1] == "eps1":
        k = int(parts[2][3:])
        fs, bs = signs[0], signs[1]
        words = [([f"a_1_{fs}", f"b_{k}_{bs}"], Fraction(1))]
        fr = f"a_1^{'+' if fs=='p' else '-'} b_{k}^{'+' if bs=='p' else '-'}"
        root = {"eps": _sgn(fs), "del": [_sgn(bs) if kk == k else 0 for kk in range(1, n + 1)]}
        return words, fr, root
    if parts[1].startswith("2del"):
        k = int(parts[1][4:])
        s = signs
        words = [([f"b_{k}_{s}", f"b_{k}_{s}"], Fraction(1))]
        fr = f"(b_{k}^{'+' if s=='p' else '-'})^2"
        root = {"eps": 0, "del": [2 * _sgn(s) if kk == k else 0 for kk in range(1, n + 1)]}
        return words, fr, root
    # E_del{i}_del{j}_xy
    i = int(parts[1][3:])
    j = int(parts[2][3:])
    si, sj = signs[0], signs[1]
    words = [([f"b_{i}_{si}", f"b_{j}_{sj}"], Fraction(1))]
    fr = f"b_{i}^{'+' if si=='p' else '-'} b_{j}^{'+' if sj=='p' else '-'}"
    root = {"eps": 0, "del": [(_sgn(si) if kk == i else 0) + (_sgn(sj) if kk == j else 0)
                              for kk in range(1, n + 1)]}
    return words, fr, root


def build_elements(alg: OscillatorAlgebra) -> Dict[str, Element]:
    """Realization of every basis label as an Element of the oscillator algebra."""
    n = alg.n
    out: Dict[str, Element] = {}
    for label in pbw_order(n):
        words, _, _ = realization_words(label, n)
        el = Element(alg)
        for w, c in words:
            el = el + Element.word(alg, *w, coeff=c)
        out[label] = el
    return out


def make_decomposer(alg: OscillatorAlgebra, elements: Dict[str, Element], with_K: bool = True) -> Decomposer:
    cols = [(lab, elements[lab]) for lab in pbw_order(alg.n)]
    if with_K:
        cols.append(("K", Element.scalar(alg, 1)))
    return Decomposer(cols)


# ---------------------------------------------------------------------------
# Structure constants
# ---------------------------------------------------------------------------
def compute_structure_constants(n: int) -> Tuple[List[dict], Dict[str, int]]:
    alg = OscillatorAlgebra(n, deformed=False)
    elements = build_elements(alg)
    dec = make_decomposer(alg, elements, with_K=True)
    labels = pbw_order(n)
    parity = {lab: elements[lab].parity() for lab in labels}
    sc: List[dict] = []
    for X in labels:
        for Y in labels:
            br = graded_commutator(elements[X], elements[Y])
            if br.is_zero():
                continue
            coeffs = dec.decompose(br)
            if "K" in coeffs:
                raise RuntimeError(f"unexpected constant term in [{X},{Y}}}: {coeffs}")
            for Z in labels:
                if Z in coeffs:
                    sc.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(coeffs[Z]), "sign_rule": "graded"})
    return sc, parity


# ---------------------------------------------------------------------------
# Schema 1 document
# ---------------------------------------------------------------------------
def algebra_block(n: int) -> dict:
    dims = dimensions(n)
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n+1})",
        "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
        "dimension": {
            "total": dims["total"], "even": dims["even"], "odd": dims["odd"],
            "formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
        },
        "even_subalgebra": "so(2) + sp(2n)",
        "rank": n + 1,
    }


def central_elements_block() -> dict:
    return {
        "kappa": {
            "label": "kappa", "parity": 1,
            "relation": "kappa^2 = 0; [kappa, X} = 0 for all X",
            "role": "odd central element of the inhomogeneous extension A = V + C K + C kappa; carries the deformation (Schema 2). Not a basis element of g; first in PBW order.",
            "in_basis": False,
        },
        "K": {
            "label": "K", "parity": 0,
            "relation": "[K, X} = 0 for all X; identified with the scalar 1",
            "role": "even central element (constant term of oscillator words). Excluded from basis lists; appears as a bracket target label only in Schemas 2-4 when a constant term arises.",
            "in_basis": False,
        },
    }


def build_schema1(n: int) -> dict:
    alg = OscillatorAlgebra(n, deformed=False)
    sc, parity = compute_structure_constants(n)
    realizations = {}
    for label in pbw_order(n):
        words, fr, root = realization_words(label, n)
        entry = {
            "standard_form": [{"words": w, "coeff": frac_str(c)} for w, c in words],
            "frappat_form": fr,
            "parity": parity[label],
            "root": root,
        }
        if label == f"H_{n+1}":
            entry["note"] = "Terminal Cartan; includes constant -1/2 (symmetrized number operator -N_n^s)"
        if label == "H_1":
            entry["note"] = "so(2)+sp(2n) Cartan element N_0^s + N_1^s (constants cancel)"
        realizations[label] = entry
    bosons = alg.bosons
    doc = {
        "schema_version": "5.0",
        "schema_layer": 1,
        "algebra": algebra_block(n),
        "oscillator_generators": {
            "fermions": {
                "m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                "description": "Standard fermionic pair a_1^± (CAR); replaces B(0,n)'s supplementary fermion a_0.",
            },
            "bosons": {
                "n": n, "count": 2 * n, "labels": bosons, "parity": 0,
                "description": "Bosonic oscillators b_k^± (CCR), k = 1..n.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard pair a_1^±",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^+)^2 = (a_1^-)^2 = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed algebra; deformed in Schema 2)"},
            "normal_ordering": "kappa < " + " < ".join(alg.oscillators),
        },
        "central_elements": central_elements_block(),
        "basis": {
            "even": even_labels(n),
            "odd": odd_labels(n),
            "pbw_order": pbw_order(n),
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": {lab: parity[lab] for lab in pbw_order(n)},
        "generator_realization": {
            "description": "Standard form: sum of normal-ordered oscillator words with rational coefficients",
            "ordering": ", ".join(alg.oscillators),
            "realizations": realizations,
        },
        "structure_constants": sc,
        "structure_constants_convention": {
            "pairs": "all ordered pairs (X, Y) with non-zero bracket",
            "bracket": "[X,Y} = X Y - (-1)^{p(X)p(Y)} Y X",
            "count": len(sc),
        },
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": _dt.date.today().isoformat(),
            "notation": "handover/notation.md",
            "references": REFERENCES,
        },
    }
    return doc


def write_schema1(n: int, data_dir: str = DATA_DIR) -> str:
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path, "w") as fh:
        json.dump(build_schema1(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_schema1(n)
        d = json.load(open(p))
        print(f"wrote {p}: dim {d['algebra']['dimension']}, "
              f"{d['structure_constants_convention']['count']} non-zero brackets")

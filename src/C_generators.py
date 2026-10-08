"""
C(n+1) = osp(2|2n): basis construction and structure-constant generator (Schema 1, v5.0).

Usage:
    python src/C_generators.py            # writes data/C_1_structure.json ... C_3_structure.json
    python src/C_generators.py 2          # only n = 2

Conventions: handover/notation.md ; schema: docs/json_schema_specification.md
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator import Decomposer, Element, LinPoly, OscillatorAlgebra  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")

SIGN = {"p": "+", "m": "-"}
SIGN_VAL = {"p": 1, "m": -1}


# --------------------------------------------------------------------------- #
# Basis (labels, ordering, realizations)
# --------------------------------------------------------------------------- #
def even_labels(n: int) -> List[str]:
    labs = [f"H_{i}" for i in range(1, n + 2)]
    labs += [f"E_2del{k}_p" for k in range(1, n + 1)]
    labs += [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labs += [f"E_2del{k}_m" for k in range(1, n + 1)]
    labs += [f"E_del{i}_del{j}_mm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labs += [f"E_del{i}_del{j}_pm" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labs += [f"E_del{i}_del{j}_mp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    return labs


def odd_labels(n: int) -> List[str]:
    labs = []
    for ss in ("pp", "pm", "mp", "mm"):
        labs += [f"E_eps1_del{k}_{ss}" for k in range(1, n + 1)]
    return labs


def pbw_order(n: int) -> List[str]:
    return odd_labels(n) + even_labels(n)


def parity_of(label: str) -> int:
    return 1 if label.startswith("E_eps1_") else 0


def realization_words(n: int, label: str) -> Tuple[List[Tuple[Tuple[str, ...], Fraction]], str, object]:
    """Return (list of (word, coeff)), Frappat-form string, root vector (or None)."""
    if label.startswith("H_"):
        i = int(label[2:])
        if i == 1:
            return ([(("a_1_p", "a_1_m"), Fraction(1)), (("b_1_p", "b_1_m"), Fraction(1))],
                    "a_1^+ a_1^- + b_1^+ b_1^-", None)
        if i <= n:
            return ([((f"b_{i-1}_p", f"b_{i-1}_m"), Fraction(1)), ((f"b_{i}_p", f"b_{i}_m"), Fraction(-1))],
                    f"b_{i-1}^+ b_{i-1}^- - b_{i}^+ b_{i}^-", None)
        return ([((f"b_{n}_p", f"b_{n}_m"), Fraction(-1)), ((), Fraction(-1, 2))],
                f"-b_{n}^+ b_{n}^- - 1/2", None)
    if label.startswith("E_2del"):
        body, s = label[len("E_2del"):].split("_")
        k = int(body)
        vec = [0] * (n + 1)
        vec[k] = 2 * SIGN_VAL[s]
        return ([((f"b_{k}_{s}", f"b_{k}_{s}"), Fraction(1))], f"(b_{k}^{SIGN[s]})^2", vec)
    if label.startswith("E_eps1_del"):
        body, ss = label[len("E_eps1_del"):].split("_")
        k = int(body)
        sigma, s = ss[0], ss[1]
        vec = [0] * (n + 1)
        vec[0] = SIGN_VAL[sigma]
        vec[k] = SIGN_VAL[s]
        return ([((f"a_1_{sigma}", f"b_{k}_{s}"), Fraction(1))], f"a_1^{SIGN[sigma]} b_{k}^{SIGN[s]}", vec)
    if label.startswith("E_del"):
        rest = label[len("E_del"):]           # e.g. "1_del2_pm"
        i_str, rest2 = rest.split("_del")
        j_str, ss = rest2.split("_")
        i, j = int(i_str), int(j_str)
        si, sj = ss[0], ss[1]
        vec = [0] * (n + 1)
        vec[i] = SIGN_VAL[si]
        vec[j] = SIGN_VAL[sj]
        return ([((f"b_{i}_{si}", f"b_{j}_{sj}"), Fraction(1))], f"b_{i}^{SIGN[si]} b_{j}^{SIGN[sj]}", vec)
    raise ValueError(label)


def root_string(vec) -> str | None:
    if vec is None:
        return None
    names = ["eps1"] + [f"del{k}" for k in range(1, len(vec))]
    parts = []
    for c, name in zip(vec, names):
        if c == 0:
            continue
        mag = "" if abs(c) == 1 else f"{abs(c)}"
        parts.append(("+" if c > 0 else "-") + mag + name)
    s = " ".join(parts)
    return s[1:] if s.startswith("+") else s


def build_basis(n: int, deformed: bool = False) -> Tuple[OscillatorAlgebra, Dict[str, Element]]:
    alg = OscillatorAlgebra(n, deformed=deformed)
    basis: Dict[str, Element] = {}
    for lab in pbw_order(n):
        words, _, _ = realization_words(n, lab)
        basis[lab] = Element(alg, {w: LinPoly(c) for w, c in words})
    return alg, basis


# --------------------------------------------------------------------------- #
# Structure constants
# --------------------------------------------------------------------------- #
def compute_brackets(n: int, deformed: bool = False):
    """Return (alg, basis, decomposer, table) with
    table[(X, Y)] = (coeffs0: {Z: LinPoly}, kappa_coeffs: {Z: LinPoly}).
    Raises if any bracket leaves span(basis) (constants are tolerated only in the kappa part)."""
    alg, basis = build_basis(n, deformed)
    dec = Decomposer(alg, basis)
    order = pbw_order(n)
    table = {}
    for x in order:
        for y in order:
            br = basis[x].bracket(basis[y])
            base, kap = br.split_kappa()
            c0, const0 = dec.decompose(base)
            if not const0.is_zero():
                raise ValueError(f"[{x},{y}] has a constant term {const0}")
            ck, _constk = dec.decompose(kap) if not kap.is_zero() else ({}, LinPoly())
            table[(x, y)] = (c0, ck, _constk)
    return alg, basis, dec, table


# --------------------------------------------------------------------------- #
# Schema 1 JSON
# --------------------------------------------------------------------------- #
def algebra_block(n: int) -> dict:
    even, odd = 2 * n * n + n + 1, 4 * n
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
        "alternative_notation": {"osp": f"osp(2|{2 * n})", "dimension_formula": "osp(2m|2n) with m=1"},
        "dimension_formula": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
        "dimension": {"total": even + odd, "even": even, "odd": odd},
        "even_subalgebra": "so(2) + sp(2n)",
        "rank": n + 1,
    }


def build_structure_json(n: int) -> dict:
    alg, basis, dec, table = compute_brackets(n, deformed=False)
    order = pbw_order(n)
    idx = {lab: i for i, lab in enumerate(order)}
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]

    realizations = {}
    for lab in order:
        words, frappat, vec = realization_words(n, lab)
        entry = {
            "standard_form": [{"words": list(w), "coeff": str(c)} for w, c in words],
            "frappat_form": frappat,
            "root": root_string(vec),
            "root_vector": vec,
            "parity": parity_of(lab),
        }
        if lab == f"H_{n + 1}":
            entry["note"] = f"Terminal Cartan; constant -1/2 makes it the super-symmetrised quadratic -(b_{n}^+b_{n}^- + 1/2)"
        realizations[lab] = entry

    sc = []
    for x in order:
        for y in order:
            c0, _, _ = table[(x, y)]
            for z, c in sorted(c0.items(), key=lambda kv: idx[kv[0]]):
                sc.append({"X": x, "Y": y, "Z": z, "coeff": str(c.scalar_value()), "sign_rule": "graded"})

    return {
        "schema_version": "5.0",
        "algebra": algebra_block(n),
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR)"},
            "bosons": {"n": n, "count": 2 * n, "labels": boson_labels, "parity": 0,
                       "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "{a_1^±, a_1^±} = 0  (i.e. (a_1^±)^2 = 0)"},
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"},
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; deformed to -gb·kappa in Schema 2)"},
        },
        "central_elements": {
            "K": {"parity": 0, "relation": "K = 1 (even central identity; excluded from basis and PBW ordering)",
                  "in_basis": False},
            "kappa": {"parity": 1, "relation": "kappa^2 = 0; kappa x = (-1)^{p(x)} x kappa (supercentral)",
                      "in_basis": False, "pbw_position": "first (kappa < odd < even)",
                      "description": "Odd nilpotent central element carrying the inhomogeneous deformation (Schema 2)"},
        },
        "basis": {
            "even": even_labels(n),
            "odd": odd_labels(n),
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
            "pbw_order": order,
        },
        "parity": {lab: parity_of(lab) for lab in order},
        "generator_realization": {
            "description": "Standard form: sum of normally ordered oscillator words with rational coefficients",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + boson_labels),
            "realizations": realizations,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date.today().isoformat(),
            "notation": "handover/notation.md",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras; arXiv:hep-th/9607161",
                "Bakalov and Sullivan (2017), arXiv:1612.09400",
            ],
        },
    }


def write_structure(n: int, data_dir: str = DATA_DIR) -> str:
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path, "w") as fh:
        json.dump(build_structure_json(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_structure(n)
        d = json.load(open(p))
        print(f"{p}: dim {d['algebra']['dimension']}, {len(d['structure_constants'])} non-zero structure constants")

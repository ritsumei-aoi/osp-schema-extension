"""Schema 1 generator for C(n+1) = osp(2|2n): basis, oscillator realization,
structure constants.  Writes data/C_{n}_structure.json (Issue I03).

Conventions: handover/notation.md ; schema: docs/json_schema_specification.md.

Usage:  python src/C_generators.py [--n 1 2 3] [--outdir data]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osc_algebra import (Element, LinearDecomposer, OscillatorAlgebra, Poly,  # noqa: E402
                         el_from_words, frac_str)

SCHEMA_VERSION = "5.0"


# --------------------------------------------------------------------------- basis


def even_basis(n: int) -> List[str]:
    out = [f"H_{k}" for k in range(1, n + 2)]
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    out += [f"E_2del{k}_p" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    out += [f"E_2del{k}_m" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return out


def odd_basis(n: int) -> List[str]:
    return [f"E_eps1_del{k}_{sig}{s}" for sig in "pm" for k in range(1, n + 1) for s in "pm"]


def pbw_order(n: int) -> List[str]:
    """PBW order of basis generators: [odd] < [even] (kappa and K excluded)."""
    return odd_basis(n) + even_basis(n)


def dimension(n: int) -> Dict[str, int]:
    even, odd = 2 * n * n + n + 1, 4 * n
    return {"total": even + odd, "even": even, "odd": odd}


# --------------------------------------------------------------------------- realizations

_SIGN = {"p": "+", "m": "-"}


def realization(label: str, n: int) -> Tuple[Element, str, int, Optional[dict]]:
    """Return (Element, frappat_form, parity, root) for a basis label."""
    def bos(k: int, s: str) -> str:
        return f"b_{k}_{s}"

    def root(eps: int, delta: Dict[int, int]) -> dict:
        return {"eps": eps, "delta": [delta.get(k, 0) for k in range(1, n + 1)]}

    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            el = el_from_words([(("a_1_p", "a_1_m"), 1), ((bos(1, "p"), bos(1, "m")), 1)])
            return el, "a_1^+ a_1^- + b_1^+ b_1^-", 0, None
        if 2 <= k <= n:
            el = el_from_words([((bos(k - 1, "p"), bos(k - 1, "m")), 1), ((bos(k, "p"), bos(k, "m")), -1)])
            return el, f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", 0, None
        if k == n + 1:
            el = el_from_words([((bos(n, "p"), bos(n, "m")), -1), ((), Fraction(-1, 2))])
            return el, f"-b_{n}^+ b_{n}^- - 1/2", 0, None
        raise ValueError(label)
    if label.startswith("E_2del"):
        body, s = label[len("E_2del"):].split("_")
        k = int(body)
        el = el_from_words([((bos(k, s), bos(k, s)), 1)])
        sg = _SIGN[s]
        return el, f"(b_{k}^{sg})^2", 0, root(0, {k: 2 if s == "p" else -2})
    if label.startswith("E_del"):
        parts = label[len("E_"):].split("_")      # ['del1', 'del2', 'pm']
        i, j, ss = int(parts[0][3:]), int(parts[1][3:]), parts[2]
        si, sj = ss[0], ss[1]
        el = el_from_words([((bos(i, si), bos(j, sj)), 1)])
        d = {i: 1 if si == "p" else -1, j: 1 if sj == "p" else -1}
        return el, f"b_{i}^{_SIGN[si]} b_{j}^{_SIGN[sj]}", 0, root(0, d)
    if label.startswith("E_eps1_del"):
        parts = label[len("E_eps1_"):].split("_")  # ['del2', 'pm']
        k, ss = int(parts[0][3:]), parts[1]
        sig, s = ss[0], ss[1]
        el = el_from_words([((f"a_1_{sig}", bos(k, s)), 1)])
        return el, f"a_1^{_SIGN[sig]} b_{k}^{_SIGN[s]}", 1, root(1 if sig == "p" else -1, {k: 1 if s == "p" else -1})
    raise ValueError(f"unknown label {label}")


# --------------------------------------------------------------------------- algebra model


class CAlgebra:
    """C(n+1) with its basis, realizations and an exact bracket."""

    def __init__(self, n: int, deformation=None):
        self.n = n
        self.alg = OscillatorAlgebra(n, deformation=deformation)
        self.even = even_basis(n)
        self.odd = odd_basis(n)
        self.labels = pbw_order(n)
        self.index = {lab: i for i, lab in enumerate(self.labels)}
        self.parity: Dict[str, int] = {}
        self.real: Dict[str, Element] = {}
        self.frappat: Dict[str, str] = {}
        self.root: Dict[str, Optional[dict]] = {}
        for lab in self.labels:
            el, ff, par, rt = realization(lab, n)
            self.real[lab], self.frappat[lab], self.parity[lab], self.root[lab] = el, ff, par, rt
        self.decomposer = LinearDecomposer(self.labels, [self.real[l] for l in self.labels], allow_K=True)

    def bracket_elements(self, x: str, y: str) -> Element:
        return self.alg.bracket(self.real[x], self.real[y], self.parity[x], self.parity[y])

    def bracket(self, x: str, y: str) -> Tuple[Dict[str, Poly], Dict[str, Poly]]:
        """Return (kappa^0 part, kappa^1 part) of [x, y}, each decomposed in basis + K."""
        full = self.bracket_elements(x, y)
        z0, z1 = self.alg.split_kappa(full)
        return self.decomposer.decompose(z0), self.decomposer.decompose(z1)

    def sort_key(self, lab: str) -> int:
        return self.index.get(lab, len(self.labels))   # "K" last


# --------------------------------------------------------------------------- Schema 1 JSON


def structure_constants(C: CAlgebra) -> List[dict]:
    recs = []
    for x in C.labels:
        for y in C.labels:
            z0, z1 = C.bracket(x, y)
            if z1:
                raise AssertionError("undeformed algebra produced kappa terms")
            for z, c in sorted(z0.items(), key=lambda kv: C.sort_key(kv[0])):
                if z == "K":
                    raise AssertionError(f"[{x},{y}] has a constant term: g is not closed")
                recs.append({"X": x, "Y": y, "Z": z, "coeff": frac_str(c.const_value()),
                             "sign_rule": "graded"})
    return recs


def algebra_block(n: int) -> dict:
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
        "alternative_notation": {"osp": f"osp(2|{2 * n})", "dimension_formula": "osp(2m|2n) with m=1"},
        "dimension_formula": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
        "dimension": dimension(n),
        "even_subalgebra": "so(2) x sp(2n)",
    }


def central_elements_block() -> dict:
    return {
        "kappa": {"label": "kappa", "parity": 1,
                  "relation": "kappa^2 = 0; x*kappa = (-1)^{p(x)} kappa*x",
                  "role": "odd central element of A = V + C K + C kappa; formal first-order parameter of the inhomogeneous deformation (Schema 2)",
                  "in_basis": False},
        "K": {"label": "K", "parity": 0, "relation": "K = 1 (identified with the scalar unit)",
              "role": "even central element; may appear as target label \"K\" in Schema 2-4 records",
              "in_basis": False},
        "pbw_position": "kappa < [odd] < [even]; K is excluded from the PBW basis",
    }


def build_schema1(n: int, today: Optional[str] = None) -> dict:
    C = CAlgebra(n)
    bos_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    realizations = {}
    for lab in C.labels:
        std = [{"words": list(w), "coeff": frac_str(c.const_value())}
               for w, c in sorted(C.real[lab].items(), key=lambda kv: (-len(kv[0]), kv[0]))]
        entry = {"standard_form": std, "frappat_form": C.frappat[lab], "parity": C.parity[lab],
                 "root": C.root[lab]}
        if lab == f"H_{n + 1}":
            entry["note"] = "Terminal Cartan H_{n+1} = [E_{2δ_n}/2, E_{-2δ_n}/2]; constant -1/2 from symmetrisation"
        if lab == "H_1":
            entry["note"] = "H_1 = {E_{ε-δ_1}, E_{δ_1-ε}} = (a_1^+a_1^- - 1/2) + (b_1^+b_1^- + 1/2)"
        realizations[lab] = entry
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": algebra_block(n),
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR); replaces the B(0,n) supplementary fermion a_0"},
            "bosons": {"n": n, "count": 2 * n, "labels": bos_labels, "parity": 0,
                       "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; see Schema 2 for the κ-deformation)"},
        },
        "central_elements": central_elements_block(),
        "basis": {
            "even": C.even, "odd": C.odd, "cartan": [f"H_{k}" for k in range(1, n + 2)],
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
            "pbw_order": C.labels,
        },
        "parity": {lab: C.parity[lab] for lab in C.labels},
        "generator_realization": {
            "description": "Standard form with PBW ordering of oscillator words",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + bos_labels),
            "realizations": realizations,
        },
        "structure_constants": structure_constants(C),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": today or _dt.date.today().isoformat(),
            "schema_specification": "docs/json_schema_specification.md",
            "notation": "handover/notation.md",
            "references": ["Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                           "docs/math/Cn1_definition.md"],
        },
    }


def write_json(obj: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
    args = ap.parse_args(argv)
    for n in args.n:
        doc = build_schema1(n)
        path = os.path.join(args.outdir, f"C_{n}_structure.json")
        write_json(doc, path)
        d = doc["algebra"]["dimension"]
        print(f"wrote {path}: C({n+1}) dim {d['even']}|{d['odd']} (total {d['total']}), "
              f"{len(doc['structure_constants'])} structure-constant records")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Schema 4: coboundary structure of C(n+1)  (Issue I07).

An odd linear map f: g -> g~ = g (+) C K is parameterized by
    f(Z_j) = sum_i phi_{ij} Z_i,     p(Z_i) = p(Z_j) + 1 (mod 2),
with Z_i ranging over the basis of g and, for odd Z_j, also over K (even, central).
Parameter label: phi__{Z_i}__{Z_j}  ("to" first, "from" second).

The coboundary (docs/math/C_coboundary_definition.md) is
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y]),
computed with the Schema 1 brackets ([X, K] = 0).  Every coefficient (delta f)_{XY}^Z is a linear
form in the phi parameters; delta f is an odd 2-cocycle with values in g~.

Usage:
    python src/C_coboundary.py           # writes data/C_{n}_coboundary.json for n = 1, 2, 3
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_generators as G  # noqa: E402
import verify_C_structure as V  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

LinForm = Dict[str, Fraction]           # phi label -> coefficient
Cochain = Dict[Tuple[str, str], Dict[str, LinForm]]   # (X, Y) -> Z -> linear form


def phi_label(to: str, frm: str) -> str:
    return f"phi__{to}__{frm}"


def coboundary_path(n: int) -> str:
    return os.path.join(DATA_DIR, f"C_{n}_coboundary.json")


class CoboundaryOperator:
    """delta on odd 1-cochains f: g -> g~ for the algebra of data/C_{n}_structure.json."""

    def __init__(self, n: int, include_K: bool = True):
        self.n = n
        self.include_K = include_K
        self.basis, self.parity, self.table, self.schema1 = V.load_structure(n)
        self.par = dict(self.parity)
        self.par["K"] = 0
        self.targets = self.basis + (["K"] if include_K else [])
        # parameters
        self.params: List[dict] = []
        for Zj in self.basis:
            for Zi in self.targets:
                if self.par[Zi] == 1 - self.par[Zj]:
                    self.params.append({"label": phi_label(Zi, Zj), "from": Zj, "to": Zi})
        self.param_labels = [p["label"] for p in self.params]
        # f(Z_j) as a vector of linear forms: f_vec[Zj] = {Zi: {phi: 1}}
        self.f_vec: Dict[str, Dict[str, LinForm]] = {Zj: {} for Zj in self.basis}
        for p in self.params:
            self.f_vec[p["from"]][p["to"]] = {p["label"]: Fraction(1)}

    # -- linear-form vector arithmetic ---------------------------------------
    @staticmethod
    def _acc(target: Dict[str, LinForm], Z: str, lf: LinForm, factor: Fraction) -> None:
        if factor == 0:
            return
        d = target.setdefault(Z, {})
        for lab, c in lf.items():
            d[lab] = d.get(lab, Fraction(0)) + factor * c

    def _bracket_left(self, X: str, vec: Dict[str, LinForm]) -> Dict[str, LinForm]:
        """[X, vec] where vec = sum_Z lf_Z Z (K is central)."""
        out: Dict[str, LinForm] = {}
        for Z, lf in vec.items():
            if Z == "K":
                continue
            for W, c in self.table.get((X, Z), {}).items():
                self._acc(out, W, lf, c)
        return out

    def _f_of_vector(self, vec: Dict[str, Fraction]) -> Dict[str, LinForm]:
        out: Dict[str, LinForm] = {}
        for Z, c in vec.items():
            for W, lf in self.f_vec[Z].items():
                self._acc(out, W, lf, c)
        return out

    @staticmethod
    def _clean(vec: Dict[str, LinForm]) -> Dict[str, LinForm]:
        out = {}
        for Z, lf in vec.items():
            lf2 = {lab: c for lab, c in lf.items() if c != 0}
            if lf2:
                out[Z] = lf2
        return out

    def delta_f(self, X: str, Y: str) -> Dict[str, LinForm]:
        """(delta f)(X, Y) as {Z: linear form in phi}."""
        pX, pY = self.par[X], self.par[Y]
        out: Dict[str, LinForm] = {}
        s1 = Fraction((-1) ** pX)
        for Z, lf in self._bracket_left(X, self.f_vec[Y]).items():
            self._acc(out, Z, lf, s1)
        s2 = Fraction(-((-1) ** ((pX + 1) * pY)))
        for Z, lf in self._bracket_left(Y, self.f_vec[X]).items():
            self._acc(out, Z, lf, s2)
        for Z, lf in self._f_of_vector(self.table.get((X, Y), {})).items():
            self._acc(out, Z, lf, Fraction(-1))
        return self._clean(out)

    def full(self) -> Cochain:
        out: Cochain = {}
        for X in self.basis:
            for Y in self.basis:
                d = self.delta_f(X, Y)
                if d:
                    out[(X, Y)] = d
        return out

    # -- evaluation ------------------------------------------------------------
    @staticmethod
    def evaluate(cochain: Cochain, phi: Dict[str, Fraction]):
        """Evaluate a symbolic cochain at numeric phi: (X, Y) -> {Z: Fraction}."""
        tab = {}
        for (X, Y), comp in cochain.items():
            d = {}
            for Z, lf in comp.items():
                c = sum((coef * phi.get(lab, Fraction(0)) for lab, coef in lf.items()), Fraction(0))
                if c != 0:
                    d[Z] = c
            if d:
                tab[(X, Y)] = d
        return tab


# ----------------------------------------------------------------------- schema
def build_schema4(n: int) -> dict:
    op = CoboundaryOperator(n, include_K=True)
    cochain = op.full()
    entries = []
    for (X, Y), comp in cochain.items():
        for Z, lf in comp.items():
            entries.append({"X": X, "Y": Y, "Z": Z,
                            "linear_form": {lab: str(c) for lab, c in sorted(lf.items())}})
    n_odd, n_even = 4 * n, 2 * n * n + n + 1
    return {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": op.schema1["algebra"],
        "source_structure": os.path.basename(G.structure_path(n)),
        "central_elements": op.schema1["central_elements"],
        "odd_linear_map": {
            "description": "General odd linear map f: g -> g~ = g (+) C K, f(Z_j) = sum_i phi_{ij} Z_i with p(Z_i) = p(Z_j) + 1. "
                           "K (even, central) is an allowed target for odd Z_j; f(K) = 0 is implicit (f is defined on g).",
            "parameter_label": "phi__{to}__{from}",
            "parameter_count": len(op.params),
            "parameter_count_formula": "dim_even*dim_odd (even->odd) + dim_odd*(dim_even+1) (odd->even or K) = "
                                       f"{n_even}*{n_odd} + {n_odd}*({n_even}+1)",
            "parameters": op.params,
        },
        "coboundary": {
            "description": "Coboundary (delta f)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y]); "
                           "entries give the Z-component as a linear form in the phi parameters.",
            "formula_source": "docs/math/C_coboundary_definition.md",
            "parity": "p(Z) = p(X) + p(Y) + 1 (mod 2)",
            "pair_convention": "All ordered pairs (X, Y) with non-zero (delta f)(X, Y) are listed.",
            "triviality_criterion": "gamma (Schema 2/3) is trivial iff gamma = delta f for some phi (equivalently gamma = -delta f, replacing f by -f).",
            "entries": entries,
            "summary": {
                "nonzero_entries": len(entries),
                "nonzero_pairs": len(cochain),
                "entries_with_Z_K": sum(1 for e in entries if e["Z"] == "K"),
                "total_phi_terms": sum(len(e["linear_form"]) for e in entries),
            },
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": _dt.date.today().isoformat(),
        },
    }


def load_schema4(n: int) -> dict:
    with open(coboundary_path(n)) as fh:
        return json.load(fh)


def cochain_from_schema4(d: dict) -> Cochain:
    out: Cochain = {}
    for e in d["coboundary"]["entries"]:
        out.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {lab: Fraction(c) for lab, c in e["linear_form"].items()}
    return out


def write_schema4(n: int) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = coboundary_path(n)
    with open(path, "w") as fh:
        json.dump(build_schema4(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_schema4(n)
        d = json.load(open(p))
        s = d["coboundary"]["summary"]
        print(f"n={n}: wrote {os.path.relpath(p, ROOT)}  phi params={d['odd_linear_map']['parameter_count']}  "
              f"entries={s['nonzero_entries']} pairs={s['nonzero_pairs']} K-entries={s['entries_with_Z_K']} "
              f"phi-terms={s['total_phi_terms']}  size={os.path.getsize(p) / 1e6:.2f} MB")

"""Shared helpers: load Schema 1 and work with the abstract Lie superalgebra g (+ K)."""
from __future__ import annotations

import json
import os
from fractions import Fraction
from typing import Dict, List, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")

Vec = Dict[str, Fraction]  # sparse vector on basis labels (+ "K")


class LieSuperalgebra:
    """Abstract bracket table read from C_{n}_structure.json.

    ``K`` is treated as an extra even central element: [X, K} = 0.
    """

    def __init__(self, doc: dict):
        self.doc = doc
        self.n = doc["algebra"]["n"]
        self.labels: List[str] = list(doc["basis"]["pbw_order"])
        self.index = {lab: i for i, lab in enumerate(self.labels)}
        self.parity: Dict[str, int] = {lab: int(doc["parity"][lab]) for lab in self.labels}
        self.parity["K"] = 0
        self.table: Dict[Tuple[str, str], Vec] = {}
        for e in doc["structure_constants"]:
            self.table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])

    @classmethod
    def load(cls, n: int, data_dir: str = DATA_DIR) -> "LieSuperalgebra":
        with open(os.path.join(data_dir, f"C_{n}_structure.json")) as fh:
            return cls(json.load(fh))

    # -- brackets --------------------------------------------------------------
    def bracket(self, X: str, Y: str) -> Vec:
        if X == "K" or Y == "K":
            return {}
        return self.table.get((X, Y), {})

    def bracket_vec(self, X: str, v: Vec) -> Vec:
        """[X, v} for v a sparse vector."""
        out: Vec = {}
        for W, c in v.items():
            for Z, cz in self.bracket(X, W).items():
                out[Z] = out.get(Z, Fraction(0)) + c * cz
        return {k: c for k, c in out.items() if c != 0}

    def bracket_vecs(self, u: Vec, v: Vec) -> Vec:
        out: Vec = {}
        for X, cx in u.items():
            for Z, cz in self.bracket_vec(X, v).items():
                out[Z] = out.get(Z, Fraction(0)) + cx * cz
        return {k: c for k, c in out.items() if c != 0}


def vec_add(u: Vec, v: Vec, scale: Fraction = Fraction(1)) -> Vec:
    out = dict(u)
    for k, c in v.items():
        out[k] = out.get(k, Fraction(0)) + scale * c
    return {k: c for k, c in out.items() if c != 0}


def frac_str(c: Fraction) -> str:
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


# ---------------------------------------------------------------------------
# Linear forms: sparse dict {symbol: Fraction}; the symbol "" is the constant term
# ---------------------------------------------------------------------------
LinForm = Dict[str, Fraction]


def lf_add(a: LinForm, b: LinForm, scale: Fraction = Fraction(1)) -> LinForm:
    out = dict(a)
    for k, c in b.items():
        out[k] = out.get(k, Fraction(0)) + scale * c
    return {k: c for k, c in out.items() if c != 0}


def lf_str(lf: LinForm) -> str:
    if not lf:
        return "0"
    parts = []
    for k in sorted(lf, key=lambda s: (s == "", s)):
        c = lf[k]
        term = frac_str(c) if k == "" else (f"{frac_str(c)}*{k}" if c not in (1, -1) else (k if c == 1 else f"-{k}"))
        parts.append(term)
    s = " + ".join(parts)
    return s.replace("+ -", "- ")


def lf_json(lf: LinForm) -> Dict[str, str]:
    return {k: frac_str(c) for k, c in sorted(lf.items())}


def lf_eval(lf: LinForm, values: Dict[str, Fraction]) -> Fraction:
    total = Fraction(0)
    for k, c in lf.items():
        total += c if k == "" else c * values[k]
    return total


# ---------------------------------------------------------------------------
# Sparse exact linear solver over Q
# ---------------------------------------------------------------------------
class SparseLinearSystem:
    """Equations  sum_j a_ij x_j = b_i  with exact rational arithmetic.

    Unknowns are identified by hashable names; each equation is a LinForm whose
    constant term "" is -(b_i), i.e. the equation reads  lf == 0.
    """

    def __init__(self):
        self.rows: List[LinForm] = []

    def add(self, lf: LinForm) -> None:
        if any(k != "" and c != 0 for k, c in lf.items()) or lf.get("", 0) != 0:
            self.rows.append(dict(lf))

    def solve(self):
        """Gaussian elimination.  Returns (status, pivots, reduced_rows, inconsistent_rows).

        status in {"consistent", "inconsistent"}.  ``pivots`` maps unknown -> reduced row
        expressing that unknown in terms of free unknowns and constant:
        x_p = -(sum_{free} c_f x_f + const).
        """
        pivots: Dict[str, LinForm] = {}
        inconsistent: List[LinForm] = []
        for row in self.rows:
            r = dict(row)
            # reduce by existing pivots
            for p in [k for k in r if k in pivots]:
                if p in r and r[p] != 0:
                    r = lf_add(r, pivots[p], -r[p])
            r = {k: c for k, c in r.items() if c != 0}
            vars_ = [k for k in r if k != ""]
            if not vars_:
                if r.get("", 0) != 0:
                    inconsistent.append(row)
                continue
            p = min(vars_)
            r = {k: c / r[p] for k, c in r.items()}
            # eliminate p from existing pivot rows
            for q, prow in list(pivots.items()):
                if p in prow and prow[p] != 0:
                    pivots[q] = lf_add(prow, r, -prow[p])
            pivots[p] = r
        status = "inconsistent" if inconsistent else "consistent"
        return status, pivots, inconsistent

    @staticmethod
    def particular_solution(pivots: Dict[str, LinForm], unknowns) -> Dict[str, Fraction]:
        """Set free unknowns to 0 and read off pivot values."""
        sol = {u: Fraction(0) for u in unknowns}
        for p, row in pivots.items():
            sol[p] = -row.get("", Fraction(0))  # free unknowns = 0
        return sol

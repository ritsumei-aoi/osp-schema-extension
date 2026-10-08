"""Schema 1 generator for C(n+1) = osp(2|2n): basis, PBW ordering, oscillator realization and
structure constants (handover/notation.md, docs/json_schema_specification.md §1).

Usage:  python src/C_generators.py [n ...]      (default: 1 2 3)  -> data/C_{n}_structure.json
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import OscillatorAlgebra, Poly, el_add, el_scale  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SIGN = {"p": "+", "m": "-"}


# ---------------------------------------------------------------------------
# Basis labels (handover/notation.md §3)
# ---------------------------------------------------------------------------
def cartan_labels(n):
    return [f"H_{k}" for k in range(1, n + 2)]


def even_labels(n):
    labs = cartan_labels(n)
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    labs += [f"E_2del{k}_p" for k in range(1, n + 1)]
    labs += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    labs += [f"E_2del{k}_m" for k in range(1, n + 1)]
    labs += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    labs += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    labs += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return labs


def odd_labels(n):
    return [f"E_eps1_del{k}_{sigma}{s}" for sigma in "pm" for k in range(1, n + 1) for s in "pm"]


def dimension(n):
    return {"even": 2 * n * n + n + 1, "odd": 4 * n, "total": 2 * n * n + 5 * n + 1}


# ---------------------------------------------------------------------------
# Oscillator realization of each generator
# ---------------------------------------------------------------------------
def realization(label: str, n: int):
    """Return (element dict word->Poly, frappat string, root string)."""
    one = Poly.const(1)
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            el = {("a_1_p", "a_1_m"): one, ("b_1_p", "b_1_m"): one}
            fr = "a_1^+ a_1^- + b_1^+ b_1^-"
        elif k <= n:
            el = {(f"b_{k-1}_p", f"b_{k-1}_m"): one, (f"b_{k}_p", f"b_{k}_m"): -one}
            fr = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
        else:  # k == n+1
            el = {(f"b_{n}_p", f"b_{n}_m"): -one, (): Poly.const(Fraction(-1, 2))}
            fr = f"-b_{n}^+ b_{n}^- - 1/2"
        return el, fr, "cartan"
    if label.startswith("E_2del"):
        body, s = label[len("E_2del"):].split("_")
        k = int(body)
        el = {(f"b_{k}_{s}", f"b_{k}_{s}"): one}
        return el, f"(b_{k}^{SIGN[s]})^2", f"{'' if s == 'p' else '-'}2del{k}"
    if label.startswith("E_eps1_del"):
        body, ss = label[len("E_eps1_del"):].split("_")
        k = int(body)
        sigma, s = ss[0], ss[1]
        el = {(f"a_1_{sigma}", f"b_{k}_{s}"): one}
        root = f"{'' if sigma == 'p' else '-'}eps1{SIGN[s]}del{k}"
        return el, f"a_1^{SIGN[sigma]} b_{k}^{SIGN[s]}", root
    if label.startswith("E_del"):
        _, di, dj, ss = label.split("_")
        i, j = int(di[3:]), int(dj[3:])
        s, t = ss[0], ss[1]
        el = {(f"b_{i}_{s}", f"b_{j}_{t}"): one}
        root = f"{'' if s == 'p' else '-'}del{i}{SIGN[t]}del{j}"
        return el, f"b_{i}^{SIGN[s]} b_{j}^{SIGN[t]}", root
    raise ValueError(label)


class CBasis:
    """Basis of C(n+1) with decomposition of normal-ordered quadratic elements into basis + K."""

    def __init__(self, n: int, deformed: bool = False, gb_values: dict | None = None):
        self.n = n
        self.alg = OscillatorAlgebra(n, deformed=deformed, gb_values=gb_values)
        self.even = even_labels(n)
        self.odd = odd_labels(n)
        self.labels = self.odd + self.even          # PBW order: kappa < odd < even
        self.parity = {lab: 1 for lab in self.odd}
        self.parity.update({lab: 0 for lab in self.even})
        self.real, self.frappat, self.root = {}, {}, {}
        for lab in self.labels:
            self.real[lab], self.frappat[lab], self.root[lab] = realization(lab, n)
        self._build_word_table()

    # -- word -> basis coordinates ------------------------------------------------
    def _build_word_table(self):
        n = self.n
        self.word_to_basis: dict = {}
        # non-Cartan generators are single words with coefficient 1
        for lab in self.labels:
            if not lab.startswith("H_"):
                (w, c), = self.real[lab].items()
                assert c == 1
                self.word_to_basis[w] = {lab: Fraction(1)}
        # Cartan block: words {a_1_p a_1_m, b_k_p b_k_m, ()} vs {H_1..H_{n+1}, K}
        cwords = [("a_1_p", "a_1_m")] + [(f"b_{k}_p", f"b_{k}_m") for k in range(1, n + 1)] + [()]
        rows = cartan_labels(n) + ["K"]
        M = []
        for r in rows:
            el = self.real[r] if r != "K" else {(): Poly.const(1)}
            M.append([el.get(w, Poly()).constant() for w in cwords])
        inv = _invert(M)           # inv[w_index][row_index]:  word = sum_r inv[w][r] * row_r
        for wi, w in enumerate(cwords):
            self.word_to_basis[w] = {rows[ri]: inv[wi][ri] for ri in range(len(rows)) if inv[wi][ri] != 0}

    def decompose(self, el: dict):
        """Split an element X + kappa*Y (X, Y quadratic) into (coords of X, coords of Y).

        Each coords dict maps basis label or 'K' -> Poly.
        """
        plain: dict = {}
        kap: dict = {}
        for w, c in el.items():
            if w and w[0] == "kappa":
                target, w2 = kap, w[1:]
            else:
                target, w2 = plain, w
            if w2 not in self.word_to_basis:
                raise ValueError(f"word {w2} is not in the quadratic span of the basis")
            for lab, coef in self.word_to_basis[w2].items():
                s = target.get(lab, Poly()) + c * coef
                if s:
                    target[lab] = s
                elif lab in target:
                    del target[lab]
        return plain, kap

    def bracket(self, x: str, y: str) -> dict:
        return self.alg.bracket(self.real[x], self.real[y], self.parity[x], self.parity[y])

    def structure_constants(self):
        """All ordered pairs: {(X, Y): {Z: Poly}} for the undeformed bracket, plus kappa part."""
        table, gamma = {}, {}
        for x in self.labels:
            for y in self.labels:
                plain, kap = self.decompose(self.bracket(x, y))
                if plain:
                    table[(x, y)] = plain
                if kap:
                    gamma[(x, y)] = kap
        return table, gamma


def _invert(M):
    """Exact inverse of a square matrix of Fractions (Gauss-Jordan)."""
    m = len(M)
    A = [[Fraction(M[i][j]) for j in range(m)] + [Fraction(int(i == j)) for j in range(m)] for i in range(m)]
    for col in range(m):
        piv = next(r for r in range(col, m) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for r in range(m):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    return [row[m:] for row in A]


# ---------------------------------------------------------------------------
# Schema 1 JSON
# ---------------------------------------------------------------------------
def build_schema1(n: int, date: str | None = None) -> dict:
    B = CBasis(n)
    table, gamma = B.structure_constants()
    assert not gamma, "undeformed algebra must not produce kappa terms"
    for (x, y), comps in table.items():
        assert "K" not in comps, f"constant term in [{x},{y}]: {comps}"
        for z, c in comps.items():
            assert c.is_constant()
            assert B.parity[z] == (B.parity[x] + B.parity[y]) % 2
    dim = dimension(n)
    assert len(B.even) == dim["even"] and len(B.odd) == dim["odd"]
    date = date or datetime.date.today().isoformat()

    realizations = {}
    for lab in B.labels:
        entry = {
            "standard_form": [{"words": list(w), "coeff": str(c.constant())}
                              for w, c in sorted(B.real[lab].items(), key=lambda kv: (-len(kv[0]), kv[0]))],
            "frappat_form": B.frappat[lab],
            "parity": B.parity[lab],
            "root": B.root[lab],
        }
        if lab == f"H_{n+1}":
            entry["note"] = "Terminal Cartan; constant written as a multiple of K = 1"
        realizations[lab] = entry

    sc = []
    for x in B.labels:
        for y in B.labels:
            if (x, y) in table:
                for z in B.labels:
                    if z in table[(x, y)]:
                        sc.append({"X": x, "Y": y, "Z": z, "coeff": str(table[(x, y)][z].constant()),
                                   "sign_rule": "graded"})

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "even_subalgebra": f"so(2) x sp({2*n})",
            "dimension": {"total": dim["total"], "even": dim["even"], "odd": dim["odd"],
                          "formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"}},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR); replaces the supplementary fermion a_0 of B(0,n)"},
            "bosons": {"n": n, "count": 2 * n, "labels": [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"],
                       "parity": 0, "description": "Bosonic oscillators b_k^± with k=1,...,n"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermionic pair",
                "relations": {"same_type": "{a_1^±, a_1^±} = 0  (equivalently (a_1^±)^2 = 0)",
                              "conjugate_pair": "{a_1^-, a_1^+} = 1"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; see Schema 2 for the κ-deformation)"},
            "central_elements_relations": {"K": "K = 1 commutes with everything",
                                           "kappa": "kappa^2 = 0; [kappa, b] = 0; {kappa, a_1^±} = 0 (odd super-central)"},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                      "role": "Odd nilpotent central element carrying the inhomogeneous deformation (Schema 2)",
                      "in_basis": False},
            "K": {"label": "K", "parity": 0, "relation": "K = 1",
                  "role": "Even central element; identified with the scalar 1. Constants produced by a_1^+ a_1^- and b_k^+ b_k^- are recorded as multiples of K",
                  "in_basis": False},
        },
        "basis": {
            "even": B.even,
            "odd": B.odd,
            "pbw_order": B.labels,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
            "roots": {lab: B.root[lab] for lab in B.labels},
        },
        "parity": {lab: B.parity[lab] for lab in B.labels},
        "generator_realization": {
            "description": "Standard form: normal-ordered oscillator words with rational coefficients",
            "ordering": ", ".join(B.alg.gens),
            "realizations": realizations,
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date,
            "conventions": "handover/notation.md",
            "references": ["Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
                           "docs/math/Cn1_definition.md"],
        },
    }


def write_schema1(n: int, out_dir: str = DATA_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"C_{n}_structure.json")
    with open(path, "w") as fh:
        json.dump(build_schema1(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        p = write_schema1(n)
        d = build_schema1(n)
        print(f"{p}: dim {d['algebra']['dimension']}, {len(d['structure_constants'])} structure-constant entries")

"""Schema 1 (algebra structure) generator for C(n+1) = osp(2|2n).

Usage:  python3 src/C_generators.py            # writes data/C_{1,2,3}_structure.json
Conventions: handover/notation.md, docs/json_schema_specification.md.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_osc import Lin, OscAlgebra, split_kappa  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SCHEMA_VERSION = "5.0"
K_LABEL = "K"


# --------------------------------------------------------------------------- basis
def even_basis(n: int) -> list[str]:
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    out = [f"H_{k}" for k in range(1, n + 2)]
    out += [f"E_2del{k}_p" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    out += [f"E_2del{k}_m" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return out


def odd_basis(n: int) -> list[str]:
    return [f"E_eps1_del{k}_{t}" for t in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def ordered_basis(n: int) -> list[str]:
    """PBW order: kappa < [odd] < [even] (kappa, K not included)."""
    return odd_basis(n) + even_basis(n)


def parity_of(label: str) -> int:
    return 1 if label.startswith("E_eps1_") else 0


def realization(n: int, label: str) -> list[tuple[tuple, Fraction]]:
    """Standard (normal-ordered) form of a generator: list of (word, coeff)."""
    half = Fraction(1, 2)
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            return [(("a_1_p", "a_1_m"), Fraction(1)), (("b_1_p", "b_1_m"), Fraction(1))]
        if k <= n:
            return [((f"b_{k-1}_p", f"b_{k-1}_m"), Fraction(1)), ((f"b_{k}_p", f"b_{k}_m"), Fraction(-1))]
        assert k == n + 1
        return [((f"b_{n}_p", f"b_{n}_m"), Fraction(-1)), ((), -half)]
    if label.startswith("E_2del"):
        k, s = label[len("E_2del"):].split("_")
        return [((f"b_{k}_{s}", f"b_{k}_{s}"), Fraction(1))]
    if label.startswith("E_eps1_del"):
        k, t = label[len("E_eps1_del"):].split("_")
        return [((f"a_1_{t[0]}", f"b_{k}_{t[1]}"), Fraction(1))]
    if label.startswith("E_del"):
        _, i, j, t = label.split("_")  # E, del{i}, del{j}, t
        i, j = i[3:], j[3:]
        w = (f"b_{i}_{t[0]}", f"b_{j}_{t[1]}")
        return [(w, Fraction(1))]
    raise ValueError(label)


def frappat_form(n: int, label: str) -> str:
    def osc(x):
        if x == ():
            return ""
        return " ".join(f"{w[0]}_{w[2]}^{'+' if w[4] == 'p' else '-'}" for w in x)
    parts = []
    for w, c in realization(n, label):
        mono = osc(w)
        if not mono:
            term = str(abs(c))
        elif abs(c) == 1:
            term = mono
        else:
            term = f"{abs(c)} {mono}"
        parts.append(("- " if c < 0 else "+ ") + term)
    s = " ".join(parts)
    return s[2:] if s.startswith("+ ") else "-" + s[2:]


# --------------------------------------------------------------------------- decomposition
class CAlgebra:
    """Basis, realizations and exact decomposition of oscillator quadratics for C(n+1)."""

    def __init__(self, n: int, deformed: bool = False):
        self.n = n
        self.osc = OscAlgebra(n, deformed=deformed)
        self.basis = ordered_basis(n)
        self.index = {b: i for i, b in enumerate(self.basis)}
        self.par = [parity_of(b) for b in self.basis]
        self.elem = {b: {w: Lin.const(c) for w, c in realization(n, b)} for b in self.basis}
        self._build_decomposer()

    def _build_decomposer(self):
        cols = self.basis + [K_LABEL]
        vecs = [self.elem[b] for b in self.basis] + [{(): Lin.const(1)}]
        monos = sorted({w for v in vecs for w in v}, key=lambda w: (len(w), w))
        self.monos = monos
        mi = {w: i for i, w in enumerate(monos)}
        M = sympy.zeros(len(monos), len(cols))
        for j, v in enumerate(vecs):
            for w, c in v.items():
                M[mi[w], j] = sympy.Rational(c["1"].numerator, c["1"].denominator)
        assert M.rank() == len(cols), "basis realizations are linearly dependent"
        L = (M.T * M).inv() * M.T  # exact left inverse
        self.cols = cols
        self.mono_index = mi
        self.M = M
        self.left_inv = [
            {monos[r]: Fraction(int(L[j, r].p), int(L[j, r].q)) for r in range(len(monos)) if L[j, r] != 0}
            for j in range(len(cols))
        ]
        self.col_vecs = vecs

    def decompose(self, elem: dict) -> dict:
        """Express a kappa-free normal-ordered element in basis + K. Returns {label: Lin}."""
        for w in elem:
            if w not in self.mono_index:
                raise ValueError(f"monomial {w} not in span of basis+K")
        out = {}
        for j, row in enumerate(self.left_inv):
            c = Lin()
            for w, a in row.items():
                if w in elem:
                    c = c + elem[w].scale(a)
            if c:
                out[self.cols[j]] = c
        # residual check: sum_j out_j * col_j == elem
        recon: dict = {}
        for lab, c in out.items():
            for w, a in self.col_vecs[self.cols.index(lab)].items():
                recon[w] = recon.get(w, Lin()) + c.scale(a["1"])
        for w in set(recon) | set(elem):
            if (recon.get(w, Lin()) + -(elem.get(w, Lin()))):
                raise ValueError(f"element not in span of basis+K (monomial {w})")
        return out

    def raw_bracket(self, x: str, y: str) -> dict:
        return self.osc.bracket(self.elem[x], self.elem[y], parity_of(x), parity_of(y))

    def bracket0(self, x: str, y: str) -> dict:
        """Undeformed bracket of two basis elements, decomposed in the basis (+K)."""
        p0, p1 = split_kappa(self.raw_bracket(x, y))
        assert not p1, "kappa term in undeformed algebra"
        return self.decompose(p0)


# --------------------------------------------------------------------------- Schema 1
def structure_constants(alg: CAlgebra) -> list[dict]:
    out = []
    for x in alg.basis:
        for y in alg.basis:
            dec = alg.bracket0(x, y)
            if K_LABEL in dec:
                raise AssertionError(f"[{x},{y}] has a K component: basis not closed")
            for z in alg.basis:
                if z in dec:
                    out.append({"X": x, "Y": y, "Z": z, "coeff": dec[z].to_str(), "sign_rule": "graded"})
    return out


def algebra_block(n: int) -> dict:
    even, odd = 2 * n * n + n + 1, 4 * n
    return {
        "family": "C",
        "m": 1,
        "n": n,
        "cartan_type": f"C({n + 1})",
        "alternative_notation": {
            "osp": f"osp(2|{2 * n})",
            "dimension_formula": "osp(2m|2n) with m=1; even = 2n^2 + n + 1, odd = 4n",
        },
        "dimension": {"total": even + odd, "even": even, "odd": odd},
    }


def central_elements_block() -> dict:
    return {
        "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                  "role": "odd central element carrying the inhomogeneous deformation (Schema 2+)"},
        "K": {"label": "K", "parity": 0, "value": "1",
              "role": "even central element; identified with the scalar 1, excluded from basis/PBW"},
    }


def build_structure(n: int) -> dict:
    alg = CAlgebra(n)
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
    realizations = {}
    for b in alg.basis:
        entry = {
            "standard_form": [{"words": list(w), "coeff": str(c)} for w, c in realization(n, b)],
            "frappat_form": frappat_form(n, b),
            "parity": parity_of(b),
        }
        if b == f"H_{n + 1}":
            entry["note"] = "Terminal Cartan H_{n+1}; constant -1/2 from super-symmetrization"
        realizations[b] = entry
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": algebra_block(n),
        "oscillator_generators": {
            "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR)"},
            "bosons": {"count": 2 * n, "n": n, "labels": bos, "parity": 0,
                       "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "{a_1^±, a_1^±} = 0  (a_1^± a_1^± = 0)"},
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"},
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed; deformed in Schema 2: "
                                 "[b_j^s, a_1^σ] = -gb_{σ,j,s} kappa)"
            },
        },
        "central_elements": central_elements_block(),
        "basis": {
            "even": even_basis(n),
            "odd": odd_basis(n),
            "ordered": alg.basis,
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": {b: parity_of(b) for b in alg.basis},
        "generator_realization": {
            "description": "Standard form with PBW ordering of oscillator words",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + bos),
            "realizations": realizations,
        },
        "structure_constants": structure_constants(alg),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"],
            "notation": "handover/notation.md",
        },
    }


def write_json(obj: dict, name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_structure(n)
        p = write_json(s, f"C_{n}_structure.json")
        d = s["algebra"]["dimension"]
        print(f"n={n}: {d['even']}|{d['odd']} ({d['total']}), "
              f"{len(s['structure_constants'])} structure constants -> {os.path.relpath(p)}")


if __name__ == "__main__":
    main()

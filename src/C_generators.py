"""Schema 1 generator for C(n+1) = osp(2|2n): basis, realizations, structure constants.

Usage:  python3 src/C_generators.py            (writes data/C_{1,2,3}_structure.json)
Conventions: handover/notation.md, docs/json_schema_specification.md §1.
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_oscillator import (ONE, Oscillators, bracket, elem_add, lin, lin_add, lin_scale,
                         solve_square)  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PM = {"p": "+", "m": "-"}


# ---------------------------------------------------------------- basis
def pairs(n):
    return [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]


def even_basis(n):
    ev = [f"H_{k}" for k in range(1, n + 2)]
    ev += [f"E_2del{k}_p" for k in range(1, n + 1)]
    ev += [f"E_del{i}_del{j}_pp" for i, j in pairs(n)]
    ev += [f"E_2del{k}_m" for k in range(1, n + 1)]
    ev += [f"E_del{i}_del{j}_mm" for i, j in pairs(n)]
    ev += [f"E_del{i}_del{j}_pm" for i, j in pairs(n)]
    ev += [f"E_del{i}_del{j}_mp" for i, j in pairs(n)]
    return ev


def odd_basis(n):
    return [f"E_eps1_del{k}_{sg}" for sg in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def full_basis(n):
    """Global PBW basis order: odd + even."""
    return odd_basis(n) + even_basis(n)


def parity_map(n):
    return {**{x: 1 for x in odd_basis(n)}, **{x: 0 for x in even_basis(n)}}


def realization_terms(n):
    """label -> list of (word labels, Fraction coeff, )  and frappat strings."""
    R, F = {}, {}
    R["H_1"] = [(["a_1_p", "a_1_m"], 1), (["b_1_p", "b_1_m"], 1)]
    F["H_1"] = "a_1^+ a_1^- + b_1^+ b_1^-"
    for k in range(2, n + 1):
        R[f"H_{k}"] = [([f"b_{k-1}_p", f"b_{k-1}_m"], 1), ([f"b_{k}_p", f"b_{k}_m"], -1)]
        F[f"H_{k}"] = f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-"
    R[f"H_{n+1}"] = [([f"b_{n}_p", f"b_{n}_m"], -1), ([], Fraction(-1, 2))]
    F[f"H_{n+1}"] = f"-b_{n}^+ b_{n}^- - 1/2"
    for k in range(1, n + 1):
        for s in "pm":
            R[f"E_2del{k}_{s}"] = [([f"b_{k}_{s}", f"b_{k}_{s}"], 1)]
            F[f"E_2del{k}_{s}"] = f"(b_{k}^{PM[s]})^2"
    for i, j in pairs(n):
        for s in "pm":
            for t in "pm":
                R[f"E_del{i}_del{j}_{s}{t}"] = [([f"b_{i}_{s}", f"b_{j}_{t}"], 1)]
                F[f"E_del{i}_del{j}_{s}{t}"] = f"b_{i}^{PM[s]} b_{j}^{PM[t]}"
    for k in range(1, n + 1):
        for sg in "pm":
            for s in "pm":
                R[f"E_eps1_del{k}_{sg}{s}"] = [([f"a_1_{sg}", f"b_{k}_{s}"], 1)]
                F[f"E_eps1_del{k}_{sg}{s}"] = f"a_1^{PM[sg]} b_{k}^{PM[s]}"
    return {k: [(w, Fraction(c)) for w, c in v] for k, v in R.items()}, F


# ---------------------------------------------------------------- algebra object
class CAlgebra:
    """Realization of C(n+1) inside U(A); optionally with the gb deformation."""

    def __init__(self, n, deformed=False, gb_values=None):
        self.n = n
        self.osc = Oscillators(n, deformed=deformed, gb_values=gb_values)
        self.basis = full_basis(n)
        self.idx = {x: i for i, x in enumerate(self.basis)}
        self.parity = parity_map(n)
        self.real_terms, self.frappat = realization_terms(n)
        self.gen = {}
        for x, terms in self.real_terms.items():
            el = {}
            for words, c in terms:
                w = tuple(self.osc.index[l] for l in words)
                for key, cc in self.osc.normal_order(w).items():
                    el = elem_add(el, {key: {k: v * c for k, v in cc.items()}})
            self.gen[x] = el
        self._build_decomposer()

    def _build_decomposer(self):
        """Columns = generators + K in the normal-ordered monomials (1, a+a-, ab, bb')."""
        L = len(self.osc.labels)
        mons = [()] + [(i, j) for i in range(L) for j in range(i, L) if not (i == j and i < 2)]
        self.monomials = mons
        self.mon_idx = {m: i for i, m in enumerate(mons)}
        cols = self.basis + ["K"]
        assert len(mons) == len(cols), (len(mons), len(cols))
        N = len(cols)
        M = [[Fraction(0)] * N for _ in mons]
        for c, x in enumerate(cols):
            el = {(0, ()): lin(1)} if x == "K" else self.gen[x]
            for (k, w), co in el.items():
                assert k == 0
                M[self.mon_idx[w]][c] = co.get(ONE, Fraction(0))
        # column j of M^{-1} = M^{-1} e_j, stored sparsely
        inv_cols = solve_square(M, [[lin(int(i == j)) for i in range(N)] for j in range(N)])
        self._inv_cols = [[(i, v[ONE]) for i, v in enumerate(col) if v] for col in inv_cols]
        self._cols = cols

    def decompose(self, el):
        """Return {kappa_power: {label|'K': Lin}} for an element of span(g) + C K."""
        out = {}
        for kp in (0, 1):
            acc = {}
            for (k, w), c in el.items():
                if k != kp:
                    continue
                if w not in self.mon_idx:
                    raise ValueError(f"word {w} outside the quadratic span")
                for i, v in self._inv_cols[self.mon_idx[w]]:
                    acc[i] = lin_add(acc.get(i, {}), lin_scale(c, v))
            res = {self._cols[i]: v for i, v in sorted(acc.items()) if v}
            if res:
                out[kp] = res
        return out

    def bracket_labels(self, x, y):
        return bracket(self.osc, self.gen[x], self.gen[y], self.parity[x], self.parity[y])


def make_algebra(n, deformed=False, gb_values=None):
    return CAlgebra(n, deformed=deformed, gb_values=gb_values)


# ---------------------------------------------------------------- Schema 1
def structure_constants(alg):
    """List of (X, Y, Z, Fraction) for undeformed brackets, all ordered pairs."""
    out = []
    for x in alg.basis:
        for y in alg.basis:
            dec = alg.decompose(alg.bracket_labels(x, y))
            part = dec.get(0, {})
            if "K" in part:
                raise AssertionError(f"K component in [{x},{y}]")
            if 1 in dec and not alg.osc.deformed:
                raise AssertionError("kappa term in undeformed bracket")
            for z in alg.basis:
                if z in part:
                    c = part[z]
                    assert set(c) == {ONE}
                    out.append((x, y, z, c[ONE]))
    return out


def build_schema1(n):
    alg = make_algebra(n)
    ev, od = even_basis(n), odd_basis(n)
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    real = {}
    for x in alg.basis:
        entry = {
            "standard_form": [{"words": w, "coeff": str(c)} for w, c in alg.real_terms[x]],
            "frappat_form": alg.frappat[x],
            "parity": alg.parity[x],
        }
        if x == f"H_{n+1}":
            entry["note"] = "Terminal Cartan; constant -1/2 makes span closed without K"
        real[x] = entry
    sc = structure_constants(alg)
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
            "dimension": {"total": len(ev) + len(od), "even": len(ev), "odd": len(od)},
        },
        "oscillator_generators": {
            "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR)"},
            "bosons": {"count": 2 * n, "n": n, "labels": bos, "parity": 0,
                       "description": "Bosonic oscillators b_i^± with i=1,...,n (CCR)"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "{a_1^±, a_1^±} = 0"},
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"},
            },
            "mixed_commutators": {
                "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed); = -gb_{σ,j,s} κ in the deformation of Schema 2"},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                      "role": "odd central element; carries the inhomogeneous deformation [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)"},
            "K": {"label": "K", "parity": 0, "value": "1",
                  "role": "even central element (Bakalov–Sullivan); identified with 1, excluded from basis/PBW"},
        },
        "basis": {"even": ev, "odd": od,
                  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
                  "global_index_order": "odd + even"},
        "parity": dict(alg.parity),
        "generator_realization": {
            "description": "Standard form with oscillator normal ordering",
            "ordering": ", ".join(alg.osc.labels),
            "realizations": real,
        },
        "structure_constants": [
            {"X": x, "Y": y, "Z": z, "coeff": str(c), "sign_rule": "graded"} for x, y, z, c in sc],
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"],
            "conventions": "handover/notation.md",
        },
    }


def write_json(obj, name):
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_schema1(n)
        p = write_json(s, f"C_{n}_structure.json")
        print(f"n={n}: dim={s['algebra']['dimension']}, nonzero structure constants="
              f"{len(s['structure_constants'])} -> {p}")


if __name__ == "__main__":
    main()

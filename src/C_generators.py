"""Basis, oscillator realization and Schema 1 structure constants for C(n+1) = osp(2|2n).

Conventions: handover/notation.md.  Usage:  python src/C_generators.py [n ...]
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import (OscillatorAlgebra, elem_add_into,  # noqa: E402
                                poly_add_into, poly_const)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SIGNS = ("p", "m")
SIGN_TXT = {"p": "+", "m": "-"}


def dims(n):
    even = 2 * n * n + n + 1
    odd = 4 * n
    return {"total": even + odd, "even": even, "odd": odd}


# ------------------------------------------------------------------ basis


def even_basis(n):
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    out = [f"H_{k}" for k in range(1, n + 2)]
    out += [f"E_2del{k}_p" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    out += [f"E_2del{k}_m" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    out += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return out


def odd_basis(n):
    return [f"E_eps1_del{k}_{s}" for s in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def pbw_basis(n):
    """Full PBW order: odd < even (kappa and K are not basis elements)."""
    return odd_basis(n) + even_basis(n)


def parity_map(n):
    p = {x: 0 for x in even_basis(n)}
    p.update({x: 1 for x in odd_basis(n)})
    return p


# ------------------------------------------------------------ realization


def realization_terms(n, label):
    """Return (standard_form terms [(words, Fraction)], frappat string)."""
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            return ([(["a_1_p", "a_1_m"], 1), (["b_1_p", "b_1_m"], 1)],
                    "a_1^+ a_1^- + b_1^+ b_1^-")
        if k == n + 1:
            return ([([f"b_{n}_p", f"b_{n}_m"], -1), ([], Fraction(-1, 2))],
                    f"-b_{n}^+ b_{n}^- - 1/2")
        return ([([f"b_{k-1}_p", f"b_{k-1}_m"], 1), ([f"b_{k}_p", f"b_{k}_m"], -1)],
                f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-")
    if label.startswith("E_2del"):
        k, s = label[6:].split("_")
        return ([([f"b_{k}_{s}", f"b_{k}_{s}"], 1)], f"(b_{k}^{SIGN_TXT[s]})^2")
    if label.startswith("E_eps1_del"):
        k, ss = label[10:].split("_")
        sig, s = ss
        return ([([f"a_1_{sig}", f"b_{k}_{s}"], 1)],
                f"a_1^{SIGN_TXT[sig]} b_{k}^{SIGN_TXT[s]}")
    if label.startswith("E_del"):
        _, a, b, ss = label.split("_")
        i, j = int(a[3:]), int(b[3:])
        s1, s2 = ss
        # i < j, bosons with different index commute; standard order is by index
        return ([([f"b_{i}_{s1}", f"b_{j}_{s2}"], 1)],
                f"b_{i}^{SIGN_TXT[s1]} b_{j}^{SIGN_TXT[s2]}")
    raise ValueError(label)


class CAlgebra:
    """Basis + exact decomposition of oscillator polynomials into g ⊕ CK."""

    def __init__(self, n, deformed=False):
        self.n = n
        self.alg = OscillatorAlgebra(n, deformed=deformed)
        self.basis = pbw_basis(n)
        self.index = {x: i for i, x in enumerate(self.basis)}
        self.parity = parity_map(n)
        self.real = {}
        for x in self.basis:
            terms, _ = realization_terms(n, x)
            e = {}
            for words, c in terms:
                poly_add_into(e.setdefault(tuple(words), {}), poly_const(c))
            # check standard form is already normal ordered
            norm = {}
            for w, p in e.items():
                elem_add_into(norm, self.alg.normal(w), p)
            assert norm == e, f"realization of {x} not in standard form"
            self.real[x] = e
        self._build_inverse()

    def _build_inverse(self):
        cols = self.basis + ["K"]
        vecs = {x: {w: p[()] for w, p in self.real[x].items()} for x in self.basis}
        vecs["K"] = {(): Fraction(1)}
        monos = sorted({w for v in vecs.values() for w in v}, key=lambda w: (len(w), w))
        if len(monos) != len(cols):
            raise RuntimeError("monomial count != basis size + 1")
        # Gauss-Jordan on augmented [M | I]  (rows = monomials)
        N = len(cols)
        M = [[vecs[c].get(m, Fraction(0)) for c in cols] + [Fraction(int(r == i)) for i in range(N)]
             for r, m in enumerate(monos)]
        for c in range(N):
            piv = next(r for r in range(c, N) if M[r][c] != 0)
            M[c], M[piv] = M[piv], M[c]
            pv = M[c][c]
            M[c] = [v / pv for v in M[c]]
            for r in range(N):
                if r != c and M[r][c] != 0:
                    f = M[r][c]
                    M[r] = [a - f * b for a, b in zip(M[r], M[c])]
        # inverse: basis coordinate c = sum_m inv[c][m] * coeff(m)
        self.monos = monos
        self.inv = {}
        for ci, c in enumerate(cols):
            row = {monos[mi]: M[ci][N + mi] for mi in range(N) if M[ci][N + mi] != 0}
            self.inv[c] = row
        self.mono_set = set(monos)

    def decompose(self, A):
        """Oscillator element (no kappa) -> {basis label or 'K': Poly}."""
        for w in A:
            if w not in self.mono_set:
                raise ValueError(f"monomial {w} outside g ⊕ CK")
        out = {}
        for c, row in self.inv.items():
            acc = {}
            for m, v in row.items():
                if m in A:
                    poly_add_into(acc, A[m], v)
            if acc:
                out[c] = acc
        return out

    def bracket_decomposed(self, X, Y):
        """Return (undeformed part, kappa part) of [X,Y} decomposed in g ⊕ CK."""
        res = self.alg.bracket(self.real[X], self.real[Y], self.parity[X], self.parity[Y])
        r0, r1 = self.alg.split_kappa(res)
        return self.decompose(r0), self.decompose(r1)


def frac_str(c):
    return str(Fraction(c))


def structure_constants(calg):
    """All non-zero [X,Y} = sum coeff Z over ordered pairs; asserts no K/kappa part."""
    out = []
    for X in calg.basis:
        for Y in calg.basis:
            d0, d1 = calg.bracket_decomposed(X, Y)
            assert not d1, "kappa appeared in undeformed bracket"
            if "K" in d0:
                raise RuntimeError(f"K component in [{X},{Y}]")
            for Z in calg.basis:
                if Z in d0:
                    c = d0[Z][()]
                    out.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(c),
                                "sign_rule": "graded"})
    return out


def build_schema1(n, date=None):
    calg = CAlgebra(n)
    d = dims(n)
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in SIGNS]
    real = {}
    for x in calg.basis:
        terms, frappat = realization_terms(n, x)
        entry = {"standard_form": [{"words": w, "coeff": frac_str(c)} for w, c in terms],
                 "frappat_form": frappat, "parity": calg.parity[x]}
        if x == f"H_{n+1}":
            entry["note"] = "Terminal Cartan; constant -1/2 from Weyl ordering"
        if x == f"E_2del{n}_p" or x == f"E_2del{n}_m":
            entry["note"] = "Chevalley simple generator of Cn1_definition.md is 1/2 of this element"
        real[x] = entry
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})",
                                     "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n",
                                   "total": "2n^2 + 5n + 1"},
            "dimension": d,
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR)"},
            "bosons": {"n": n, "count": 2 * n, "labels": bos, "parity": 0,
                       "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "same_type": "{a_1^+, a_1^+} = 0, {a_1^-, a_1^-} = 0"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0 (undeformed; deformed version in Schema 2)"},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                      "role": "odd central element; carries the inhomogeneous deformation"},
            "K": {"label": "K", "parity": 0, "relation": "K = 1",
                  "role": "even central element identified with 1; excluded from basis/PBW"},
        },
        "basis": {
            "even": even_basis(n), "odd": odd_basis(n), "ordering": calg.basis,
            "ordering_convention": ("PBW: κ < [odd: pp < pm < mp < mm, each by k] < [even: H, "
                                    "E_2del_p, E_del_del_pp, E_2del_m, E_del_del_mm, "
                                    "E_del_del_pm, E_del_del_mp]  (K = 1 excluded)"),
        },
        "parity": calg.parity,
        "generator_realization": {
            "description": "Standard form: words in oscillator order, Weyl-ordered generators",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + bos),
            "realizations": real,
        },
        "structure_constants": structure_constants(calg),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date or datetime.date.today().isoformat(),
            "conventions": "handover/notation.md",
            "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"],
        },
    }


def write_json(obj, path):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def main(ns):
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in ns:
        s = build_schema1(n)
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        write_json(s, path)
        print(f"n={n}: dim={s['algebra']['dimension']}, "
              f"{len(s['structure_constants'])} non-zero structure constants -> {path}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])

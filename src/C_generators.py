"""Basis and structure-constant generator for C(n+1) = osp(2|2n) (Schema 1).

usage: python src/C_generators.py   # writes data/C_{1,2,3}_structure.json
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from oscalg import AM, AP, OscAlgebra, b_letter, letter_name, make_decomposer  # noqa: E402

SIGNS = ("pp", "pm", "mp", "mm")


def basis_labels(n):
    """(even, odd) label lists in the PBW order of handover/notation.md."""
    odd = [f"E_eps1_del{k}_{sg}" for sg in SIGNS for k in range(1, n + 1)]
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    even = [f"H_{k}" for k in range(1, n + 2)]
    even += [f"E_2del{k}_p" for k in range(1, n + 1)]
    even += [f"E_del{i}_del{j}_pp" for i, j in pairs]
    even += [f"E_2del{k}_m" for k in range(1, n + 1)]
    even += [f"E_del{i}_del{j}_mm" for i, j in pairs]
    even += [f"E_del{i}_del{j}_pm" for i, j in pairs]
    even += [f"E_del{i}_del{j}_mp" for i, j in pairs]
    return even, odd


def realization(label, n):
    """Oscillator realization: dict {word tuple: Fraction} (normal-ordered words)."""
    F = Fraction
    bp = lambda k: b_letter(k, "p")  # noqa: E731
    bm = lambda k: b_letter(k, "m")  # noqa: E731
    if label.startswith("H_"):
        k = int(label[2:])
        if k == 1:
            r = {(AP, AM): F(1), (bp(1), bm(1)): F(1)}
        elif k == n + 1:
            r = {(bp(n), bm(n)): F(-1), (): F(-1, 2)}
        else:
            r = {(bp(k - 1), bm(k - 1)): F(1), (bp(k), bm(k)): F(-1)}
        return r
    if label.startswith("E_2del"):
        k = int(label[6:-2])
        s = label[-1]
        return {(b_letter(k, s),) * 2: F(1)}
    if label.startswith("E_eps1_del"):
        body = label[len("E_eps1_del"):]
        k, sg = body.split("_")
        return {(AP if sg[0] == "p" else AM, b_letter(int(k), sg[1])): F(1)}
    if label.startswith("E_del"):
        body = label[len("E_del"):]
        i, rest = body.split("_del")
        j, sg = rest.split("_")
        return {(b_letter(int(i), sg[0]), b_letter(int(j), sg[1])): F(1)}
    raise ValueError(label)


class CAlgebra:
    def __init__(self, n, gb=None):
        self.n = n
        self.even, self.odd = basis_labels(n)
        self.labels = self.odd + self.even  # PBW order: odd < even
        self.parity = {l: (1 if l in self.odd else 0) for l in self.labels}
        self.real = {l: realization(l, n) for l in self.labels}
        self.osc = OscAlgebra(gb)
        self.decompose = make_decomposer([self.real[l] for l in self.labels])

    def bracket_words(self, X, Y):
        return self.osc.bracket(self.real[X], self.parity[X], self.real[Y], self.parity[Y])

    def bracket(self, X, Y):
        """[X,Y} in the undeformed algebra -> {label: coeff}; raises if not closed."""
        coeffs, resid = self.decompose(self.bracket_words(X, Y))
        if resid:
            raise ValueError(f"bracket [{X},{Y}] leaves residual {resid}")
        return {self.labels[i]: c for i, c in coeffs.items()}


def structure_constants(alg):
    sc = []
    for X in alg.labels:
        for Y in alg.labels:
            for Z, c in alg.bracket(X, Y).items():
                sc.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
    return sc


def word_label(w):
    return [letter_name(x) for x in w]


def schema1(n):
    alg = CAlgebra(n)
    even, odd = alg.even, alg.odd
    bl = [f"b_{i}_{s}" for i in range(1, n + 1) for s in "pm"]
    reals = {}
    for l in alg.labels:
        reals[l] = {
            "standard_form": [
                {"words": word_label(w), "coeff": str(c)} for w, c in sorted(alg.real[l].items())
            ],
            "parity": alg.parity[l],
        }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})",
            "alternative_notation": {"osp": f"osp(2|{2 * n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension": {"total": len(alg.labels), "even": len(even), "odd": len(odd)},
            "dimension_formula": {"even": "2n^2+n+1", "odd": "4n", "total": "2n^2+5n+1"},
        },
        "oscillator_generators": {
            "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^±"},
            "bosons": {"count": 2 * n, "n": n, "labels": bl, "parity": 0,
                       "description": "Bosonic oscillators b_i^±, i=1..n"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {"relations": {
                "anticommutator": "{a_1^-, a_1^+} = 1", "nilpotent": "(a_1^+)^2 = (a_1^-)^2 = 0"}},
            "bosonic_commutators": {"relations": {
                "same_type": "[b_i^±, b_j^±] = 0", "conjugate_pair": "[b_i^-, b_j^+] = δ_ij"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "central_elements": {
            "kappa": {"parity": 1, "relation": "kappa^2 = 0", "description": "odd central, nilpotent"},
            "K": {"parity": 0, "description": "even central identity, identified with scalar 1; not a basis element"},
        },
        "basis": {"odd": odd, "even": even,
                  "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 excluded)"},
        "parity": dict(alg.parity),
        "generator_realization": {
            "description": "Weyl-ordered quadratics in normal-ordered words",
            "ordering": "a_1_p, a_1_m, " + ", ".join(bl),
            "realizations": reals,
        },
        "structure_constants": structure_constants(alg),
        "metadata": {
            "generated_by": "src/C_generators.py", "generation_date": "2026-10-06", "n": n,
            "bracket_convention": "[X,Y} = XY - (-1)^{p(X)p(Y)} YX",
            "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"],
        },
    }


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "data")
    for n in (1, 2, 3):
        d = schema1(n)
        with open(os.path.join(out, f"C_{n}_structure.json"), "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        print(n, d["algebra"]["dimension"], len(d["structure_constants"]))


if __name__ == "__main__":
    main()

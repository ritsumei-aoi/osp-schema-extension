"""Structure constants for C(n+1) = osp(2|2n) from an oscillator realization.

Each basis element is a polynomial in the oscillators a_1_p, a_1_m (CAR,
{a_1_m, a_1_p} = 1) and b_k_p, b_k_m (CCR, [b_k_m, b_l_p] = delta_kl).
Products are normal-ordered exactly (rational arithmetic), and brackets are
expressed in the basis by solving a linear system. Any constant term that
the brackets produce is reported as the central element K (K = 1).

Labels and PBW ordering follow handover/notation.md (I01).
"""

import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import sympy


FERMION = "a_1_"


class Oscillators:
    """Normal ordering for the oscillators of C(n+1), with n bosonic modes."""

    def __init__(self, n):
        self.n = n
        self.symbols = ["a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.symbols += [f"b_{k}_p", f"b_{k}_m"]
        self.order = {s: i for i, s in enumerate(self.symbols)}

    @staticmethod
    def is_fermion(sym):
        return sym.startswith(FERMION)

    def contraction(self, x, y):
        """Value of x*y - (sign) * y*x, i.e. the c-number part of the swap.

        For fermions this is the anticommutator {x, y}; for bosons it is
        the commutator [x, y]. Mixed pairs commute, so the value is 0.
        """
        if self.is_fermion(x) and self.is_fermion(y):
            return Fraction(1) if {x, y} == {"a_1_p", "a_1_m"} else Fraction(0)
        if self.is_fermion(x) or self.is_fermion(y):
            return Fraction(0)
        if x[2:-2] != y[2:-2]:  # different modes commute
            return Fraction(0)
        if x.endswith("_m") and y.endswith("_p"):
            return Fraction(1)
        if x.endswith("_p") and y.endswith("_m"):
            return Fraction(-1)
        return Fraction(0)

    @lru_cache(maxsize=None)
    def _normal(self, word):
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and self.is_fermion(x):
                return ()  # a^2 = 0 for a fermion
            if self.order[x] > self.order[y]:
                # xy = s * yx + c, with s = -1 for fermions, +1 for bosons/mixed
                sign = -1 if (self.is_fermion(x) and self.is_fermion(y)) else 1
                swapped = word[:i] + (y, x) + word[i + 2:]
                contracted = word[:i] + word[i + 2:]
                out = {}
                for w, c in self._normal(swapped):
                    out[w] = out.get(w, 0) + sign * c
                c0 = self.contraction(x, y)
                if c0 != 0:
                    for w, c in self._normal(contracted):
                        out[w] = out.get(w, 0) + c0 * c
                return tuple((w, c) for w, c in out.items() if c != 0)
        return ((word, Fraction(1)),)

    def normal(self, poly):
        """Normal-order a polynomial given as {word: coeff}."""
        out = {}
        for word, c in poly.items():
            for w, d in self._normal(word):
                out[w] = out.get(w, 0) + c * d
        return {w: c for w, c in out.items() if c != 0}


def mul(osc, A, B):
    prod = {}
    for wa, ca in A.items():
        for wb, cb in B.items():
            prod[wa + wb] = prod.get(wa + wb, 0) + ca * cb
    return osc.normal(prod)


def supercomm(osc, A, pA, B, pB):
    """Graded commutator [A, B} = AB - (-1)^(pA pB) BA."""
    sign = -1 if (pA * pB) % 2 else 1
    ab = mul(osc, A, B)
    ba = mul(osc, B, A)
    out = dict(ab)
    for w, c in ba.items():
        out[w] = out.get(w, 0) - sign * c
    return {w: c for w, c in out.items() if c != 0}


def basis(n):
    """Return a list of (label, parity, polynomial) in the PBW order of I01.

    Odd block first, then even block, as fixed in handover/notation.md.
    Bilinears are Weyl-symmetrized so that the constant parts are fixed.
    """
    F = Fraction
    odd = []
    for k in range(1, n + 1):
        odd += [
            (f"E_eps1_del{k}_pp", {("a_1_p", f"b_{k}_p"): F(1)}),
            (f"E_eps1_del{k}_pm", {("a_1_p", f"b_{k}_m"): F(1)}),
            (f"E_eps1_del{k}_mp", {("a_1_m", f"b_{k}_p"): F(1)}),
            (f"E_eps1_del{k}_mm", {("a_1_m", f"b_{k}_m"): F(1)}),
        ]
    even = [("H_eps", {("a_1_p", "a_1_m"): F(1), (): F(-1, 2)})]
    for k in range(1, n + 1):
        even.append((f"H_{k}", {(f"b_{k}_p", f"b_{k}_m"): F(1), (): F(1, 2)}))
    # Order per handover/notation.md: E_2del_p, mixed pp/pm/mp, E_2del_m, mixed mm.
    for k in range(1, n + 1):
        even.append((f"E_2del{k}_p", {(f"b_{k}_p", f"b_{k}_p"): F(1, 2)}))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append((f"E_del{i}_del{j}_pp", {(f"b_{i}_p", f"b_{j}_p"): F(1)}))
            even.append((f"E_del{i}_del{j}_pm", {(f"b_{i}_p", f"b_{j}_m"): F(1)}))
            even.append((f"E_del{i}_del{j}_mp", {(f"b_{i}_m", f"b_{j}_p"): F(1)}))
    for k in range(1, n + 1):
        even.append((f"E_2del{k}_m", {(f"b_{k}_m", f"b_{k}_m"): F(1, 2)}))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append((f"E_del{i}_del{j}_mm", {(f"b_{i}_m", f"b_{j}_m"): F(1)}))
    return [(l, 1, p) for l, p in odd] + [(l, 0, p) for l, p in even]


def structure(n):
    """Compute brackets [X, Y} = sum_Z c_Z Z + c_K K for all pairs of basis labels."""
    osc = Oscillators(n)
    elems = basis(n)
    labels = [e[0] for e in elems]
    parity = {e[0]: e[1] for e in elems}
    polys = {e[0]: osc.normal(e[2]) for e in elems}

    # Linear system: columns = basis elements plus K (the scalar 1).
    polys_all = dict(polys, K={(): Fraction(1)})
    cols = labels + ["K"]
    monomials = sorted({m for p in polys_all.values() for m in p} | {()})
    A = sympy.Matrix(
        [[to_sympy(polys_all[c].get(m, Fraction(0))) for c in cols] for m in monomials]
    )

    brackets = {}
    for i, X in enumerate(labels):
        for Y in labels[i:]:
            comm = supercomm(osc, polys[X], parity[X], polys[Y], parity[Y])
            if not comm:
                continue
            rhs = sympy.Matrix([to_sympy(comm.get(m, Fraction(0))) for m in monomials])
            sol, params = A.gauss_jordan_solve(rhs)
            assert not params, f"basis not unique for [{X},{Y}]"
            terms = {c: from_sympy(s) for c, s in zip(cols, sol) if s != 0}
            if terms:
                brackets[(X, Y)] = terms
    return labels, parity, brackets


def to_sympy(q):
    return sympy.Rational(q.numerator, q.denominator)


def from_sympy(s):
    return Fraction(int(s.p), int(s.q))


def to_json(n):
    labels, parity, brackets = structure(n)
    osc = Oscillators(n)
    entries = []
    for (X, Y), terms in brackets.items():
        for Z, c in terms.items():
            entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c), "sign_rule": "graded"})
    realization = {}
    for label, _, poly in basis(n):
        realization[label] = {
            "standard_form": [
                {"words": list(w), "coeff": str(c)} for w, c in osc.normal(poly).items()
            ],
            "parity": parity[label],
        }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1; even = 2n^2+n+1, odd = 4n",
            },
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair with CAR",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": osc.symbols[2:],
                "description": "Bosonic oscillators b_k^± with k=1,...,n",
            },
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {"relations": {"anticommutator": "{a_1^-, a_1^+} = 1"}},
            "bosonic_commutators": {"relations": {"conjugate_pair": "[b_k^-, b_l^+] = δ_{kl}"}},
            "mixed_commutators": {"boson_fermion": "[b_k^±, a_1^±] = 0"},
        },
        "central_elements": {
            "kappa": {"parity": 1, "relation": "κ^2 = 0"},
            "K": {"parity": 0, "relation": "K = 1"},
        },
        "basis": {
            "even": [l for l in labels if parity[l] == 0],
            "odd": [l for l in labels if parity[l] == 1],
            "ordering_convention": "PBW: odd < even (see handover/notation.md)",
        },
        "parity": {l: parity[l] for l in labels},
        "generator_realization": realization,
        "structure_constants": entries,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "arXiv:hep-th/9607161",
            ],
        },
    }


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(exist_ok=True)
    for n in (1, 2, 3):
        out = data_dir / f"C_{n}_structure.json"
        out.write_text(json.dumps(to_json(n), indent=2) + "\n")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()

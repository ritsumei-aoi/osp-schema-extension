"""Basis, realization and structure constants of C(n+1) = osp(2|2n).

Conventions are fixed in handover/notation.md.  Layer 1 (Schema 1) JSON is
written to data/C_{n}_structure.json.
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_oscillator import OscAlgebra, KAPPA, A_P, A_M, b_index, gen_names  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNS = ("p", "m")


def even_basis(n):
    out = [f"H_{k}" for k in range(1, n + 2)]
    out += [f"E_2del{k}_p" for k in range(1, n + 1)]
    out += [f"E_del{i}_del{j}_pp" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    out += [f"E_2del{k}_m" for k in range(1, n + 1)]
    for t in ("mm", "pm", "mp"):
        out += [f"E_del{i}_del{j}_{t}" for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    return out


def odd_basis(n):
    return [f"E_eps1_del{k}_{t}" for t in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def all_labels(n):
    """PBW order of the g part: odd block first, then even block."""
    return odd_basis(n) + even_basis(n)


def parity_map(n):
    p = {x: 0 for x in even_basis(n)}
    p.update({x: 1 for x in odd_basis(n)})
    return p


def realization(n):
    """Normal-ordered oscillator words {label: {word: Fraction}} (words = index tuples).

    Cartan elements are Weyl-symmetrised so that g closes without constants:
      h_a = a+ a- - 1/2,  h_k = b_k+ b_k- + 1/2,
      H_1 = h_a + h_1, H_k = h_{k-1} - h_k, H_{n+1} = -h_n.
    """
    F = Fraction

    def bp(k):
        return b_index(k, "p")

    def bm(k):
        return b_index(k, "m")

    R = {}
    ha = {(A_P, A_M): F(1), (): F(-1, 2)}
    h = {k: {(bp(k), bm(k)): F(1), (): F(1, 2)} for k in range(1, n + 1)}

    def comb(*terms):
        out = {}
        for c, d in terms:
            for w, v in d.items():
                out[w] = out.get(w, 0) + c * v
        return {w: v for w, v in out.items() if v != 0}

    R["H_1"] = comb((1, ha), (1, h[1]))
    for k in range(2, n + 1):
        R[f"H_{k}"] = comb((1, h[k - 1]), (-1, h[k]))
    R[f"H_{n + 1}"] = comb((-1, h[n]))
    for k in range(1, n + 1):
        R[f"E_2del{k}_p"] = {(bp(k), bp(k)): F(1)}
        R[f"E_2del{k}_m"] = {(bm(k), bm(k)): F(1)}
        for l in range(k + 1, n + 1):
            R[f"E_del{k}_del{l}_pp"] = {(bp(k), bp(l)): F(1)}
            R[f"E_del{k}_del{l}_pm"] = {(bp(k), bm(l)): F(1)}
            R[f"E_del{k}_del{l}_mp"] = {(bm(k), bp(l)): F(1)}
            R[f"E_del{k}_del{l}_mm"] = {(bm(k), bm(l)): F(1)}
        for e, a in (("p", A_P), ("m", A_M)):
            for d in SIGNS:
                R[f"E_eps1_del{k}_{e}{d}"] = {(a, b_index(k, d)): F(1)}
    return R


class Decomposer:
    """Expand an oscillator element (no kappa) in the Weyl-symmetrised basis of g."""

    def __init__(self, n):
        self.n = n
        self.real = realization(n)
        self.single = {}
        for lab, d in self.real.items():
            if not lab.startswith("H_"):
                (w,) = d.keys()
                self.single[w] = lab
        self.ha_word = (A_P, A_M)

    def decompose(self, E):
        """Return ({label: coeff}, residual_constant)."""
        n = self.n
        out = {}
        alpha = Fraction(0)
        beta = {k: Fraction(0) for k in range(1, n + 1)}
        const = Fraction(0)
        for w, c in E.items():
            if w in self.single:
                out[self.single[w]] = out.get(self.single[w], 0) + c
            elif w == ():
                const += c
            elif w == self.ha_word:
                alpha += c
            elif len(w) == 2 and w[0] >= 3 and (w[0] - 3) % 2 == 0 and w[1] == w[0] + 1:
                beta[(w[0] - 3) // 2 + 1] += c
            else:
                raise ValueError(f"word {w} outside g")
        # diagonal part = alpha h_a + sum beta_k h_k + residual constant
        resid = const + alpha / 2 - sum(beta.values()) / 2
        coef_h = dict(beta)
        coef_h[1] += -alpha          # h_a = H_1 - h_1
        coefH = {k: Fraction(0) for k in range(1, n + 2)}
        coefH[1] += alpha
        for k in range(1, n + 1):    # h_k = -(H_{k+1} + ... + H_{n+1})
            for j in range(k + 1, n + 2):
                coefH[j] += -coef_h[k]
        for k in range(1, n + 2):
            if coefH[k] != 0:
                out[f"H_{k}"] = out.get(f"H_{k}", 0) + coefH[k]
        return {k: v for k, v in out.items() if v != 0}, resid


def split_kappa(E):
    """Split E = E0 + kappa*E1 (kappa is leftmost after normal ordering)."""
    E0, E1 = {}, {}
    for w, c in E.items():
        if w and w[0] == KAPPA:
            E1[w[1:]] = c
        else:
            E0[w] = c
    return E0, E1


def structure_constants(n, gb=None):
    """Return (sc0, sc1, resid): undeformed brackets, kappa-parts as
    {(X, Y): {Z: coeff}}, and residual central constants (kappa*1 parts)."""
    alg = OscAlgebra(n, gb)
    dec = Decomposer(n)
    real = dec.real
    par = parity_map(n)
    labels = all_labels(n)
    sc0, sc1, resid = {}, {}, {}
    for X in labels:
        for Y in labels:
            R = alg.bracket(real[X], real[Y], par[X], par[Y])
            R0, R1 = split_kappa(R)
            for tag, part, store in (("0", R0, sc0), ("k", R1, sc1)):
                if not part:
                    continue
                d, r = dec.decompose(part)
                if r != 0:
                    resid[(X, Y, tag)] = r
                if d:
                    store[(X, Y)] = d
    return sc0, sc1, resid


def fstr(c):
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def realization_json(n):
    real = realization(n)
    names = gen_names(n)
    par = parity_map(n)
    out = {}
    for lab, d in real.items():
        out[lab] = {
            "standard_form": [
                {"words": [names[g] for g in w], "coeff": fstr(c)}
                for w, c in sorted(d.items(), key=lambda t: (len(t[0]), t[0]))
            ],
            "parity": par[lab],
        }
    return out


def build_schema1(n):
    sc0, sc1, resid = structure_constants(n)
    assert not sc1 and not resid, "undeformed algebra must close without kappa/constants"
    even, odd = even_basis(n), odd_basis(n)
    entries = []
    for X in all_labels(n):
        for Y in all_labels(n):
            for Z, c in sc0.get((X, Y), {}).items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": fstr(c), "sign_rule": "graded"})
    bl = [f"b_{k}_{s}" for k in range(1, n + 1) for s in SIGNS]
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {"osp": f"osp(2|{2 * n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension": {"total": len(even) + len(odd), "even": len(even), "odd": len(odd)},
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^+, a_1^- (CAR).",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": bl,
                "description": "Bosonic oscillators b_i^± with i=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for the standard pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1", "same_type": "(a_1^±)^2 = 0"},
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"},
            },
            "mixed_commutators": {
                "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed); deformed in Schema 2 as -gb_{σ,j,s} κ"
            },
        },
        "central_elements": {
            "kappa": {"parity": 1, "nilpotent": True, "relation": "kappa^2 = 0", "description": "Odd central element."},
            "K": {"parity": 0, "value": "1", "description": "Even central element, identified with the scalar 1; not a basis element."},
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd: E_eps1_del{k}_pp,pm,mp,mm] < [even: H, E_2del_p, E_del_pp, E_2del_m, E_del_mm, E_del_pm, E_del_mp]  (K = 1 is excluded)",
        },
        "parity": parity_map(n),
        "generator_realization": {
            "description": "Standard (normal-ordered, Weyl-symmetrised Cartan) form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(bl),
            "realizations": realization_json(n),
        },
        "structure_constants": entries,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-06",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def write_all(ns=(1, 2, 3), out_dir=DATA_DIR):
    os.makedirs(out_dir, exist_ok=True)
    for n in ns:
        path = os.path.join(out_dir, f"C_{n}_structure.json")
        with open(path, "w") as fh:
            json.dump(build_schema1(n), fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("wrote", path)


if __name__ == "__main__":
    write_all()

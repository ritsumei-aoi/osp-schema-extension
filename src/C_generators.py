"""Schema 1 generator for C(n+1) = osp(2|2n): basis, realization, structure constants.

Usage:  python3 src/C_generators.py        -> writes data/C_{n}_structure.json, n = 1, 2, 3
Conventions: handover/notation.md; format: docs/json_schema_specification.md (Schema 1).
"""
import datetime
import json
import os
import sys
from fractions import Fraction
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import OscillatorAlgebra  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SIGN = {"p": "+", "m": "-"}


def frac_str(c):
    return str(Fraction(c))


# ---------------------------------------------------------------- basis
def even_basis(n):
    pairs = list(combinations(range(1, n + 1), 2))
    return ([f"H_{k}" for k in range(1, n + 2)]
            + [f"E_2del{k}_p" for k in range(1, n + 1)]
            + [f"E_del{i}_del{j}_pp" for i, j in pairs]
            + [f"E_2del{k}_m" for k in range(1, n + 1)]
            + [f"E_del{i}_del{j}_mm" for i, j in pairs]
            + [f"E_del{i}_del{j}_pm" for i, j in pairs]
            + [f"E_del{i}_del{j}_mp" for i, j in pairs])


def odd_basis(n):
    return [f"E_eps1_del{k}_{s}" for s in ("pp", "pm", "mp", "mm") for k in range(1, n + 1)]


def global_order(n):
    """PBW order kappa < [odd] < [even]; index order for all layers."""
    return odd_basis(n) + even_basis(n)


def parity_map(n):
    return {**{x: 1 for x in odd_basis(n)}, **{x: 0 for x in even_basis(n)}}


# ---------------------------------------------------------------- realization
def realization_terms(n):
    """label -> (list of (word tuple, Fraction)), frappat string, root string."""
    R = {}
    one, mone = Fraction(1), Fraction(-1)
    R["H_1"] = ([(("a_1_p", "a_1_m"), one), (("b_1_p", "b_1_m"), one)],
                "a_1^+ a_1^- + b_1^+ b_1^-", "0")
    for k in range(2, n + 1):
        R[f"H_{k}"] = ([((f"b_{k-1}_p", f"b_{k-1}_m"), one), ((f"b_{k}_p", f"b_{k}_m"), mone)],
                       f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", "0")
    R[f"H_{n+1}"] = ([((f"b_{n}_p", f"b_{n}_m"), mone), ((), Fraction(-1, 2))],
                     f"-b_{n}^+ b_{n}^- - 1/2", "0")
    for k in range(1, n + 1):
        for s in ("p", "m"):
            R[f"E_2del{k}_{s}"] = ([((f"b_{k}_{s}", f"b_{k}_{s}"), one)],
                                   f"(b_{k}^{SIGN[s]})^2", f"{'' if s == 'p' else '-'}2del{k}")
    for i, j in combinations(range(1, n + 1), 2):
        for s, t in (("p", "p"), ("m", "m"), ("p", "m"), ("m", "p")):
            root = f"{'' if s == 'p' else '-'}del{i}{SIGN[t]}del{j}"
            R[f"E_del{i}_del{j}_{s}{t}"] = ([((f"b_{i}_{s}", f"b_{j}_{t}"), one)],
                                            f"b_{i}^{SIGN[s]} b_{j}^{SIGN[t]}", root)
    for k in range(1, n + 1):
        for s in ("p", "m"):
            for t in ("p", "m"):
                root = f"{'' if s == 'p' else '-'}eps1{SIGN[t]}del{k}"
                R[f"E_eps1_del{k}_{s}{t}"] = ([((f"a_1_{s}", f"b_{k}_{t}"), one)],
                                              f"a_1^{SIGN[s]} b_{k}^{SIGN[t]}", root)
    return R


def realizations(n, alg=None):
    """label -> normal-ordered element of U(A)."""
    alg = alg or OscillatorAlgebra(n)
    return {lab: alg.normalize({w: c for w, c in terms})
            for lab, (terms, _, _) in realization_terms(n).items()}


# ---------------------------------------------------------------- decomposition
class Decomposer:
    """Express a kappa-free quadratic element as sum_Z c_Z Z + c_K * 1 (exact)."""

    def __init__(self, n):
        self.n = n
        self.labels = global_order(n) + ["K"]
        reals = realizations(n)
        reals["K"] = {(): Fraction(1)}
        monos = sorted({w for e in reals.values() for w in e}, key=lambda w: (len(w), w))
        if len(monos) != len(self.labels):
            raise RuntimeError("basis + K is not square in the monomial space")
        self.monos = monos
        m_index = {w: i for i, w in enumerate(monos)}
        N = len(monos)
        # augmented matrix [A | I], columns of A = basis vectors in monomial coordinates
        A = [[Fraction(0)] * N for _ in range(N)]
        for j, lab in enumerate(self.labels):
            for w, c in reals[lab].items():
                A[m_index[w]][j] = c
        self.inv = _invert(A)
        self.m_index = m_index

    def decompose(self, elem):
        coords = {}
        vec = [Fraction(0)] * len(self.monos)
        for w, c in elem.items():
            if w not in self.m_index:
                raise ValueError(f"monomial {w} is not in g + C K")
            vec[self.m_index[w]] += c
        for j, lab in enumerate(self.labels):
            v = sum((self.inv[j][i] * vec[i] for i in range(len(vec)) if vec[i]), Fraction(0))
            if v:
                coords[lab] = v
        return coords


def _invert(A):
    N = len(A)
    M = [row[:] + [Fraction(int(i == j)) for j in range(N)] for i, row in enumerate(A)]
    for col in range(N):
        piv = next(r for r in range(col, N) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        p = M[col][col]
        M[col] = [x / p for x in M[col]]
        for r in range(N):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[N:] for row in M]


# ---------------------------------------------------------------- structure constants
def structure_constants(n):
    """{(X, Y): {Z: coeff}} for all ordered pairs with non-zero bracket (undeformed)."""
    alg = OscillatorAlgebra(n)
    reals = realizations(n, alg)
    dec = Decomposer(n)
    basis = global_order(n)
    sc = {}
    for X in basis:
        for Y in basis:
            br = alg.bracket(reals[X], reals[Y])
            coords = dec.decompose(br)
            if coords.pop("K", 0) != 0:
                raise RuntimeError(f"undeformed bracket [{X},{Y}] has a K-component")
            if coords:
                sc[(X, Y)] = coords
    return sc


def build_schema1(n, date=None):
    date = date or datetime.date.today().isoformat()
    ev, od = even_basis(n), odd_basis(n)
    par = parity_map(n)
    basis = global_order(n)
    idx = {x: i for i, x in enumerate(basis)}
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
    R = realization_terms(n)
    real_json = {}
    for lab in basis:
        terms, fr, root = R[lab]
        entry = {"standard_form": [{"words": list(w), "coeff": frac_str(c)} for w, c in terms],
                 "frappat_form": fr, "root": root, "parity": par[lab]}
        if lab == f"H_{n+1}":
            entry["note"] = "Terminal Cartan H_{n+1}; constant term from symmetric ordering"
        real_json[lab] = entry
    sc = structure_constants(n)
    sc_list = []
    for (X, Y) in sorted(sc, key=lambda p: (idx[p[0]], idx[p[1]])):
        for Z in sorted(sc[(X, Y)], key=idx.get):
            sc_list.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(sc[(X, Y)][Z]),
                            "sign_rule": "graded"})
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
            "dimension": {"total": len(basis), "even": len(ev), "odd": len(od)},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic pair a_1^± (CAR); replaces the B(0,n) supplementary fermion a_0."},
            "bosons": {"n": n, "count": 2 * n, "labels": bos, "parity": 0,
                       "description": "Bosonic oscillators b_k^± with k=1,...,n (CCR)."},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = K = 1",
                              "same_type": "{a_1^±, a_1^±} = 0, i.e. (a_1^±)^2 = 0"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij} K = δ_{ij}"}},
            "mixed_commutators": {
                "boson_fermion": "[b_j^s, a_1^σ] = 0 (undeformed). The inhomogeneous deformation (Schema 2) sets [b_j^s, a_1^σ] = -gb_{σ,j,s} κ."},
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1,
                      "relations": ["kappa is central (supercommutes with everything)", "kappa^2 = 0"],
                      "role": "Odd central element carrying the inhomogeneous deformation: [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)."},
            "K": {"label": "K", "parity": 0, "value": "1",
                  "role": "Even central element of the pre-oscillator algebra (value of [b^-,b^+] and {a^-,a^+}); identified with 1, excluded from basis and PBW ordering."},
        },
        "basis": {"even": ev, "odd": od,
                  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)",
                  "global_order": basis},
        "parity": {x: par[x] for x in basis},
        "generator_realization": {
            "description": "Standard form (normal-ordered oscillator words) with K = 1",
            "ordering": ", ".join(["a_1_p", "a_1_m"] + bos),
            "realizations": real_json},
        "structure_constants": sc_list,
        "metadata": {
            "generated_by": "src/C_generators.py", "generation_date": date,
            "conventions": "handover/notation.md",
            "references": ["Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                           "Bakalov and Sullivan (2017)"]},
    }


def write_json(obj, name):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return path


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_schema1(n)
        p = write_json(s, f"C_{n}_structure.json")
        print(f"n={n}: dim={s['algebra']['dimension']}, nonzero structure constants="
              f"{len(s['structure_constants'])} -> {os.path.relpath(p)}")


if __name__ == "__main__":
    main()

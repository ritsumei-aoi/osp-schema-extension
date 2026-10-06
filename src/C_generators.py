"""Schema 1 generator for C(n+1) = osp(2|2n).

Builds the basis (PBW order of handover/notation.md), the oscillator
realizations, and the structure constants, and writes data/C_{n}_structure.json.

Usage:  python3 src/C_generators.py [n ...]      (default: 1 2 3)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator import OscillatorAlgebra, from_standard_form  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SIGNS = ("p", "m")


def frac_str(c):
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


# ---------------------------------------------------------------- basis ----
def pairs(n):
    return [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]


def build_basis(n):
    even = [f"H_{k}" for k in range(1, n + 2)]
    even += [f"E_2del{k}_p" for k in range(1, n + 1)]
    even += [f"E_del{i}_del{j}_pp" for i, j in pairs(n)]
    even += [f"E_2del{k}_m" for k in range(1, n + 1)]
    even += [f"E_del{i}_del{j}_mm" for i, j in pairs(n)]
    even += [f"E_del{i}_del{j}_pm" for i, j in pairs(n)]
    even += [f"E_del{i}_del{j}_mp" for i, j in pairs(n)]
    odd = [f"E_eps1_del{k}_{sg}{s}" for sg in SIGNS for s in SIGNS for k in range(1, n + 1)]
    return even, odd


def _sup(s):
    return "+" if s == "p" else "-"


def build_realizations(n):
    """label -> (standard_form list, frappat_form, parity)."""
    R = {}

    def w(*words_coeffs):
        return [{"words": list(ws), "coeff": frac_str(c)} for ws, c in words_coeffs]

    R["H_1"] = (w((("a_1_p", "a_1_m"), 1), (("b_1_p", "b_1_m"), 1)),
                "a_1^+ a_1^- + b_1^+ b_1^-", 0)
    for k in range(2, n + 1):
        R[f"H_{k}"] = (w(((f"b_{k-1}_p", f"b_{k-1}_m"), 1), ((f"b_{k}_p", f"b_{k}_m"), -1)),
                       f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", 0)
    R[f"H_{n+1}"] = (w(((f"b_{n}_p", f"b_{n}_m"), -1), ((), Fraction(-1, 2))),
                     f"-b_{n}^+ b_{n}^- - 1/2", 0)
    for k in range(1, n + 1):
        for s in SIGNS:
            R[f"E_2del{k}_{s}"] = (w(((f"b_{k}_{s}", f"b_{k}_{s}"), Fraction(1, 2))),
                                   f"1/2 (b_{k}^{_sup(s)})^2", 0)
    for i, j in pairs(n):
        for s in SIGNS:
            for t in SIGNS:
                R[f"E_del{i}_del{j}_{s}{t}"] = (w(((f"b_{i}_{s}", f"b_{j}_{t}"), 1)),
                                               f"b_{i}^{_sup(s)} b_{j}^{_sup(t)}", 0)
    for k in range(1, n + 1):
        for sg in SIGNS:
            for s in SIGNS:
                R[f"E_eps1_del{k}_{sg}{s}"] = (w(((f"a_1_{sg}", f"b_{k}_{s}"), 1)),
                                              f"a_1^{_sup(sg)} b_{k}^{_sup(s)}", 1)
    return R


# --------------------------------------------------------- decomposition ----
class Decomposer:
    """Expresses normally ordered quadratic oscillator polynomials in the
    basis of g plus the central element K (= constant word ())."""

    def __init__(self, n, basis, realizations):
        self.basis = basis
        self.cols = list(basis) + ["K"]
        vecs = {lab: {k[2]: c for k, c in from_standard_form(realizations[lab][0]).items()}
                for lab in basis}
        vecs["K"] = {(): Fraction(1)}
        monos = sorted({m for v in vecs.values() for m in v}, key=lambda m: (len(m), m))
        if len(monos) != len(self.cols):
            raise ValueError("basis + K is not square over its monomials")
        # Exact Gauss-Jordan inverse: monomial -> coefficients on cols
        N = len(monos)
        idx = {m: i for i, m in enumerate(monos)}
        A = [[Fraction(0)] * N for _ in range(N)]
        for j, lab in enumerate(self.cols):
            for m, c in vecs[lab].items():
                A[idx[m]][j] = c
        inv = _inverse(A)
        self.mono_to_cols = {m: {self.cols[j]: inv[j][idx[m]] for j in range(N) if inv[j][idx[m]] != 0}
                             for m in monos}

    def decompose(self, poly):
        """poly: {word: coeff} -> {label or 'K': coeff}."""
        out = {}
        for m, c in poly.items():
            if m not in self.mono_to_cols:
                raise ValueError(f"monomial {m} outside g + CK")
            for lab, d in self.mono_to_cols[m].items():
                out[lab] = out.get(lab, 0) + c * d
        return {k: v for k, v in out.items() if v != 0}


def _inverse(A):
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


# ------------------------------------------------------------- builder ----
class CAlgebra:
    """Basis, parity, realizations, and bracket for C(n+1)."""

    def __init__(self, n, deformed=False):
        self.n = n
        self.even, self.odd = build_basis(n)
        self.basis = self.odd + self.even  # PBW: odd < even
        self.real = build_realizations(n)
        self.parity = {lab: self.real[lab][2] for lab in self.basis}
        self.alg = OscillatorAlgebra(n, deformed=deformed)
        self.elem = {lab: self.alg.normal_order(from_standard_form(self.real[lab][0]))
                     for lab in self.basis}
        self.dec = Decomposer(n, self.basis, self.real)

    def raw_bracket(self, X, Y):
        return self.alg.bracket(self.elem[X], self.parity[X], self.elem[Y], self.parity[Y])

    def split(self, elem):
        """Split an element into (undeformed part, {gb: kappa part}), each decomposed in g + CK."""
        part0, partk = {}, {}
        for (kap, gb, word), c in elem.items():
            if kap == 0:
                part0[word] = part0.get(word, 0) + c
            else:
                partk.setdefault(gb, {})
                partk[gb][word] = partk[gb].get(word, 0) + c
        return self.dec.decompose(part0), {g: d for g, p in partk.items()
                                           if (d := self.dec.decompose(p))}


def structure_constants(C):
    """{(X, Y): {Z: coeff}} for all ordered pairs with non-zero bracket."""
    out = {}
    for X in C.basis:
        for Y in C.basis:
            res, kap = C.split(C.raw_bracket(X, Y))
            if kap:
                raise ValueError("kappa terms in undeformed bracket")
            if "K" in res:
                raise ValueError(f"central K term in [{X},{Y}]: {res['K']}")
            if res:
                out[(X, Y)] = res
    return out


def build_schema1(n):
    C = CAlgebra(n)
    sc = structure_constants(C)
    order = {lab: i for i, lab in enumerate(C.basis)}
    sc_list = [{"X": X, "Y": Y, "Z": Z, "coeff": frac_str(c), "sign_rule": "graded"}
               for (X, Y), res in sc.items() for Z, c in sorted(res.items(), key=lambda t: order[t[0]])]
    bos = [f"b_{k}_{s}" for k in range(1, n + 1) for s in SIGNS]
    real = {}
    for lab in C.basis:
        sf, fr, p = C.real[lab]
        real[lab] = {"standard_form": sf, "frappat_form": fr, "parity": p}
    real[f"H_{n+1}"]["note"] = "Terminal Cartan; super-symmetrized form -(1/2){b_n^+, b_n^-}"
    real["H_1"]["note"] = "so(2)-carrying Cartan; equals (1/2)[a_1^+,a_1^-] + (1/2){b_1^+,b_1^-}"
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n", "total": "2n^2 + 5n + 1"},
            "dimension": {"total": len(C.basis), "even": len(C.even), "odd": len(C.odd)},
        },
        "oscillator_generators": {
            "fermions": {"count": 2, "m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermionic CAR pair a_1^± (replaces supplementary fermion a_0)"},
            "bosons": {"count": 2 * n, "n": n, "labels": bos, "parity": 0,
                       "description": "Bosonic oscillators b_k^± with k=1,...,n"},
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for the pair a_1^±",
                "relations": {"conjugate_pair": "{a_1^-, a_1^+} = 1",
                              "nilpotency": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0"}},
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                              "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0  (undeformed)"},
            "normal_order": ", ".join(C.alg.order),
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                      "role": "odd central element carrying the inhomogeneous deformation (Schema 2+)"},
            "K": {"label": "K", "parity": 0, "relation": "K = 1",
                  "role": "even central element; identified with scalar 1, excluded from basis"},
        },
        "basis": {"even": C.even, "odd": C.odd,
                  "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"},
        "parity": {lab: C.parity[lab] for lab in C.basis},
        "generator_realization": {"description": "Standard form with oscillator normal order",
                                  "ordering": ", ".join(C.alg.order), "realizations": real},
        "structure_constants": sc_list,
        "metadata": {"generated_by": "src/C_generators.py",
                     "generation_date": datetime.date.today().isoformat(),
                     "references": ["Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                                    "Bakalov and Sullivan (2017)"],
                     "notation": "handover/notation.md",
                     "n_nonzero_entries": len(sc_list)},
    }


def write_json(obj, name):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    return path


def main(ns):
    for n in ns:
        s = build_schema1(n)
        p = write_json(s, f"C_{n}_structure.json")
        d = s["algebra"]["dimension"]
        print(f"n={n}: {s['algebra']['cartan_type']} dim {d['even']}|{d['odd']} "
              f"entries={len(s['structure_constants'])} -> {os.path.relpath(p)}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])

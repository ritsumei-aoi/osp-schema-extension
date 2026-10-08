"""
Schema 1 generator for C(n+1) = osp(2|2n).

Builds the basis (PBW order of handover/notation.md §4), the oscillator
realizations, computes all graded brackets [X, Y} in the undeformed
oscillator algebra and writes data/C_{n}_structure.json.

Usage:  python3 src/C_generators.py [n ...]      (default: 1 2 3)
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from itertools import combinations

import sympy
from sympy import Rational, Integer, Matrix, expand

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osc_algebra import OscAlgebra, ONE, ZERO  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SCHEMA_VERSION = "5.0"

# --------------------------------------------------------------------- basis

def cartan_labels(n):
    return [f"H_{k}" for k in range(1, n + 2)]


def even_basis(n):
    H = cartan_labels(n)
    E2p = [f"E_2del{k}_p" for k in range(1, n + 1)]
    Epp = [f"E_del{i}_del{j}_pp" for i, j in combinations(range(1, n + 1), 2)]
    E2m = [f"E_2del{k}_m" for k in range(1, n + 1)]
    Emm = [f"E_del{i}_del{j}_mm" for i, j in combinations(range(1, n + 1), 2)]
    Epm = [f"E_del{i}_del{j}_pm" for i, j in combinations(range(1, n + 1), 2)]
    Emp = [f"E_del{i}_del{j}_mp" for i, j in combinations(range(1, n + 1), 2)]
    return H + E2p + Epp + E2m + Emm + Epm + Emp


def odd_basis(n):
    return [f"E_eps1_del{k}_{ss}" for ss in ("pp", "pm", "mp", "mm")
            for k in range(1, n + 1)]


def pbw_order(n):
    """PBW order: kappa < odd < even (kappa itself is not a basis element)."""
    return odd_basis(n) + even_basis(n)


def basis(n):
    return even_basis(n) + odd_basis(n)


def parity_map(n):
    p = {x: 0 for x in even_basis(n)}
    p.update({x: 1 for x in odd_basis(n)})
    return p


def dimensions(n):
    return {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1, "odd": 4 * n}


# ------------------------------------------------------------- realizations

def realizations(n):
    """label -> element dict {word: coeff} in oscillator normal order."""
    R = {}
    a_p, a_m = "a_1_p", "a_1_m"
    b = lambda k, s: f"b_{k}_{s}"
    # Cartan (Frappat distinguished form, Cn1_definition.md §2)
    R["H_1"] = {(a_p, a_m): ONE, (b(1, "p"), b(1, "m")): ONE}
    for k in range(2, n + 1):
        R[f"H_{k}"] = {(b(k - 1, "p"), b(k - 1, "m")): ONE,
                       (b(k, "p"), b(k, "m")): -ONE}
    R[f"H_{n + 1}"] = {(b(n, "p"), b(n, "m")): -ONE, (): Rational(-1, 2)}
    # even root vectors
    for k in range(1, n + 1):
        R[f"E_2del{k}_p"] = {(b(k, "p"), b(k, "p")): ONE}
        R[f"E_2del{k}_m"] = {(b(k, "m"), b(k, "m")): ONE}
    for i, j in combinations(range(1, n + 1), 2):
        R[f"E_del{i}_del{j}_pp"] = {(b(i, "p"), b(j, "p")): ONE}
        R[f"E_del{i}_del{j}_pm"] = {(b(i, "p"), b(j, "m")): ONE}
        R[f"E_del{i}_del{j}_mp"] = {(b(i, "m"), b(j, "p")): ONE}
        R[f"E_del{i}_del{j}_mm"] = {(b(i, "m"), b(j, "m")): ONE}
    # odd root vectors: first sign = eps, second = delta_k
    for k in range(1, n + 1):
        for sig, a in (("p", a_p), ("m", a_m)):
            for s in "pm":
                R[f"E_eps1_del{k}_{sig}{s}"] = {(a, b(k, s)): ONE}
    return R


def frappat_form(label, elem):
    def letter(l):
        if l == "a_1_p":
            return "a_1^+"
        if l == "a_1_m":
            return "a_1^-"
        _, k, s = l.split("_")
        return f"b_{k}^{'+' if s == 'p' else '-'}"
    terms = []
    for w, c in elem.items():
        word = " ".join(letter(l) for l in w)
        c = sympy.nsimplify(c)
        if word == "":
            terms.append(str(c))
        elif c == 1:
            terms.append(word)
        elif c == -1:
            terms.append("-" + word)
        else:
            terms.append(f"{c} {word}")
    s = " + ".join(terms)
    return s.replace("+ -", "- ")


# ------------------------------------------------------------ decomposition

class Decomposer:
    """Exact decomposition of elements of U(A) into span(basis) + C K."""

    def __init__(self, n, alg: OscAlgebra | None = None):
        self.n = n
        self.alg = alg or OscAlgebra(n)
        self.labels = basis(n) + ["K"]
        R = realizations(n)
        R["K"] = {(): ONE}
        self.R = R
        words = []
        for lab in self.labels:
            for w in R[lab]:
                if w not in words:
                    words.append(w)
        self.words = words
        self.widx = {w: i for i, w in enumerate(words)}
        M = Matrix(len(words), len(self.labels), lambda i, j:
                   R[self.labels[j]].get(words[i], ZERO))
        if M.shape[0] != M.shape[1]:
            raise ValueError("monomial count != basis count + 1")
        self.M = M
        self.Minv = M.inv()

    def decompose(self, elem: dict) -> dict:
        """elem (no kappa words) -> {label: coeff}, label in basis or 'K'."""
        v = [ZERO] * len(self.words)
        for w, c in elem.items():
            if w not in self.widx:
                raise ValueError(f"word {w} not in span(basis)+K")
            v[self.widx[w]] = c
        coeffs = self.Minv * Matrix(v)
        return {self.labels[i]: expand(coeffs[i]) for i in range(len(self.labels))
                if expand(coeffs[i]) != 0}


def coeff_str(c) -> str:
    return str(sympy.nsimplify(c))


# ------------------------------------------------------ structure constants

def structure_constants(n, dec: Decomposer | None = None):
    dec = dec or Decomposer(n)
    alg = dec.alg
    R = dec.R
    B = basis(n)
    entries = []
    for X in B:
        for Y in B:
            br = alg.bracket(R[X], R[Y])
            if not br:
                continue
            d = dec.decompose(br)
            if "K" in d:
                raise ValueError(f"[{X},{Y}] has a K component: {d['K']}")
            for Z, c in d.items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": coeff_str(c),
                                "sign_rule": "graded"})
    return entries


def build_schema1(n, date=None):
    date = date or datetime.date.today().isoformat()
    dec = Decomposer(n)
    R = realizations(n)
    par = parity_map(n)
    dim = dimensions(n)
    gen_real = {}
    for lab in basis(n):
        gen_real[lab] = {
            "standard_form": [{"words": list(w), "coeff": coeff_str(c)}
                              for w, c in R[lab].items()],
            "frappat_form": frappat_form(lab, R[lab]),
            "parity": par[lab],
        }
    gen_real[f"H_{n+1}"]["note"] = "Terminal Cartan; the constant -1/2 is required for closure"
    gen_real["H_1"]["note"] = "Cartan of the odd simple root eps - delta_1; contains the so(2) number operator a_1^+ a_1^-"
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension_formulas": {"even": "2n^2 + n + 1", "odd": "4n",
                                   "total": "2n^2 + 5n + 1"},
            "dimension": dim,
            "even_subalgebra": "so(2) + sp(2n)",
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1, "count": 2, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                "description": "Standard fermionic pair a_1^± with CAR {a_1^-, a_1^+} = 1",
            },
            "bosons": {
                "n": n, "count": 2 * n, "labels": boson_labels, "parity": 0,
                "description": "Bosonic oscillators b_k^± with k=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the fermionic pair",
                "relations": {
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0  (i.e. (a_1^±)^2 = 0)",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^±, a_1^±] = 0  (undeformed; Schema 2 deforms this to -gb·kappa)",
            },
            "normal_order": "kappa < " + " < ".join(["a_1_p", "a_1_m"] + boson_labels),
        },
        "central_elements": {
            "kappa": {
                "label": "kappa", "parity": 1, "relation": "kappa^2 = 0",
                "central": "[kappa, X} = 0 for all X (anticommutes with odd oscillators as an associative element)",
                "role": "formal odd parameter of the inhomogeneous deformation (Schema 2); absent from Schema 1 brackets",
                "in_basis": False,
            },
            "K": {
                "label": "K", "parity": 0,
                "relation": "K = 1 (identified with the scalar identity)",
                "role": "even central element of the oscillator extension A = V + CK + C kappa; appears as a target of gamma in Schema 2",
                "in_basis": False,
            },
        },
        "basis": {
            "even": even_basis(n),
            "odd": odd_basis(n),
            "cartan": cartan_labels(n),
            "pbw_order": pbw_order(n),
            "ordering_convention": "PBW: kappa < [odd] < [even]  (K = 1 is excluded)",
        },
        "parity": par,
        "generator_realization": {
            "description": "Standard form with oscillator normal ordering",
            "ordering": ", ".join(["kappa", "a_1_p", "a_1_m"] + boson_labels),
            "realizations": gen_real,
        },
        "structure_constants": structure_constants(n, dec),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": date,
            "notation": "handover/notation.md",
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def structure_path(n):
    return os.path.join(DATA_DIR, f"C_{n}_structure.json")


def write_schema1(n):
    os.makedirs(DATA_DIR, exist_ok=True)
    data = build_schema1(n)
    with open(structure_path(n), "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    return data


def load_structure(n):
    with open(structure_path(n)) as f:
        return json.load(f)


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        d = write_schema1(n)
        print(f"C({n+1}) n={n}: dim {d['algebra']['dimension']}, "
              f"{len(d['structure_constants'])} nonzero bracket terms -> {structure_path(n)}")

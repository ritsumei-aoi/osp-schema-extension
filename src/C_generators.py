"""Structure-constant generator for C(n+1) = osp(2|2n) (Schema 1, v5.0).

Elements of the oscillator algebra are linear combinations of normal-ordered
monomials in
  fermions:  a_1_m, a_1_p    with  {a_1_m, a_1_p} = 1,  a_1_p^2 = a_1_m^2 = 0
  bosons:    b_k_m, b_k_p    with  [b_k_m, b_l_p] = delta_kl  (k = 1..n)
All other pairs commute. Normal order: a_1_m < a_1_p < b_1_m < b_1_p < b_2_m < ...

Basis labels and PBW ordering follow handover/notation.md (Issue I01).
"""

import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import sympy

ODD_PATTERNS = ("pp", "pm", "mp", "mm")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def is_fermion(name):
    return name.startswith("a_")


def parity_of(name):
    return 1 if is_fermion(name) else 0


def order_key(name):
    """Position of a generator in the normal ordering."""
    if name == "a_1_m":
        return 0
    if name == "a_1_p":
        return 1
    _, k, s = name.split("_")
    return 2 + 2 * (int(k) - 1) + (0 if s == "m" else 1)


def _swap_rule(x, y):
    """Return (s, c) with x*y = s*y*x + c for x out of order (x left of y)."""
    if is_fermion(x) and is_fermion(y):
        return -1, Fraction(1)  # a_p a_m = -a_m a_p + 1
    if not is_fermion(x) and not is_fermion(y) and x.split("_")[1] == y.split("_")[1]:
        # x = b_k_p, y = b_k_m: b_p b_m = b_m b_p - 1
        return 1, Fraction(-1)
    return 1, Fraction(0)


@lru_cache(maxsize=None)
def _normal_order_cached(word):
    for i in range(len(word) - 1):
        x, y = word[i], word[i + 1]
        if x == y and is_fermion(x):
            return ()
        if order_key(x) > order_key(y):
            s, c = _swap_rule(x, y)
            out = {}
            for mono, coeff in _normal_order_cached(word[:i] + (y, x) + word[i + 2:]):
                out[mono] = out.get(mono, 0) + s * coeff
            if c != 0:
                for mono, coeff in _normal_order_cached(word[:i] + word[i + 2:]):
                    out[mono] = out.get(mono, 0) + c * coeff
            return tuple((m, v) for m, v in out.items() if v != 0)
    return ((word, Fraction(1)),)


def normal_order(word):
    """Normal-order a word; returns dict monomial -> Fraction."""
    return dict(_normal_order_cached(tuple(word)))


def multiply(X, Y):
    out = {}
    for mx, cx in X.items():
        for my, cy in Y.items():
            for mono, c in normal_order(mx + my).items():
                out[mono] = out.get(mono, 0) + cx * cy * c
    return {m: c for m, c in out.items() if c != 0}


def bracket(X, pX, Y, pY):
    """Super-commutator [X, Y] = XY - (-1)^{pX pY} YX."""
    sign = -1 if (pX and pY) else 1
    out = dict(multiply(X, Y))
    for m, c in multiply(Y, X).items():
        out[m] = out.get(m, 0) - sign * c
    return {m: c for m, c in out.items() if c != 0}


def element_from_terms(terms):
    """terms: list of (coeff, word) -> dict monomial -> Fraction."""
    out = {}
    for coeff, word in terms:
        for mono, c in normal_order(word).items():
            out[mono] = out.get(mono, 0) + Fraction(coeff) * c
    return {m: c for m, c in out.items() if c != 0}


def build_basis(n):
    """Return the ordered basis (PBW: odd, then even; K excluded) for C(n+1).

    Each entry: dict with keys label, parity, terms (realization: (coeff, word)).
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    odd = []
    for k in range(1, n + 1):
        for pat in ODD_PATTERNS:
            fa = "a_1_p" if pat[0] == "p" else "a_1_m"
            bo = f"b_{k}_{pat[1]}"
            odd.append({
                "label": f"E_eps1_del{k}_{pat}",
                "parity": 1,
                "terms": [(1, (fa, bo))],
            })

    even = []
    # Cartan: H_1 = a_1_p a_1_m + b_1_p b_1_m ; H_k = b_{k-1}^+b_{k-1}^- - b_k^+b_k^- ;
    # H_{n+1} = -b_n^+ b_n^- - 1/2
    even.append({"label": "H_1", "parity": 0,
                 "terms": [(1, ("a_1_p", "a_1_m")), (1, ("b_1_p", "b_1_m"))]})
    for k in range(2, n + 1):
        even.append({"label": f"H_{k}", "parity": 0,
                     "terms": [(1, (f"b_{k-1}_p", f"b_{k-1}_m")),
                               (-1, (f"b_{k}_p", f"b_{k}_m"))]})
    even.append({"label": f"H_{n+1}", "parity": 0,
                 "terms": [(-1, (f"b_{n}_p", f"b_{n}_m")), (Fraction(-1, 2), ())]})
    # 2 delta_k roots
    for k in range(1, n + 1):
        even.append({"label": f"E_2del{k}_p", "parity": 0,
                     "terms": [(1, (f"b_{k}_p", f"b_{k}_p"))]})
        even.append({"label": f"E_2del{k}_m", "parity": 0,
                     "terms": [(1, (f"b_{k}_m", f"b_{k}_m"))]})
    # delta_i +- delta_j roots, i < j
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for pat in ODD_PATTERNS:
                fi = f"b_{i}_{pat[0]}"
                fj = f"b_{j}_{pat[1]}"
                even.append({"label": f"E_del{i}_del{j}_{pat}", "parity": 0,
                             "terms": [(1, (fi, fj))]})
    return odd + even


def _solve_in_basis(target, basis_elems):
    """Solve target = sum_i c_i B_i over Q. Raises if target is outside the span."""
    monos = sorted({m for B in basis_elems for m in B} | set(target), key=str)
    A = sympy.Matrix([[sympy.Rational(B.get(m, 0).numerator, B.get(m, 0).denominator)
                       for B in basis_elems] for m in monos])
    b = sympy.Matrix([sympy.Rational(target.get(m, 0).numerator, target.get(m, 0).denominator)
                      for m in monos])
    sol = sympy.linsolve((A, b))
    if not sol:
        raise ValueError("bracket is not in the span of the basis")
    (vals,) = tuple(sol)
    if any(v.free_symbols for v in vals):
        raise ValueError("basis is linearly dependent")
    return {i: Fraction(int(sympy.fraction(v)[0]), int(sympy.fraction(v)[1]))
            for i, v in enumerate(vals) if v != 0}


def structure_constants(n):
    """Return (basis labels, parities, list of brackets) for C(n+1)."""
    basis = build_basis(n)
    elems = [element_from_terms(b["terms"]) for b in basis]
    labels = [b["label"] for b in basis]
    parities = [b["parity"] for b in basis]
    brackets = []
    for i in range(len(basis)):
        for j in range(i, len(basis)):
            br = bracket(elems[i], parities[i], elems[j], parities[j])
            if not br:
                continue
            coeffs = _solve_in_basis(br, elems)
            for z, c in sorted(coeffs.items()):
                brackets.append({
                    "X": labels[i], "Y": labels[j], "Z": labels[z],
                    "coeff": str(c), "sign_rule": "graded",
                })
    return labels, parities, brackets


def build_schema(n):
    """Assemble the full Schema 1 (v5.0) dictionary for C(n+1)."""
    basis = build_basis(n)
    labels, parities, brackets = structure_constants(n)
    even = [b["label"] for b in basis if b["parity"] == 0]
    odd = [b["label"] for b in basis if b["parity"] == 1]
    dim_even, dim_odd = 2 * n * n + n + 1, 4 * n
    realization = {}
    for b in basis:
        realization[b["label"]] = {
            "standard_form": [
                {"words": list(word), "coeff": str(Fraction(coeff))}
                for coeff, word in b["terms"]
            ],
            "parity": b["parity"],
        }
    bosons = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
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
            "dimension": {"total": dim_even + dim_odd, "even": dim_even, "odd": dim_odd},
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "parity": 1,
                         "description": "Standard fermion pair a_1^+, a_1^-"},
            "bosons": {"n": n, "count": 2 * n, "labels": bosons, "parity": 0,
                       "description": "Bosonic oscillators b_k^+, b_k^- with k=1,...,n"},
        },
        "oscillator_relations": {
            "fermionic_anticommutator": {
                "relation": "{a_1_m, a_1_p} = 1",
                "others": "a_1_p^2 = a_1_m^2 = 0",
            },
            "bosonic_commutators": {
                "same_type": "[b_i^s, b_j^s] = 0",
                "conjugate_pair": "[b_i^m, b_j^p] = delta_{ij}",
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^s, a_1^sigma] = 0 (undeformed; deformation lives in gb, see Schema 2)",
            },
        },
        "central_elements": {
            "kappa": {"parity": 1, "relation": "kappa^2 = 0",
                      "role": "odd nilpotent central extension"},
            "K": {"parity": 0, "value": 1,
                  "role": "even central element; identified with the scalar 1, excluded from basis"},
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: kappa < [odd] < [even]; K excluded",
        },
        "parity": {label: p for label, p in zip(labels, parities)},
        "generator_realization": {
            "description": "Defining oscillator words as written in docs/math/Cn1_definition.md, "
                           "with coefficients; words are not normal-ordered",
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m, ...",
            "realizations": realization,
        },
        "structure_constants": brackets,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": "2026-10-08",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def write_schema(n, out_dir=DATA_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"C_{n}_structure.json"
    with path.open("w") as f:
        json.dump(build_schema(n), f, indent=2)
        f.write("\n")
    return path


if __name__ == "__main__":
    for rank in (1, 2, 3):
        print(write_schema(rank))

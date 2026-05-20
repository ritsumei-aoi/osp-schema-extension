"""
C_generators.py  —  Structure-constant generator for C(n+1) = osp(2|2n).

Oscillator algebra
------------------
Standard fermionic pair  a_1^+, a_1^-  (parity 1, CAR):
    {a_1^-, a_1^+} = 1,  (a_1^+)^2 = (a_1^-)^2 = 0
Bosonic oscillators  b_k^+, b_k^-  k=1..n  (parity 0, CCR):
    [b_k^-, b_l^+] = delta_{kl}
Mixed:  [b_i^+/-, a_1^+/-] = 0

PBW index assignment:
    a_1_p -> 0,  a_1_m -> 1,  b_k_p -> 2k,  b_k_m -> 2k+1  (k = 1..n)

PBW ordering (Option A, Fermionic-first, approved in Issue I01-1):
    kappa  <  odd generators  <  even generators

Convention for E_{±2δ_k}: (b_k^±)^2 — the 1/2 Frappat factor is absorbed.
"""

import json
from fractions import Fraction
from datetime import date
from typing import Dict, List, Tuple

OscWord = Tuple[int, ...]
OscPoly = Dict[OscWord, Fraction]


# ---------------------------------------------------------------------------
# Oscillator algebra: PBW reduction
# ---------------------------------------------------------------------------

def _osc_is_fermionic(idx: int) -> bool:
    return idx <= 1


def _swap_pair(i: int, j: int) -> List[Tuple[Fraction, OscWord]]:
    """
    Return terms for op_i · op_j  when i > j (out of PBW order).
    Each term is (coeff, replacement_word_fragment).
    """
    # (a_1_m, a_1_p): anticommutation  a_1^- a_1^+ = 1 - a_1^+ a_1^-
    if i == 1 and j == 0:
        return [(Fraction(1), ()), (Fraction(-1), (0, 1))]
    # (b_k_m, b_k_p): same bosonic pair  b_k^- b_k^+ = 1 + b_k^+ b_k^-
    if i >= 3 and j >= 2 and i == j + 1 and i % 2 == 1 and j % 2 == 0:
        return [(Fraction(1), ()), (Fraction(1), (j, i))]
    # All other pairs commute freely
    return [(Fraction(1), (j, i))]


def pbw_reduce_word(word: OscWord) -> OscPoly:
    """Reduce an arbitrary oscillator word to PBW normal form."""
    terms: List[Tuple[Fraction, List[int]]] = [(Fraction(1), list(word))]
    result: OscPoly = {}

    while terms:
        coeff, w = terms.pop()
        if coeff == 0:
            continue

        # Fermionic squares vanish: (a_1^+)^2 = (a_1^-)^2 = 0
        fermionic_sq = any(
            w[k] == w[k + 1] and w[k] <= 1 for k in range(len(w) - 1)
        )
        if fermionic_sq:
            continue

        # Find first out-of-order adjacent pair
        swapped = False
        for k in range(len(w) - 1):
            if w[k] > w[k + 1]:
                for sc, repl in _swap_pair(w[k], w[k + 1]):
                    new_w = w[:k] + list(repl) + w[k + 2:]
                    terms.append((coeff * sc, new_w))
                swapped = True
                break

        if not swapped:
            key = tuple(w)
            result[key] = result.get(key, Fraction(0)) + coeff

    return {k: v for k, v in result.items() if v != 0}


def poly_add(A: OscPoly, B: OscPoly, coeff_B: Fraction = Fraction(1)) -> OscPoly:
    result = dict(A)
    for w, c in B.items():
        result[w] = result.get(w, Fraction(0)) + coeff_B * c
    return {k: v for k, v in result.items() if v != 0}


def poly_multiply(X: OscPoly, Y: OscPoly) -> OscPoly:
    result: OscPoly = {}
    for wx, cx in X.items():
        for wy, cy in Y.items():
            for w, c in pbw_reduce_word(wx + wy).items():
                result[w] = result.get(w, Fraction(0)) + cx * cy * c
    return {k: v for k, v in result.items() if v != 0}


def word_parity(word: OscWord) -> int:
    """Parity of a PBW word = number of fermionic indices mod 2."""
    return sum(1 for i in word if _osc_is_fermionic(i)) % 2


def graded_bracket(X: OscPoly, pX: int, Y: OscPoly, pY: int) -> OscPoly:
    """Graded bracket [X, Y} = XY - (-1)^{p(X)p(Y)} YX."""
    XY = poly_multiply(X, Y)
    YX = poly_multiply(Y, X)
    sign = Fraction((-1) ** (pX * pY))
    result: OscPoly = {}
    for w, c in XY.items():
        result[w] = result.get(w, Fraction(0)) + c
    for w, c in YX.items():
        result[w] = result.get(w, Fraction(0)) - sign * c
    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Generator definitions for C(n+1)
# ---------------------------------------------------------------------------

def build_generators(n: int) -> Tuple[
    Dict[str, OscPoly],
    Dict[str, int],
    List[str],
    List[str],
]:
    """
    Return (realizations, parities, even_basis, odd_basis) for C(n+1).

    Index map:  a_1_p=0, a_1_m=1, b_k_p=2k, b_k_m=2k+1  (k=1..n)
    """
    gens: Dict[str, OscPoly] = {}
    parities: Dict[str, int] = {}

    # --- Cartan generators ---
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    gens["H_1"] = {(0, 1): Fraction(1), (2, 3): Fraction(1)}
    parities["H_1"] = 0

    # H_k = b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-  (k = 2..n)
    for k in range(2, n + 1):
        label = f"H_{k}"
        gens[label] = {
            (2 * (k - 1), 2 * (k - 1) + 1): Fraction(1),
            (2 * k, 2 * k + 1): Fraction(-1),
        }
        parities[label] = 0

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    label = f"H_{n + 1}"
    gens[label] = {(2 * n, 2 * n + 1): Fraction(-1), (): Fraction(-1, 2)}
    parities[label] = 0

    # --- Positive even roots ---
    # E_2del{k}_p = (b_k^+)^2  (convention: 1/2 Frappat factor absorbed)
    for k in range(1, n + 1):
        label = f"E_2del{k}_p"
        gens[label] = {(2 * k, 2 * k): Fraction(1)}
        parities[label] = 0

    # E_del{i}_del{j}_pp = b_i^+ b_j^+  (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            label = f"E_del{i}_del{j}_pp"
            gens[label] = {(2 * i, 2 * j): Fraction(1)}
            parities[label] = 0

    # --- Negative even roots ---
    # E_2del{k}_m = (b_k^-)^2
    for k in range(1, n + 1):
        label = f"E_2del{k}_m"
        gens[label] = {(2 * k + 1, 2 * k + 1): Fraction(1)}
        parities[label] = 0

    # E_del{i}_del{j}_mm = b_i^- b_j^-  (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            label = f"E_del{i}_del{j}_mm"
            gens[label] = {(2 * i + 1, 2 * j + 1): Fraction(1)}
            parities[label] = 0

    # --- Mixed even roots ---
    # E_del{i}_del{j}_pm = b_i^+ b_j^-  (i < j)
    # E_del{i}_del{j}_mp = b_i^- b_j^+  (i < j)
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            label_pm = f"E_del{i}_del{j}_pm"
            gens[label_pm] = {(2 * i, 2 * j + 1): Fraction(1)}
            parities[label_pm] = 0

            label_mp = f"E_del{i}_del{j}_mp"
            gens[label_mp] = {(2 * i + 1, 2 * j): Fraction(1)}
            parities[label_mp] = 0

    # --- Odd generators ---
    for k in range(1, n + 1):
        for suffix, (fi, bi) in [
            ("pp", (0, 2 * k)),
            ("pm", (0, 2 * k + 1)),
            ("mp", (1, 2 * k)),
            ("mm", (1, 2 * k + 1)),
        ]:
            label = f"E_eps1_del{k}_{suffix}"
            gens[label] = {(fi, bi): Fraction(1)}
            parities[label] = 1

    # --- Basis lists in PBW order (Option A) ---
    # Odd block: E_eps1_del{k}_pp (k=1..n), then pm, mp, mm
    odd_basis: List[str] = []
    for suffix in ("pp", "pm", "mp", "mm"):
        for k in range(1, n + 1):
            odd_basis.append(f"E_eps1_del{k}_{suffix}")

    # Even block: H_1..H_{n+1}, pos roots, neg roots, mixed roots
    even_basis: List[str] = []
    for k in range(1, n + 2):
        even_basis.append(f"H_{k}")
    for k in range(1, n + 1):
        even_basis.append(f"E_2del{k}_p")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_pp")
    for k in range(1, n + 1):
        even_basis.append(f"E_2del{k}_m")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_mm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even_basis.append(f"E_del{i}_del{j}_pm")
            even_basis.append(f"E_del{i}_del{j}_mp")

    return gens, parities, even_basis, odd_basis


# ---------------------------------------------------------------------------
# Express bracket result in terms of generators
# ---------------------------------------------------------------------------

def express_in_generators(
    poly: OscPoly,
    gens: Dict[str, OscPoly],
    basis: List[str],
) -> Dict[str, Fraction]:
    """
    Express poly as a linear combination of generators in basis.
    Uses exact Gaussian elimination with Fraction arithmetic.
    Returns {label: coeff} for non-zero coefficients only.
    """
    # Collect all monomials that appear in poly or in any generator
    all_monomials: List[OscWord] = sorted(
        {w for p in [poly] + [gens[g] for g in basis] for w in p},
        key=lambda t: (len(t), t),
    )

    m = len(all_monomials)
    k = len(basis)
    monom_idx = {w: i for i, w in enumerate(all_monomials)}

    # Augmented matrix [A | b] (m rows × (k+1) cols)
    mat = [[Fraction(0)] * (k + 1) for _ in range(m)]
    for i, w in enumerate(all_monomials):
        mat[i][k] = poly.get(w, Fraction(0))
    for j, g in enumerate(basis):
        for w, c in gens[g].items():
            mat[monom_idx[w]][j] = c

    # Gaussian elimination (partial pivoting on first non-zero)
    pivot_col: Dict[int, int] = {}  # col -> pivot row
    pivot_row = 0
    for col in range(k):
        found = next((r for r in range(pivot_row, m) if mat[r][col] != 0), -1)
        if found == -1:
            continue
        mat[pivot_row], mat[found] = mat[found], mat[pivot_row]
        piv = mat[pivot_row][col]
        mat[pivot_row] = [x / piv for x in mat[pivot_row]]
        for row in range(m):
            if row != pivot_row and mat[row][col] != 0:
                f = mat[row][col]
                mat[row] = [mat[row][c] - f * mat[pivot_row][c] for c in range(k + 1)]
        pivot_col[col] = pivot_row
        pivot_row += 1

    return {
        basis[col]: mat[row][k]
        for col, row in pivot_col.items()
        if mat[row][k] != 0
    }


# ---------------------------------------------------------------------------
# Structure constant computation
# ---------------------------------------------------------------------------

def _fraction_to_str(f: Fraction) -> str:
    return str(f) if f.denominator != 1 else str(f.numerator)


def compute_structure_constants(n: int) -> List[dict]:
    """
    Compute all non-zero graded brackets [X, Y} for C(n+1).
    Iterates over all pairs (X, Y) with X ≤ Y in the PBW ordering.
    Returns a list of dicts ready for JSON serialisation.
    """
    gens, parities, even_basis, odd_basis = build_generators(n)
    all_basis = odd_basis + even_basis  # PBW order (kappa excluded)

    records: List[dict] = []
    for a, lx in enumerate(all_basis):
        for b in range(a, len(all_basis)):
            ly = all_basis[b]
            bracket = graded_bracket(
                gens[lx], parities[lx], gens[ly], parities[ly]
            )
            if not bracket:
                continue
            coeffs = express_in_generators(bracket, gens, all_basis)
            for lz, coeff in coeffs.items():
                records.append(
                    {
                        "X": lx,
                        "Y": ly,
                        "Z": lz,
                        "coeff": _fraction_to_str(coeff),
                        "sign_rule": "graded",
                    }
                )
    return records


# ---------------------------------------------------------------------------
# Schema 1 JSON builder
# ---------------------------------------------------------------------------

def _build_realization_dict(
    n: int,
    gens: Dict[str, OscPoly],
    parities: Dict[str, int],
    even_basis: List[str],
    odd_basis: List[str],
) -> dict:
    """Build the generator_realization sub-object."""
    osc_order = ["a_1_p", "a_1_m"] + [
        f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")
    ]
    idx_label = {0: "a_1_p", 1: "a_1_m"}
    for k in range(1, n + 1):
        idx_label[2 * k] = f"b_{k}_p"
        idx_label[2 * k + 1] = f"b_{k}_m"

    def frappat_form(label: str) -> str:
        osc = gens[label]
        terms = []
        for word, coeff in sorted(osc.items(), key=lambda t: (len(t[0]), t[0])):
            coeff_str = "" if coeff == 1 else ("-" if coeff == -1 else f"{coeff}*")
            if not word:
                terms.append(str(coeff))
            elif len(word) == 1:
                terms.append(f"{coeff_str}{idx_label[word[0]]}")
            else:
                terms.append(coeff_str + " ".join(idx_label[i] for i in word))
        return "  +  ".join(terms) if terms else "0"

    realizations = {}
    for label in even_basis + odd_basis:
        osc = gens[label]
        standard_form = [
            {
                "words": [idx_label[i] for i in word],
                "coeff": _fraction_to_str(coeff),
            }
            for word, coeff in sorted(osc.items(), key=lambda t: (len(t[0]), t[0]))
        ]
        entry: dict = {
            "standard_form": standard_form,
            "frappat_form": frappat_form(label),
            "parity": parities[label],
        }
        if label == f"H_{n + 1}":
            entry["note"] = (
                "Terminal Cartan (k = n+1); constant -1/2 is intrinsic to the Frappat formula"
            )
        if label.startswith("E_2del") and label.endswith("_p"):
            entry["note"] = "Convention: 1/2 factor from Frappat absorbed into normalization"
        if label.startswith("E_2del") and label.endswith("_m"):
            entry["note"] = "Convention: 1/2 factor from Frappat absorbed into normalization"
        realizations[label] = entry

    return {
        "description": "Standard form with PBW ordering of oscillators",
        "ordering": ", ".join(osc_order),
        "realizations": realizations,
    }


def build_schema1(n: int) -> dict:
    """Build the complete Schema 1 dict for C(n+1)."""
    gens, parities, even_basis, odd_basis = build_generators(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim

    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim,
            },
        },
        "oscillator_generators": {
            "standard_fermion": {
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic pair a_1^± satisfying CAR: {a_1^-, a_1^+} = 1",
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k = 1,...,{n}",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for the standard fermionic pair",
                "relations": {
                    "cross": "{a_1^-, a_1^+} = 1",
                    "same_plus": "{a_1^+, a_1^+} = 0",
                    "same_minus": "{a_1^-, a_1^-} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0  for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}",
                },
            },
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"},
        },
        "central_elements": {
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "relation": "kappa^2 = 0",
                "description": (
                    "Odd central element of the Bakalov-Sullivan extension. "
                    "Appears first in the PBW ordering."
                ),
            },
            "K": {
                "label": "K",
                "parity": 0,
                "relation": "K = 1",
                "description": (
                    "Even central identity element. Identified with the scalar 1 in all "
                    "current applications; excluded from PBW basis and structure constant computations."
                ),
            },
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": (
                "PBW: κ < [odd: E_eps1_del{k}_{pp/pm/mp/mm} k=1..n] < "
                "[even: H_1..H_{n+1}, E_2del{k}_p/m, E_del{i}_del{j}_pp/mm/pm/mp]  (K=1 excluded)"
            ),
        },
        "parity": {**{g: 0 for g in even_basis}, **{g: 1 for g in odd_basis}},
        "generator_realization": _build_realization_dict(
            n, gens, parities, even_basis, odd_basis
        ),
        "structure_constants": compute_structure_constants(n),
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017), arXiv:1612.09400",
                "Aoi (2026), On the triviality of inhomogeneous deformations of osp(1|2n)",
            ],
        },
    }
    return schema


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import os

    os.makedirs("data", exist_ok=True)
    for n in (1, 2, 3):
        schema = build_schema1(n)
        path = f"data/C_{n}_structure.json"
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        sc_count = len(schema["structure_constants"])
        print(f"C({n + 1})  n={n}  dim=({schema['algebra']['dimension']['even']}|"
              f"{schema['algebra']['dimension']['odd']})  "
              f"structure_constants={sc_count}  -> {path}")


if __name__ == "__main__":
    main()

"""
C_gamma.py — Schema 2 (gamma structure) generator for C(n+1) = osp(2|2n).

Computes the gamma coefficients γ_{XYZ}(gb) for the inhomogeneous deformation:

    [b_j^s, a_1^sigma]_deformed = [b_j^s, a_1^sigma]_0  -  gb_{sigma,j,s} · kappa

Approved sign convention: Option A  (Issue I05-1, approved 2026-05-20).

PBW-level formula:
    b_j^s · a_1^sigma  =  a_1^sigma · b_j^s  -  gb_{sigma,j,s} · kappa

kappa is odd and central with kappa^2 = 0, so kappa-contributions never cascade.
"""

import json
import sys
import os
from fractions import Fraction
from datetime import date
from typing import Dict, List, Tuple

# Allow running from project root or from src/
sys.path.insert(0, os.path.dirname(__file__))

from C_generators import (
    OscWord,
    OscPoly,
    _swap_pair,
    pbw_reduce_word,
    build_generators,
    express_in_generators,
    _fraction_to_str,
)


# ---------------------------------------------------------------------------
# gb label helper
# ---------------------------------------------------------------------------

def _gb_label(a_idx: int, b_idx: int) -> str:
    """
    Return the gb parameter label for the deformation [b_j^s, a_1^sigma].

    a_idx: 0 = a_1^+, 1 = a_1^-
    b_idx: 2j = b_j^+, 2j+1 = b_j^-   (j >= 1)
    """
    sigma = "p" if a_idx == 0 else "m"
    j = b_idx // 2
    s = "p" if b_idx % 2 == 0 else "m"
    return f"gb_a1{sigma}_b{j}{s}"


# ---------------------------------------------------------------------------
# Deformed PBW reduction
# ---------------------------------------------------------------------------

def pbw_reduce_word_deformed(
    word: OscWord,
) -> Tuple[OscPoly, List[Tuple[Fraction, OscWord, str]]]:
    """
    PBW-reduce an oscillator word in the deformed algebra.

    For each b-a swap encountered during bubble-sort, emit a kappa-contribution
    tagged with the corresponding gb label:
        b_j^s a_1^sigma  -->  a_1^sigma b_j^s  -  gb_{sigma,j,s} kappa

    Returns
    -------
    normal : OscPoly
        The kappa-free part (identical to the undeformed pbw_reduce_word).
    kappa_raw : list of (coeff, rest_word, gb_label)
        Raw kappa contributions.  Each item means: add  coeff * kappa * rest_word
        to the bracket.  rest_word must still be PBW-reduced via the *undeformed*
        reduction (safe because kappa^2 = 0 means no further deformed swaps arise).
    """
    stack: List[Tuple[Fraction, List[int]]] = [(Fraction(1), list(word))]
    normal: OscPoly = {}
    kappa_raw: List[Tuple[Fraction, OscWord, str]] = []

    while stack:
        coeff, w = stack.pop()
        if coeff == 0:
            continue

        # Fermionic squares vanish
        if any(w[k] == w[k + 1] and w[k] <= 1 for k in range(len(w) - 1)):
            continue

        swapped = False
        for k in range(len(w) - 1):
            if w[k] > w[k + 1]:
                left, right = w[k], w[k + 1]

                # Standard undeformed swap
                for sc, repl in _swap_pair(left, right):
                    stack.append((coeff * sc, w[:k] + list(repl) + w[k + 2:]))

                # b-a swap: left is b-oscillator (>=2), right is a-oscillator (<=1)
                if left >= 2 and right <= 1:
                    gb = _gb_label(right, left)
                    rest = tuple(w[:k] + w[k + 2:])
                    kappa_raw.append((coeff * Fraction(-1), rest, gb))

                swapped = True
                break

        if not swapped:
            key = tuple(w)
            normal[key] = normal.get(key, Fraction(0)) + coeff

    return {k: v for k, v in normal.items() if v != 0}, kappa_raw


# ---------------------------------------------------------------------------
# Deformed polynomial multiplication and graded bracket
# ---------------------------------------------------------------------------

def poly_multiply_deformed(
    X: OscPoly,
    Y: OscPoly,
) -> Tuple[OscPoly, Dict[str, OscPoly]]:
    """
    Compute X · Y in the deformed algebra.

    Returns
    -------
    normal : OscPoly
        The kappa-free part (same as undeformed poly_multiply).
    kappa : dict[str, OscPoly]
        kappa[gb_label] = oscillator polynomial for the kappa coefficient.
        The full product is:  normal  +  kappa * sum_gb (gb_label * kappa[gb_label]).
    """
    normal: OscPoly = {}
    kappa_raw_all: List[Tuple[Fraction, OscWord, str]] = []

    for wx, cx in X.items():
        for wy, cy in Y.items():
            norm, raw = pbw_reduce_word_deformed(wx + wy)
            for w, c in norm.items():
                normal[w] = normal.get(w, Fraction(0)) + cx * cy * c
            for c, rest, gb in raw:
                kappa_raw_all.append((cx * cy * c, rest, gb))

    # Process kappa contributions: reduce each rest_word using undeformed reduction
    # (safe because kappa^2 = 0 prevents further deformed swaps in kappa-sector)
    kappa: Dict[str, OscPoly] = {}
    for c, rest, gb in kappa_raw_all:
        reduced = pbw_reduce_word(rest)
        if gb not in kappa:
            kappa[gb] = {}
        for w, rc in reduced.items():
            kappa[gb][w] = kappa[gb].get(w, Fraction(0)) + c * rc

    kappa = {
        gb: {k: v for k, v in poly.items() if v != 0}
        for gb, poly in kappa.items()
    }
    kappa = {gb: poly for gb, poly in kappa.items() if poly}

    return {k: v for k, v in normal.items() if v != 0}, kappa


def graded_bracket_deformed(
    X: OscPoly,
    pX: int,
    Y: OscPoly,
    pY: int,
) -> Tuple[OscPoly, Dict[str, OscPoly]]:
    """
    Compute [X, Y}_deformed = [X, Y}_0 + kappa * gamma(X, Y).

    Returns
    -------
    normal : OscPoly
        The kappa-free bracket (= Schema 1 bracket [X, Y}_0).
    kappa : dict[str, OscPoly]
        kappa[gb_label] = contribution to gamma(X, Y) from gb_label.
        So gamma(X, Y) = sum_gb (gb_label * kappa[gb_label]).
    """
    XY_norm, XY_kap = poly_multiply_deformed(X, Y)
    YX_norm, YX_kap = poly_multiply_deformed(Y, X)
    sign = Fraction((-1) ** (pX * pY))

    normal: OscPoly = {}
    for w, c in XY_norm.items():
        normal[w] = normal.get(w, Fraction(0)) + c
    for w, c in YX_norm.items():
        normal[w] = normal.get(w, Fraction(0)) - sign * c

    kappa: Dict[str, OscPoly] = {}
    for gb in set(XY_kap) | set(YX_kap):
        combined: OscPoly = {}
        for w, c in XY_kap.get(gb, {}).items():
            combined[w] = combined.get(w, Fraction(0)) + c
        for w, c in YX_kap.get(gb, {}).items():
            combined[w] = combined.get(w, Fraction(0)) - sign * c
        combined = {k: v for k, v in combined.items() if v != 0}
        if combined:
            kappa[gb] = combined

    return {k: v for k, v in normal.items() if v != 0}, kappa


# ---------------------------------------------------------------------------
# Gamma matrix computation
# ---------------------------------------------------------------------------

def compute_gamma_matrix(n: int) -> Tuple[List[dict], int]:
    """
    Compute all non-zero gamma_{XYZ} coefficients for C(n+1).

    The γ-map is the g-valued projection of the κ-contribution in the deformed
    bracket: [X,Y]_γ = [X,Y]_0 + κ·(γ_g(X,Y) + λ(X,Y)·K).
    The central K-component is tracked but excluded from the returned records.

    Returns (records, central_count) where central_count counts κ-contributions
    that had a non-zero K (scalar identity) component.

    Implementation note: κ-contributions can include oscillator monomials like
    b_k^+b_k^- that are not standalone generators but lie in span(generators + K).
    We solve in the extended basis {generators} ∪ {K} for exactness, then project
    onto g by dropping K.
    """
    gens, parities, even_basis, odd_basis = build_generators(n)
    all_basis = odd_basis + even_basis

    # Extend basis with K = identity (constant term) for exact expression of
    # bosonic number operators b_k^+b_k^- that arise in κ-contributions but are
    # not standalone generators (they appear only as sub-terms of Cartan elements).
    gens_with_K = dict(gens)
    gens_with_K["K"] = {(): Fraction(1)}
    basis_with_K = all_basis + ["K"]

    records: List[dict] = []
    central_count = 0
    for a, lx in enumerate(all_basis):
        for b in range(a, len(all_basis)):
            ly = all_basis[b]
            _, kappa = graded_bracket_deformed(
                gens[lx], parities[lx], gens[ly], parities[ly]
            )
            if not kappa:
                continue

            # For each gb parameter, express kappa[gb] in the extended basis
            # (generators + K) and accumulate contributions per output generator Z.
            gamma_by_z: Dict[str, Dict[str, Fraction]] = {}
            for gb, poly in kappa.items():
                z_coeffs = express_in_generators(poly, gens_with_K, basis_with_K)

                # Verify exactness: reconstruct poly and check residual is zero.
                reconstructed: OscPoly = {}
                for lz, coeff in z_coeffs.items():
                    for w, c in gens_with_K[lz].items():
                        reconstructed[w] = (
                            reconstructed.get(w, Fraction(0)) + coeff * c
                        )
                reconstructed = {k: v for k, v in reconstructed.items() if v != 0}
                assert reconstructed == poly, (
                    f"Non-zero residual for pair ({lx},{ly}) gb={gb}: "
                    f"poly={poly}, reconstructed={reconstructed}"
                )

                if "K" in z_coeffs and z_coeffs["K"] != 0:
                    central_count += 1

                for lz, coeff in z_coeffs.items():
                    if lz == "K":
                        continue  # Project onto g: drop scalar central component
                    if lz not in gamma_by_z:
                        gamma_by_z[lz] = {}
                    gamma_by_z[lz][gb] = (
                        gamma_by_z[lz].get(gb, Fraction(0)) + coeff
                    )

            for lz, gb_coeffs in gamma_by_z.items():
                clean = {gb: c for gb, c in gb_coeffs.items() if c != 0}
                if clean:
                    records.append(
                        {
                            "X": lx,
                            "Y": ly,
                            "Z": lz,
                            "coeff": {
                                gb: _fraction_to_str(c) for gb, c in clean.items()
                            },
                            "sign_rule": "graded",
                        }
                    )

    return records, central_count


# ---------------------------------------------------------------------------
# Schema 2 JSON builder
# ---------------------------------------------------------------------------

def _build_gb_matrix(n: int) -> dict:
    """Build the gb_matrix specification (2 × 2n layout)."""
    row_labels = ["a_1_p", "a_1_m"]
    col_labels = [
        f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")
    ]
    entries = [
        [f"gb_a1{sigma}_b{j}{s}" for j in range(1, n + 1) for s in ("p", "m")]
        for sigma in ("p", "m")
    ]
    return {
        "shape": [2, 2 * n],
        "row_labels": row_labels,
        "col_labels": col_labels,
        "entries": entries,
        "interpretation": (
            "entry[sigma_row][col] = gb_{sigma,j,s}; "
            "row sigma_row: 0=a_1^+, 1=a_1^-; "
            "col = 2*(j-1)+{0:b_j^+, 1:b_j^-}"
        ),
    }


def build_schema2(n: int) -> dict:
    """Build the complete Schema 2 dict for C(n+1)."""
    gens, parities, even_basis, odd_basis = build_generators(n)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim
    boson_labels = [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]

    gamma_matrix, central_count = compute_gamma_matrix(n)

    return {
        "schema_version": "5.0",
        "schema_layer": 2,
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
                "description": (
                    "Standard fermionic pair a_1^± satisfying CAR: {a_1^-, a_1^+} = 1"
                ),
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k = 1,...,{n}",
            },
        },
        "inhomogeneous_deformation": {
            "exchange_relation": "[b_j^s, a_1^sigma]_deformed = -gb_{sigma,j,s} * kappa",
            "sign_convention": (
                "Option A (Issue I05-1): "
                "b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa"
            ),
            "parameters": {
                "count": 4 * n,
                "description": (
                    f"4n = {4 * n} deformation parameters gb_{{sigma,j,s}} "
                    f"for sigma in {{+,-}}, j=1..{n}, s in {{+,-}}"
                ),
            },
            "gb_matrix": _build_gb_matrix(n),
            "gamma_matrix": gamma_matrix,
            "gamma_matrix_count": len(gamma_matrix),
            "gamma_projection_note": (
                "gamma_matrix records the g-valued projection of the deformation "
                "cocycle. κ-contributions that include a scalar K (central identity) "
                "component are projected onto g by dropping the K-part. "
                f"Number of (X,Y,gb) triples with non-zero K component: {central_count}."
            ),
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": date.today().isoformat(),
            "issue": "I05-1",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017), arXiv:1612.09400",
                "Aoi (2026), On the triviality of inhomogeneous deformations of osp(1|2n)",
                "docs/math/C_inhomogeneous_definition.md",
            ],
        },
    }


# ---------------------------------------------------------------------------
# Spot-check: verify gamma vs hand-computed example
# ---------------------------------------------------------------------------

def _spot_check(n: int, schema: dict) -> bool:
    """
    Verify the worked example from Issue I05-1 proposal:
        gamma(E_eps1_del1_pp, E_eps1_del1_mm) for n >= 1
    Expected:
        Z = E_eps1_del1_pm  with coeff  {"gb_a1m_b1p": "-1"}
        Z = E_eps1_del1_mp  with coeff  {"gb_a1p_b1m": "-1"}
    Returns True if verified.
    """
    gamma = schema["inhomogeneous_deformation"]["gamma_matrix"]
    lx, ly = "E_eps1_del1_pp", "E_eps1_del1_mm"
    hits = [r for r in gamma if r["X"] == lx and r["Y"] == ly]
    expected = {
        "E_eps1_del1_pm": {"gb_a1m_b1p": "-1"},
        "E_eps1_del1_mp": {"gb_a1p_b1m": "-1"},
    }
    found = {r["Z"]: r["coeff"] for r in hits}
    ok = all(found.get(z) == c for z, c in expected.items())
    if not ok:
        print(f"  SPOT-CHECK FAIL for n={n}: found {found}, expected {expected}")
    return ok


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    os.makedirs("data", exist_ok=True)
    all_ok = True
    for n in (1, 2, 3):
        schema = build_schema2(n)
        path = f"data/C_{n}_gamma.json"
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        count = schema["inhomogeneous_deformation"]["gamma_matrix_count"]
        ok = _spot_check(n, schema)
        status = "✓" if ok else "✗ SPOT-CHECK FAIL"
        print(
            f"C({n + 1})  n={n}  "
            f"dim=({schema['algebra']['dimension']['even']}|"
            f"{schema['algebra']['dimension']['odd']})  "
            f"gamma_entries={count}  {status}  -> {path}"
        )
        if not ok:
            all_ok = False
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

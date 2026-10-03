"""
C_gamma.py

Computes Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1) = osp(2|2n).

Mathematical basis: docs/math/C_inhomogeneous_definition.md

The inhomogeneous deformation is defined by:
  [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa
where sigma in {+,-} (fermionic index), j in {1..n} (boson index), s in {+,-} (boson sign).

The deformed bracket is [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y),
where gamma is a 2-cocycle.

The gamma coefficients are computed by evaluating the deformed oscillator relations
symbolically, deriving how the gb parameters enter each generator bracket.

Label convention for gb parameters:
  gb_{sigma}{k}_{s} where sigma in {p,m} and s in {p,m}
  e.g., gb_p1_p for gb_{a_1^+, b_1^+, +}

The gamma coefficients gamma_{abc} (indexed by X=a, Y=b, Z=c in basis) are:
  gamma(X,Y) = sum_Z gamma_{Z;XY} * Z
"""

from __future__ import annotations
import json
import datetime
import os
import sys
from fractions import Fraction
from itertools import product as iproduct

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_generators, build_basis_order, _graded_bracket,
    _build_decomposition_matrix, _solve_decomposition,
    _normalize_word, _add, _scale, _single, _parity_of_osc
)


# ---------------------------------------------------------------------------
# Symbolic gb parameters
# ---------------------------------------------------------------------------
# We represent elements as dicts:
#   {(word_tuple, gb_monomial_tuple): coeff}
# where gb_monomial_tuple is a tuple of gb parameter labels (sorted)
# and the total is the "deformation contribution" (coefficient of kappa).
#
# For simplicity in this implementation, we work linearly in gb parameters
# (first-order deformation theory). gamma(X,Y) is linear in the gb parameters.

def gb_label(sigma: str, k: int, s: str) -> str:
    """gb_{sigma,k,s}: sigma in {p,m}, k=boson index, s in {p,m}"""
    return f"gb_{sigma}{k}_{s}"


def build_gb_params(n: int) -> list:
    """Return list of all 4n gb parameter labels for C(n+1)."""
    params = []
    for sigma in ["p", "m"]:
        for k in range(1, n + 1):
            for s in ["p", "m"]:
                params.append(gb_label(sigma, k, s))
    return params


def compute_gamma_coefficients(n: int) -> list:
    """
    Compute gamma_{Z;XY} coefficients for C(n+1).

    The deformation arises from the modified commutation relation:
      [b_j^s, a_1^sigma]_deformed = 0 + kappa * (-gb_{sigma,j,s})

    For a bracket [X,Y] involving generators where one uses b_j^s and the
    other uses a_1^sigma (or vice versa), the deformation contributes
    gamma(X,Y) terms.

    Strategy: For each pair (X,Y) of basis generators, compute the "deformed
    part" of [X,Y] by:
    1. Expressing X and Y as oscillator words.
    2. Computing which oscillator pairs (b_j^s, a_1^sigma) or (a_1^sigma, b_j^s)
       appear as adjacent factors in the product X*Y - (-1)^{pX pY} Y*X.
    3. Each such pair contributes -gb_{sigma,j,s} * kappa * (remaining oscillators).

    Since we work to first order in gb (the cocycle is linear in gb),
    we compute gamma(X,Y) = sum over all adjacent (b,a) or (a,b) pairs.
    """
    gens = build_generators(n)
    basis = build_basis_order(n)
    parity = {k: v[1] for k, v in gens.items()}

    # Build decomposition matrix for the algebra
    words, word_to_idx, A = _build_decomposition_matrix(gens, basis)

    gb_params = build_gb_params(n)
    gb_to_idx = {g: i for i, g in enumerate(gb_params)}

    gamma_entries = []

    # For each basis pair (X, Y), compute the deformation contribution
    # gamma(X,Y): the part of the bracket that comes from the gb deformation.
    #
    # The key insight: the deformation is in the oscillator relations.
    # In the undeformed algebra, [b_j^s, a_1^sigma] = 0.
    # In the deformed algebra, [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.
    #
    # When computing [X,Y] via the oscillator representation, any time we
    # commute b_j^s past a_1^sigma (or vice versa), we get a gb contribution.
    #
    # Implementation: compute the "gb contribution" from each generator's
    # oscillator word products by tracking which mixed commutations arise.

    for X_label in basis:
        for Y_label in basis:
            X_elem, pX = gens[X_label]
            Y_elem, pY = gens[Y_label]

            # Compute gamma(X,Y) as the deformation contribution
            gamma_elem = _compute_deformation(X_elem, Y_elem, pX, pY, n, gb_params)

            if not gamma_elem:
                continue

            # gamma_elem is dict {(word, gb_label): coeff}
            # Group by gb_label and decompose each word-group into generators

            # Collect: {gb_label: {word: total_coeff}}
            by_gb = {}
            for (word, gb), coeff in gamma_elem.items():
                if gb not in by_gb:
                    by_gb[gb] = {}
                by_gb[gb][word] = by_gb[gb].get(word, Fraction(0)) + coeff

            for gb_lbl, word_dict in by_gb.items():
                # Clean zeros
                word_dict = {w: c for w, c in word_dict.items() if c != 0}
                if not word_dict:
                    continue

                # Decompose into generators
                decomp = _solve_decomposition(word_dict, words, word_to_idx, A, basis)
                if decomp is None or not decomp:
                    continue

                for Z_label, coeff in decomp.items():
                    if coeff != 0:
                        gamma_entries.append({
                            "X": X_label,
                            "Y": Y_label,
                            "Z": Z_label,
                            "gb": gb_lbl,
                            "coeff": str(coeff),
                            "description": f"gamma({X_label},{Y_label})[{Z_label}] = {coeff} * {gb_lbl}"
                        })

    return gamma_entries


def _compute_deformation(X_elem: dict, Y_elem: dict, pX: int, pY: int,
                          n: int, gb_params: list) -> dict:
    """
    Compute the first-order deformation contribution from the gb parameters
    for the bracket [X,Y]_gamma - [X,Y]_0.

    Returns dict {(word, gb_label): coeff} representing the linear-in-gb
    deformation term (coefficient of kappa).

    Strategy: enumerate all oscillator word products and collect the
    "mixed commutation" residuals where a bosonic oscillator b_j^s
    commutes past a_1^sigma (or vice versa).
    """
    result = {}

    for wX, cX in X_elem.items():
        for wY, cY in Y_elem.items():
            # Compute the deformation from wX * wY
            xy_def = _word_product_deformation(wX, wY, n)
            for (word, gb), c in xy_def.items():
                key = (word, gb)
                result[key] = result.get(key, Fraction(0)) + cX * cY * c

            # Compute the deformation from (-1)^{pX*pY} * wY * wX
            sign = Fraction((-1) ** (pX * pY))
            yx_def = _word_product_deformation(wY, wX, n)
            for (word, gb), c in yx_def.items():
                key = (word, gb)
                result[key] = result.get(key, Fraction(0)) - sign * cX * cY * c

    return {k: v for k, v in result.items() if v != 0}


def _word_product_deformation(w1: tuple, w2: tuple, n: int) -> dict:
    """
    Compute the first-order gb deformation arising when multiplying word w1 * w2.

    This collects terms where a bosonic oscillator b_j^s commutes past
    a fermionic oscillator a_1^sigma, contributing -gb_{sigma,j,s} * (remaining_word).

    Returns dict {(remaining_word, gb_label): coeff}.
    """
    combined = w1 + w2
    return _collect_mixed_deformations(combined, n)


def _collect_mixed_deformations(word: tuple, n: int) -> dict:
    """
    Collect deformation contributions from commuting oscillators in a word to PBW order.

    At each swap where a bosonic oscillator passes a fermionic oscillator (or vice versa),
    the deformation gives a contribution -gb_{sigma,j,s} * (word without this pair).

    Works recursively like _normalize_word but collects deformation terms.
    """
    if len(word) <= 1:
        return {}

    # Check if in order
    in_order = True
    for i in range(len(word) - 1):
        from C_generators import _osc_order
        if _osc_order(word[i], n) > _osc_order(word[i + 1], n):
            in_order = False
            break

    if in_order:
        # No more swaps needed; check for adjacent same fermionic
        for i in range(len(word) - 1):
            if word[i] == word[i + 1] and _parity_of_osc(word[i]) == 1:
                return {}
        return {}

    result = {}

    # Find first inversion
    from C_generators import _osc_order, _parity_of_osc as _posc
    for i in range(len(word) - 1):
        if _osc_order(word[i], n) > _osc_order(word[i + 1], n):
            osc1, osc2 = word[i], word[i + 1]
            prefix = word[:i]
            suffix = word[i + 2:]

            p1 = _parity_of_osc(osc1)
            p2 = _parity_of_osc(osc2)

            if p1 == 1 and p2 == 0:
                # Fermionic osc1 commutes past bosonic osc2: deformation!
                # [osc2, osc1]_deformed = -gb_{sigma,j,s} (where osc1=a_1^sigma, osc2=b_j^s)
                # But wait: osc1 has higher PBW order than osc2. So osc1 is fermionic (order 1)
                # and osc2 is bosonic (order 2+). osc1 is a_1_p or a_1_m (order 0,1)
                # and osc2 is b_k^± (order 2+). But order of a_1_m (1) < b_k_p (2),
                # so a fermionic oscillator (a_1_m, order=1) can't have higher order than bosonic.
                # Actually a_1_p has order 0, a_1_m has order 1, b_1_p has order 2, etc.
                # So fermionic always has lower order than bosonic → no inversion a→b.
                # Inversion (boson before fermion): osc1=bosonic (order 2+) before osc2=fermionic (order 0,1)
                pass

            if p1 == 0 and p2 == 1:
                # Bosonic osc1 commutes past fermionic osc2: DEFORMATION
                # In undeformed: [b_j^s, a_1^sigma] = 0 → no residual
                # In deformed: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
                gb_lbl = _gb_from_osc(osc1, osc2, n)
                if gb_lbl is not None:
                    # Contribution: -gb_{sigma,j,s} * (prefix + suffix) normalized
                    remaining = prefix + suffix
                    from C_generators import _normalize_word
                    normalized_remaining = _normalize_word(remaining, n)
                    for rem_word, rem_coeff in normalized_remaining.items():
                        key = (rem_word, gb_lbl)
                        result[key] = result.get(key, Fraction(0)) + (-1) * rem_coeff

                # Continue collecting from swapped word (undeformed part)
                sign = Fraction(1)  # Bosonic-fermionic: commute with sign +1 in undeformed
                swapped = prefix + (osc2, osc1) + suffix
                sub_result = _collect_mixed_deformations(swapped, n)
                for k, v in sub_result.items():
                    result[k] = result.get(k, Fraction(0)) + sign * v

            elif p1 == 1 and p2 == 1:
                # Fermionic-fermionic: undeformed, but check for zero
                sign = Fraction(-1)
                from C_generators import _anticommutator_fermion_fermion
                res = _anticommutator_fermion_fermion(osc1, osc2)
                swapped = prefix + (osc2, osc1) + suffix
                sub_result = _collect_mixed_deformations(swapped, n)
                for k, v in sub_result.items():
                    result[k] = result.get(k, Fraction(0)) + sign * v
                # Residual from anticommutator (scalar, no deformation)

            elif p1 == 0 and p2 == 0:
                # Bosonic-bosonic: undeformed commutation
                sign = Fraction(1)
                swapped = prefix + (osc2, osc1) + suffix
                sub_result = _collect_mixed_deformations(swapped, n)
                for k, v in sub_result.items():
                    result[k] = result.get(k, Fraction(0)) + sign * v
                # Residual (scalar [b_i^-, b_j^+] = delta_ij): no deformation

            break  # Only handle first inversion

    return {k: v for k, v in result.items() if v != 0}


def _gb_from_osc(boson_osc: str, fermion_osc: str, n: int) -> str:
    """
    Given a bosonic oscillator (b_j^s) and fermionic oscillator (a_1^sigma),
    return the gb parameter label gb_{sigma,j,s}.

    The relation is: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
    """
    if fermion_osc == "a_1_p":
        sigma = "p"
    elif fermion_osc == "a_1_m":
        sigma = "m"
    else:
        return None

    parts = boson_osc.split("_")
    if len(parts) != 3 or parts[0] != "b":
        return None
    k = int(parts[1])
    s = parts[2]

    return gb_label(sigma, k, s)


def build_schema2(n: int) -> dict:
    """Build Schema 2 JSON for C(n+1) with bosonic rank n."""
    gb_params = build_gb_params(n)
    gamma_entries = compute_gamma_coefficients(n)

    # Build gb_matrix description
    gb_matrix_params = {}
    for gb in gb_params:
        parts = gb.split("_")
        # Format: gb_p1_p -> sigma=p, k=1, s=p
        sigma = parts[1][0]
        k = int(parts[1][1])
        s = parts[2]
        gb_matrix_params[gb] = {
            "sigma": "+" if sigma == "p" else "-",
            "k": k,
            "s": "+" if s == "p" else "-",
            "parity": 1,
            "description": f"gb between a_1^{'+' if sigma=='p' else '-'} and b_{k}^{'+' if s=='p' else '-'}"
        }

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "description": "Schema 2: Inhomogeneous deformation (gamma structure) for C(n+1)",
        "gb_matrix": {
            "size": f"2 x {2*n}",
            "total_parameters": 4 * n,
            "parameters": gb_matrix_params,
            "convention": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
        },
        "gamma_coefficients": gamma_entries,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
            "note": "Gamma coefficients are linear in gb parameters. Each entry gives the coefficient of kappa*Z in the deformed bracket [X,Y]_gamma - [X,Y]_0.",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat, Sciarrino, Sorba (2000)"
            ]
        }
    }
    return schema


def verify_schema2_vs_schema1(n: int) -> bool:
    """Verify that gamma entries involve only generators from Schema 1 basis."""
    with open(os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")) as f:
        schema1 = json.load(f)
    basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    basis_set = set(basis)

    schema2 = build_schema2(n)
    for entry in schema2["gamma_coefficients"]:
        if entry["X"] not in basis_set:
            return False
        if entry["Y"] not in basis_set:
            return False
        if entry["Z"] not in basis_set:
            return False
    return True


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C_{n}_gamma.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema2(n)
        n_gamma = len(schema["gamma_coefficients"])
        print(f"  gb parameters: {schema['gb_matrix']['total_parameters']}")
        print(f"  gamma entries: {n_gamma}")

        ok = verify_schema2_vs_schema1(n)
        print(f"  Consistency with Schema 1: {'PASS' if ok else 'FAIL'}")

        out_path = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {out_path}")


if __name__ == "__main__":
    main()

"""
C_gamma.py — Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1).

The deformation is parametrized by 4n gb parameters:
  gb[sigma][j][s] = gb_{a_1^sigma, b_j^s}   (sigma,s in {p,m}, j=1..n)
satisfying [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

Gamma coefficients gamma_{abc} encode the deformed bracket:
  [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)

Reference: docs/math/C_inhomogeneous_definition.md
"""

import json
import os
import sys
from datetime import date
from fractions import Fraction
from itertools import product

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (build_basis, build_parity, gen_realization,
                           osc_order, _normal_order, multiply_elements)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


# ---------------------------------------------------------------------------
# Deformed bracket computation
#
# In the deformed algebra A = V ⊕ C*K ⊕ C*kappa, the exchange relations
# between bosonic and fermionic oscillators become:
#   [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
#
# The gamma cocycle gamma(X, Y) is the coefficient of kappa in [X,Y]_deformed.
# We compute it symbolically: replace the deformed commutator contribution.
#
# For generators X, Y expressed as oscillator monomials, the deformed bracket
# picks up extra kappa terms from each application of the deformed exchange.
# Specifically, when normal-ordering a product of oscillators, each swap of
# (b_j^s, a_1^sigma) produces an extra -gb_{sigma,j,s} * kappa term.
#
# Method: compute graded_bracket(X, Y) in the DEFORMED algebra by tracking
# kappa contributions. We represent elements as (normal_part, kappa_part)
# where normal_part is the standard element and kappa_part is the gamma
# coefficient (linear in gb parameters).
# ---------------------------------------------------------------------------

def gb_label(sigma, j, s):
    """Return gb parameter name: gb_p_j_p, gb_m_j_m, etc."""
    return f"gb_{sigma}_{j}_{s}"


def build_gb_params(n):
    """Return list of all 4n gb parameter labels."""
    params = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                params.append(gb_label(sigma, j, s))
    return params


def _normal_order_deformed(mon, order_idx, n):
    """
    Normal-order a monomial tuple tracking kappa contributions.
    Returns (normal_terms, kappa_terms):
      normal_terms: dict tuple->Fraction  (coefficient in normal algebra)
      kappa_terms: dict tuple -> dict{gb_label: Fraction}
        (coefficient of kappa*gb_label in the deformed algebra)

    Deformed exchange: when swapping (b_j^s = "bjX") OVER (a_1^sigma = "a1Y"):
    If the swap is "bjX then a1Y" → "a1Y then bjX", the deformation gives:
      extra term: +gb_{sigma,j,s} * (remaining monomial without both)
    Note: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa →
      b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa
    When we swap (a1Y at position i) and (bjX at position i+1) because ia > ib:
      a1Y is "earlier" in order, bjX is "later" — but order is a1<b, so
      if we have (bjX, a1Y) at positions (i,i+1) with idx[bjX] > idx[a1Y]:
        swap: a1Y bjX - (-1)^{p(bjX)*p(a1Y)} * (deformed exchange term)
        Since p(bjX)=0, p(a1Y)=1: sign = (-1)^0 = 1. Normal swap.
        Deformed extra: when b*a → a*b, the deformed relation gives:
          b*a = a*b - gb_{sigma,j,s} * kappa
        So extra kappa term: -gb_{sigma,j,s} * (rest of monomial)

    Wait, let me be careful with sign convention.
    [b_j^s, a_1^sigma] = b_j^s * a_1^sigma - a_1^sigma * b_j^s = -gb_{sigma,j,s} * kappa
    So: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa

    In normal ordering, when we encounter (b_j^s, a_1^sigma) needing a swap:
    b*a → a*b + extra: (b*a = a*b - gb*kappa) → extra = -gb * rest
    """
    # Represent as list of (normal_coeff_dict, kappa_coeff_dict)
    # where kappa_coeff_dict maps gb_label -> Fraction coefficient

    # Start: one monomial with unit coefficient, no kappa part
    # State: list of (monomial, normal_coeff, kappa_coeff_dict)
    states = [(list(mon), Fraction(1), {})]

    for _ in range(len(mon) ** 2 + 10):  # bounded iterations
        new_states = []
        changed = False
        for m, coeff, kappa_c in states:
            swapped = False
            for i in range(len(m) - 1):
                a, b = m[i], m[i + 1]
                ia, ib = order_idx[a], order_idx[b]

                pa = 1 if a.startswith("a") else 0
                pb = 1 if b.startswith("a") else 0

                if ia > ib:
                    sign = (-1) ** (pa * pb)

                    # Remainder from CAR/CCR (same as undeformed)
                    remainder = None
                    if pa == 0 and pb == 0:
                        if a.endswith("m") and b.endswith("p") and a[:-1] == b[:-1]:
                            remainder = m[:i] + m[i + 2:]
                    elif pa == 1 and pb == 1:
                        if a == "a1m" and b == "a1p":
                            remainder = m[:i] + m[i + 2:]

                    # Deformed exchange: b_j^s * a_1^sigma → a_1^sigma * b_j^s - gb*kappa
                    # This occurs when a (higher idx) is a boson b_j^s and
                    # b (lower idx) is a fermion a_1^sigma
                    gb_extra = None
                    if pa == 0 and pb == 1:
                        # a = boson b_j^X, b = fermion a_1^Y
                        # swap: b*a → a*b (normal swap, sign=1) - gb*kappa*(rest)
                        # Identify sigma and s from labels
                        if a.startswith("b") and b.startswith("a1"):
                            # a = "b{j}p" or "b{j}m" → s
                            j_str = a[1:-1]  # digits
                            if j_str.isdigit():
                                j = int(j_str)
                                s = a[-1]  # p or m
                                sigma = b[2]  # a1p or a1m → index 2 gives p or m
                                gb_lbl = gb_label(sigma, j, s)
                                gb_extra = (gb_lbl, m[:i] + m[i + 2:])

                    swapped_m = m[:i] + [b, a] + m[i + 2:]
                    new_states.append((swapped_m, coeff * sign, dict(kappa_c)))

                    if remainder is not None:
                        new_states.append((remainder, coeff, dict(kappa_c)))

                    if gb_extra is not None:
                        gb_lbl, rest = gb_extra
                        new_kappa = dict(kappa_c)
                        new_kappa[gb_lbl] = new_kappa.get(gb_lbl, Fraction(0)) - coeff
                        new_states.append((rest, Fraction(0), new_kappa))
                        # Note: we add rest to new_states with zero normal coeff
                        # but non-zero kappa coeff

                    swapped = True
                    changed = True
                    break

                elif ia == ib and pa == 1:
                    # Adjacent identical fermions in normal order → zero
                    swapped = True
                    changed = True
                    break

            if not swapped:
                new_states.append((m, coeff, kappa_c))

        if not changed:
            break
        states = new_states

    # Aggregate results
    normal_terms = {}
    kappa_terms = {}

    for m, coeff, kappa_c in states:
        t = tuple(m)
        # normal part
        if coeff != 0:
            normal_terms[t] = normal_terms.get(t, Fraction(0)) + coeff
        # kappa part
        for gb_lbl, c in kappa_c.items():
            if c != 0:
                if t not in kappa_terms:
                    kappa_terms[t] = {}
                kappa_terms[t][gb_lbl] = kappa_terms[t].get(gb_lbl, Fraction(0)) + c

    normal_terms = {k: v for k, v in normal_terms.items() if v != 0}
    kappa_terms = {k: {g: c for g, c in v.items() if c != 0}
                   for k, v in kappa_terms.items() if v}
    kappa_terms = {k: v for k, v in kappa_terms.items() if v}

    return normal_terms, kappa_terms


def multiply_deformed(d1, d2, order_idx, n):
    """Multiply two elements in the deformed algebra, tracking kappa terms."""
    normal_out = {}
    kappa_out = {}

    for m1, c1 in d1.items():
        for m2, c2 in d2.items():
            norm, kappa = _normal_order_deformed(m1 + m2, order_idx, n)
            for m, c in norm.items():
                normal_out[m] = normal_out.get(m, Fraction(0)) + c1 * c2 * c
            for m, gb_dict in kappa.items():
                if m not in kappa_out:
                    kappa_out[m] = {}
                for gb_lbl, c in gb_dict.items():
                    kappa_out[m][gb_lbl] = kappa_out[m].get(gb_lbl, Fraction(0)) + c1 * c2 * c

    normal_out = {k: v for k, v in normal_out.items() if v != 0}
    kappa_out = {k: {g: c for g, c in v.items() if c != 0}
                 for k, v in kappa_out.items() if v}
    return normal_out, {k: v for k, v in kappa_out.items() if v}


def graded_bracket_deformed(X_real, Y_real, pX, pY, order_idx, n):
    """
    Compute [X,Y}_deformed = XY - (-1)^{pX*pY} YX in the deformed algebra.
    Returns (normal_bracket, kappa_bracket):
      normal_bracket: dict tuple->Fraction (undeformed part)
      kappa_bracket: dict tuple -> dict{gb_label: Fraction} (gamma part)
    """
    XY_norm, XY_kap = multiply_deformed(X_real, Y_real, order_idx, n)
    YX_norm, YX_kap = multiply_deformed(Y_real, X_real, order_idx, n)
    sign = (-1) ** (pX * pY)

    normal_br = dict(XY_norm)
    for m, c in YX_norm.items():
        normal_br[m] = normal_br.get(m, Fraction(0)) - sign * c
    normal_br = {k: v for k, v in normal_br.items() if v != 0}

    kappa_br = dict(XY_kap)
    for m, gb_dict in YX_kap.items():
        if m not in kappa_br:
            kappa_br[m] = {}
        for gb_lbl, c in gb_dict.items():
            kappa_br[m][gb_lbl] = kappa_br[m].get(gb_lbl, Fraction(0)) - sign * c
    kappa_br = {k: {g: c for g, c in v.items() if c != 0}
                for k, v in kappa_br.items() if v}

    return normal_br, {k: v for k, v in kappa_br.items() if v}


def decompose_kappa_in_basis(kappa_element, realization, basis_all):
    """
    Decompose kappa element (dict: monomial -> {gb_label: Fraction})
    in terms of basis generators.
    Returns dict: (Z, gb_label) -> Fraction coefficient.
    """
    # For each gb_label, collect the monomial -> coeff mapping
    gb_elements = {}
    for m, gb_dict in kappa_element.items():
        for gb_lbl, c in gb_dict.items():
            if gb_lbl not in gb_elements:
                gb_elements[gb_lbl] = {}
            gb_elements[gb_lbl][m] = gb_elements[gb_lbl].get(m, Fraction(0)) + c

    result = {}
    for gb_lbl, element in gb_elements.items():
        # Decompose element in basis (same method as in C_generators.py)
        remaining = dict(element)
        # Handle scalar separately
        if () in remaining:
            remaining.pop(())  # K contribution ignored for kappa part

        for _ in range(len(basis_all) + 1):
            for g in basis_all:
                g_real = realization[g]
                for pivot, pivot_coeff in g_real.items():
                    if pivot != () and pivot in remaining and remaining[pivot] != 0:
                        c = remaining[pivot] / pivot_coeff
                        if c != 0:
                            key = (g, gb_lbl)
                            result[key] = result.get(key, Fraction(0)) + c
                            for m, v in g_real.items():
                                remaining[m] = remaining.get(m, Fraction(0)) - c * v
                        break
            remaining = {k: v for k, v in remaining.items() if v != 0}
            if not remaining or remaining.keys() == {()}:
                break

    return {k: v for k, v in result.items() if v != 0}


def compute_gamma(n):
    """
    Compute gamma coefficients for C(n+1) inhomogeneous deformation.
    Returns list of dicts: {X, Y, Z, gb_label, coeff}.
    """
    odd, even = build_basis(n)
    basis_all = odd + even
    parity = build_parity(odd, even)
    realization = gen_realization(n)
    order_idx = {l: i for i, l in enumerate(osc_order(n))}

    gamma_entries = []
    for i, X in enumerate(basis_all):
        for j, Y in enumerate(basis_all):
            if i > j:
                continue
            pX, pY = parity[X], parity[Y]
            _, kappa_br = graded_bracket_deformed(
                realization[X], realization[Y], pX, pY, order_idx, n)
            if not kappa_br:
                continue
            decomp = decompose_kappa_in_basis(kappa_br, realization, basis_all)
            for (Z, gb_lbl), c in decomp.items():
                gamma_entries.append({
                    "X": X, "Y": Y, "Z": Z,
                    "gb_label": gb_lbl,
                    "coeff": str(c)
                })
    return gamma_entries


def build_schema2(n):
    odd, even = build_basis(n)
    gb_params = build_gb_params(n)

    gamma = compute_gamma(n)

    # Build gb_matrix description
    gb_param_desc = {}
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                lbl = gb_label(sigma, j, s)
                gb_param_desc[lbl] = f"gb_{{a_1^{sigma}, b_{j}^{s}}}"

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "gb_matrix": {
            "shape": [2, 2 * n],
            "count": 4 * n,
            "parity": 1,
            "index_description": "gb[sigma][j][s] = gb_{a_1^sigma, b_j^s}",
            "parameters": gb_param_desc,
            "exchange_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
        },
        "gamma_coefficients": gamma,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
            "description": "Gamma cocycle [X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y)"
        }
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating C_{n}_gamma.json (n={n})...")
        schema = build_schema2(n)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Gamma entries: {len(schema['gamma_coefficients'])}")
        print(f"  gb parameters ({4*n}): {schema['gb_matrix']['parameters']}")
    print("Done.")


if __name__ == "__main__":
    main()

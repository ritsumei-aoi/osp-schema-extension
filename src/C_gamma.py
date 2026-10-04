"""
Schema 2 (gamma structure) generator for C(n+1) = osp(2|2n).

The inhomogeneous deformation is defined by the gb matrix: 4n parameters
gb_{sigma, j, s} for sigma in {+,-}, j in {1,...,n}, s in {+,-}.

Deformed commutator: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

The gamma 2-cocycle gamma(X, Y) is derived by substituting the deformed
oscillator relations into the graded bracket computation and collecting
the terms proportional to kappa.

Reference: docs/math/C_inhomogeneous_definition.md
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_basis, build_parity_dict, build_generator_realizations,
    graded_bracket, express_in_basis, _normalize, osc_type
)


# ---------------------------------------------------------------------------
# Deformation parameters (symbolic gb matrix)
# ---------------------------------------------------------------------------

def gb_label(sigma, j, s):
    """
    Return symbolic label for gb_{sigma, j, s}.
    sigma in {'p','m'}, j in 1..n, s in {'p','m'}
    """
    return f"gb_a1{sigma}_b{j}{s}"


def get_all_gb_labels(n):
    """Return all 4n symbolic gb parameter labels."""
    labels = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                labels.append(gb_label(sigma, j, s))
    return labels


# ---------------------------------------------------------------------------
# Deformed normalization: extends _normalize to track kappa contributions.
# ---------------------------------------------------------------------------
# In the deformed theory, the relation [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
# means: when we pass a b-oscillator past an a_1 oscillator (or vice versa),
# we also get a kappa term.
#
# We represent the result as a pair:
#   (undeformed_part: dict{mono: Fraction}, kappa_part: dict{mono: dict{gb_label: Fraction}})
#
# The kappa_part maps each oscillator monomial (of degree 2 less than original)
# to a linear combination of gb parameters with rational coefficients.

def _normalize_deformed(word, n):
    """
    Normalize a word, tracking kappa contributions from deformed commutators.

    Returns:
        (undeformed, kappa_terms) where
        undeformed: dict {tuple: Fraction} — undeformed normal form
        kappa_terms: dict {tuple: dict{gb_label: Fraction}} — monomials * kappa
    """
    # Stack items: (word_list, undeformed_coeff: Fraction, kappa_coeff: dict{gb_label: Fraction})
    # kappa_coeff is the accumulated gb-linear prefactor for this word
    init_kappa = {}  # empty = no kappa term yet
    stack = [(list(word), Fraction(1), {})]

    undeformed = {}
    kappa_terms = {}  # {mono: {gb_label: Fraction}}

    def add_kappa(mono, scalar, gb_dict):
        """Add scalar * gb_dict contribution to kappa_terms[mono]."""
        if not gb_dict:
            return
        tup = tuple(mono)
        if tup not in kappa_terms:
            kappa_terms[tup] = {}
        for gb, c in gb_dict.items():
            kappa_terms[tup][gb] = kappa_terms[tup].get(gb, Fraction(0)) + scalar * c

    def scale_gb(gb_dict, scalar):
        return {k: scalar * v for k, v in gb_dict.items()}

    def add_gb(d1, d2):
        result = dict(d1)
        for k, v in d2.items():
            result[k] = result.get(k, Fraction(0)) + v
        return {k: v for k, v in result.items() if v != 0}

    def order_idx(label):
        order = ["a_1_p", "a_1_m"] + [x for k in range(1, n + 1)
                                        for x in (f"b_{k}_p", f"b_{k}_m")]
        return order.index(label)

    while stack:
        w, c, kgb = stack.pop()

        moved = False
        for i in range(len(w) - 1):
            if order_idx(w[i]) > order_idx(w[i + 1]):
                a, b = w[i], w[i + 1]
                moved = True
                ta, tb = osc_type(a), osc_type(b)

                if ta == "f" and tb == "f":
                    # Standard CAR (unchanged by deformation)
                    anticom = Fraction(0)
                    if (a == "a_1_m" and b == "a_1_p") or (a == "a_1_p" and b == "a_1_m"):
                        anticom = Fraction(1)
                    # Swap: -b·a
                    nw = list(w); nw[i], nw[i+1] = b, a
                    stack.append((nw, -c, kgb))
                    if anticom != 0:
                        rem = w[:i] + w[i+2:]
                        stack.append((rem, c * anticom, kgb))

                elif ta == "b" and tb == "b":
                    # Standard CCR (unchanged)
                    com = Fraction(0)
                    if a.endswith("_m") and b.endswith("_p") and a[:-2] == b[:-2]:
                        com = Fraction(1)
                    nw = list(w); nw[i], nw[i+1] = b, a
                    stack.append((nw, c, kgb))
                    if com != 0:
                        rem = w[:i] + w[i+2:]
                        stack.append((rem, c * com, kgb))

                else:
                    # Mixed: one boson (b_j^s), one fermion (a_1^sigma)
                    # Undeformed: just swap (free commutation)
                    # Deformed: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
                    #   So b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa * (surrounding word)

                    # Determine which is boson and which is fermion, and the direction
                    if ta == "b":
                        # w[i]=b_j^s, w[i+1]=a_1^sigma (out of order, need to swap)
                        boson_label = a  # b_j^s
                        ferm_label = b   # a_1^sigma
                    else:
                        # w[i]=a_1^sigma (higher index?), w[i+1]=b_j^s (lower index?)
                        # Actually order_idx(w[i]) > order_idx(w[i+1]) means a_1 is out of order
                        # i.e., a_1 comes AFTER b in the word but should come BEFORE
                        boson_label = b  # b_j^s
                        ferm_label = a   # a_1^sigma

                    # Parse boson: b_{j}_{s} → j, s
                    parts = boson_label.split("_")  # ['b', 'k', 's']
                    j = int(parts[1])
                    bs = parts[2]  # 'p' or 'm'

                    # Parse fermion: a_1_{sigma} → sigma
                    sigma = ferm_label[-1]  # 'p' or 'm'

                    # gb label for [b_j^s, a_1^sigma]
                    # The deformed commutator is: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,bs} * kappa
                    gb = gb_label(sigma, j, bs)

                    # Swap term (undeformed part): a·b with same coeff
                    nw = list(w); nw[i], nw[i+1] = b, a
                    stack.append((nw, c, kgb))

                    # Kappa term: -c * gb * kappa * (surrounding word)
                    # Remaining word after removing positions i, i+1
                    rem = w[:i] + w[i+2:]
                    # Kappa coefficient for this piece: kgb + {gb: -c}
                    # But kgb is already multiplied into c — we need:
                    # new kappa term: kgb * (-c) is not right...
                    # Actually: the full kappa contribution is:
                    # c * kgb * (-gb * kappa) = -c * gb * kappa * kgb_word
                    # Since kappa^2=0, if kgb is already non-empty, the kappa term is 0.
                    if not kgb:
                        # First kappa insertion: coefficient is -c, gb parameter is {gb: Fraction(1)}
                        new_kappa_for_rem = {gb: -c}
                        add_kappa(rem, Fraction(1), new_kappa_for_rem)
                    # else: kgb already has a kappa, second kappa gives kappa^2=0

                break

        if not moved:
            # Check for adjacent identical fermions
            has_zero = False
            for i in range(len(w) - 1):
                if osc_type(w[i]) == "f" and w[i] == w[i+1]:
                    has_zero = True
                    break
            if has_zero:
                continue
            # Contribute to undeformed part
            key = tuple(w)
            undeformed[key] = undeformed.get(key, Fraction(0)) + c
            # If there's a kappa coefficient (kgb non-empty), this would be a kappa term
            # But in practice kgb accumulates only when we have a kappa term from a swap,
            # which we handle via add_kappa above
            if kgb:
                add_kappa(list(w), c, kgb)

    return (
        {k: v for k, v in undeformed.items() if v != 0},
        {k: {gb: c for gb, c in v.items() if c != 0}
         for k, v in kappa_terms.items() if any(v.values())}
    )


def compute_gamma(n):
    """
    Compute gamma coefficients for C(n+1).

    gamma(X, Y) is the 2-cocycle such that [X,Y]_deformed = [X,Y]_0 + kappa * gamma(X,Y).

    Returns list of dicts: {X, Y, Z, gb_coeffs} where
    gamma(X,Y) = sum_Z gb_coeffs[Z] * Z (as a linear comb of basis generators).
    """
    even_basis, odd_basis = build_basis(n)
    basis = odd_basis + even_basis
    parity = build_parity_dict(even_basis, odd_basis)
    gens = build_generator_realizations(n)

    gamma_entries = []

    for xi, X in enumerate(basis):
        for yi in range(xi, len(basis)):
            Y = basis[yi]
            pX, pY = parity[X], parity[Y]

            # Compute the bracket using deformed normalization
            # [X, Y}_deformed = sum_monomials of X * sum_monomials of Y - (-1)^{pX*pY} * reverse
            sign = Fraction((-1) ** (pX * pY))

            kappa_result = {}  # {mono: {gb: coeff}}

            def add_kappa_result(mono, gb_dict, scalar):
                key = tuple(mono)
                if key not in kappa_result:
                    kappa_result[key] = {}
                for gb, c in gb_dict.items():
                    kappa_result[key][gb] = kappa_result[key].get(gb, Fraction(0)) + scalar * c

            # XY term
            for mx, cx in gens[X].items():
                for my, cy in gens[Y].items():
                    _, kap = _normalize_deformed(list(mx) + list(my), n)
                    for mono, gb_dict in kap.items():
                        add_kappa_result(list(mono), gb_dict, cx * cy)

            # -sign * YX term
            for my, cy in gens[Y].items():
                for mx, cx in gens[X].items():
                    _, kap = _normalize_deformed(list(my) + list(mx), n)
                    for mono, gb_dict in kap.items():
                        add_kappa_result(list(mono), gb_dict, -sign * cy * cx)

            # Clean up zeros
            kappa_result = {
                k: {gb: c for gb, c in v.items() if c != 0}
                for k, v in kappa_result.items()
            }
            kappa_result = {k: v for k, v in kappa_result.items() if v}

            if not kappa_result:
                continue

            # Express kappa_result in the generator basis
            # For each gb parameter, collect the coefficient at each generator
            # gamma(X,Y) = sum_gb gb * [sum_Z gamma_{XYZ,gb} Z]
            # We express the oscillator element (for each gb value) in the basis
            gb_labels = get_all_gb_labels(n)

            # Restructure: for each gb, build an oscillator element
            gb_to_osc = {gb: {} for gb in gb_labels}
            for mono, gb_dict in kappa_result.items():
                for gb, c in gb_dict.items():
                    gb_to_osc[gb][mono] = gb_to_osc[gb].get(mono, Fraction(0)) + c

            gb_to_osc = {gb: {k: v for k, v in elem.items() if v != 0}
                         for gb, elem in gb_to_osc.items()}

            # Express each gb's oscillator contribution in the generator basis
            gb_gen_coeffs = {}
            for gb, osc_elem in gb_to_osc.items():
                if not osc_elem:
                    continue
                expressed = express_in_basis(osc_elem, gens, n)
                if expressed and any(v != 0 for v in expressed.values()):
                    gb_gen_coeffs[gb] = expressed

            if gb_gen_coeffs:
                gamma_entries.append({
                    "X": X,
                    "Y": Y,
                    "gamma_coeffs": {
                        gb: {Z: str(c) for Z, c in gen_coeffs.items()}
                        for gb, gen_coeffs in gb_gen_coeffs.items()
                    }
                })

    return gamma_entries


def build_schema2(n):
    """Build the complete Schema 2 JSON dict."""
    gb_labels = get_all_gb_labels(n)
    gamma_entries = compute_gamma(n)

    schema = {
        "schema_version": "5.0",
        "algebra_ref": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "description": "Inhomogeneous deformation of C(n+1) via gb matrix",
            "deformed_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "gb_matrix": {
                "size": f"2 x {2*n}",
                "description": f"{4*n} symbolic deformation parameters (parity 1)",
                "parameters": gb_labels
            },
            "gamma_coefficients": gamma_entries
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": str(date.today()),
            "n_gamma_entries": len(gamma_entries)
        }
    }
    return schema


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing gamma for C_{n}_gamma.json (n={n})...")
        schema = build_schema2(n)
        fname = f"data/C_{n}_gamma.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        entries = len(schema["inhomogeneous_deformation"]["gamma_coefficients"])
        gb_count = 4 * n
        print(f"  Done: {entries} non-zero gamma entries, {gb_count} gb parameters.")


if __name__ == "__main__":
    main()

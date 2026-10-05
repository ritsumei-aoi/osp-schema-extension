"""
C(n+1) = osp(2|2n) Schema 2: Gamma structure (inhomogeneous deformation).

Computes gamma coefficients γ_{abc} arising from the deformed oscillator relations:
  [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ
"""

import json
import os
from fractions import Fraction
from C_generators import (build_basis, get_realization, get_parity,
                          osc_parity, normal_order, express_in_basis)


def build_gb_parameters(n):
    """Build the 4n deformation parameters for C(n+1)."""
    params = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                label = f"gb_a1{sigma}_b{j}{s}"
                params.append({
                    "label": label,
                    "fermionic": f"a_1_{sigma}",
                    "bosonic": f"b_{j}_{s}",
                    "parity": 1
                })
    return params


def compute_deformed_product(word_X, word_Y, n, symbolic=True):
    """Compute X·Y in the deformed oscillator algebra.

    The deformation modifies the mixed commutator:
      [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ  (was 0 in homogeneous case)

    Since κ² = 0, terms with two or more κ factors vanish.

    Returns: dict mapping (word_tuple, gb_monomial_tuple) -> Fraction coefficient
    where gb_monomial_tuple is () for undeformed terms or (gb_label,) for first-order.
    """
    word = list(word_X) + list(word_Y)
    return deformed_normal_order(word, n)


def deformed_normal_order(word, n):
    """Normal-order with deformed mixed commutators.

    Returns dict: {(word_tuple, gb_tuple): Fraction}
    gb_tuple is () for zeroth order and (gb_label,) for first order in κ.
    """
    osc_order = ["a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        osc_order.extend([f"b_{k}_p", f"b_{k}_m"])
    order_map = {o: i for i, o in enumerate(osc_order)}

    terms = {(tuple(word), ()): Fraction(1)}

    changed = True
    max_iter = 200
    iteration = 0
    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        new_terms = {}
        for (w, gb), c in terms.items():
            if c == 0:
                continue
            swapped = False
            for pos in range(len(w) - 1):
                o1, o2 = w[pos], w[pos + 1]
                if order_map.get(o1, 0) > order_map.get(o2, 0):
                    p1 = osc_parity(o1)
                    p2 = osc_parity(o2)
                    sign = (-1) ** (p1 * p2)

                    swapped_word = list(w)
                    swapped_word[pos] = o2
                    swapped_word[pos + 1] = o1
                    sw_key = (tuple(swapped_word), gb)
                    new_terms[sw_key] = new_terms.get(sw_key, Fraction(0)) + c * sign

                    contraction = get_undeformed_contraction(o1, o2, n)
                    if contraction != 0:
                        contracted = tuple(list(w[:pos]) + list(w[pos+2:]))
                        ck = (contracted, gb)
                        new_terms[ck] = new_terms.get(ck, Fraction(0)) + c * contraction

                    if len(gb) == 0:
                        gb_label = get_deformed_contraction(o1, o2)
                        if gb_label is not None:
                            contracted = tuple(list(w[:pos]) + list(w[pos+2:]))
                            dk = (contracted, (gb_label,))
                            new_terms[dk] = new_terms.get(dk, Fraction(0)) + c * Fraction(1)

                    swapped = True
                    changed = True
                    break
            if not swapped:
                new_terms[(w, gb)] = new_terms.get((w, gb), Fraction(0)) + c

        terms = {k: v for k, v in new_terms.items() if v != 0}

    cleaned = {}
    for (w, gb), c in terms.items():
        fermion_labels = [o for o in w if osc_parity(o) == 1]
        if len(fermion_labels) != len(set(fermion_labels)):
            continue
        cleaned[(w, gb)] = c

    return cleaned


def get_undeformed_contraction(o1, o2, n):
    if o1 == "a_1_m" and o2 == "a_1_p":
        return Fraction(1)
    for k in range(1, n + 1):
        if o1 == f"b_{k}_m" and o2 == f"b_{k}_p":
            return Fraction(1)
    return Fraction(0)


def get_deformed_contraction(o1, o2):
    """Returns gb label if swapping o1 past o2 produces a deformed contraction.

    The deformation: [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ
    When o1 = b_j_s is to the left and o2 = a_1_σ is to the right,
    swapping gives: b_j^s · a_1^σ = a_1^σ · b_j^s + [b_j^s, a_1^σ]
    = a_1^σ · b_j^s - gb_{σ,j,s} · κ

    The -gb factor is the deformed contraction.
    """
    if o1.startswith("b_") and o2.startswith("a_1_"):
        sigma = o2.split("_")[2]
        parts = o1.split("_")
        j = parts[1]
        s = parts[2]
        return f"gb_a1{sigma}_b{j}{s}"
    return None


def compute_gamma_coefficients(n):
    """Compute all γ_{X,Y,Z} coefficients for C(n+1).

    γ_{X,Y,Z} is the coefficient of Z in the deformation part of [X, Y}_γ.
    """
    even, odd = build_basis(n)
    all_gens = odd + even

    gamma_coefficients = []

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue

            real_X = get_realization(X, n)
            real_Y = get_realization(Y, n)
            pX = get_parity(X)
            pY = get_parity(Y)

            deformed_bracket = {}

            for cX, word_X in real_X:
                for cY, word_Y in real_Y:
                    parity_x_term = sum(osc_parity(o) for o in word_X) % 2
                    parity_y_term = sum(osc_parity(o) for o in word_Y) % 2
                    sign = (-1) ** (parity_x_term * parity_y_term)

                    xy = compute_deformed_product(word_X, word_Y, n)
                    yx = compute_deformed_product(word_Y, word_X, n)

                    for (w, gb), coeff in xy.items():
                        if len(gb) == 1:
                            key = (w, gb)
                            deformed_bracket[key] = deformed_bracket.get(key, Fraction(0)) + cX * cY * coeff
                    for (w, gb), coeff in yx.items():
                        if len(gb) == 1:
                            key = (w, gb)
                            deformed_bracket[key] = deformed_bracket.get(key, Fraction(0)) - cX * cY * coeff * sign

            deformed_bracket = {k: v for k, v in deformed_bracket.items() if v != 0}

            by_gb = {}
            for (w, gb), coeff in deformed_bracket.items():
                gb_label = gb[0]
                if gb_label not in by_gb:
                    by_gb[gb_label] = {}
                by_gb[gb_label][w] = by_gb[gb_label].get(w, Fraction(0)) + coeff

            for gb_label, osc_result in by_gb.items():
                osc_result = {k: v for k, v in osc_result.items() if v != 0}
                if not osc_result:
                    continue

                decomp = express_in_basis(osc_result, all_gens, n)
                for Z, coeff in decomp.items():
                    if coeff != 0:
                        gamma_coefficients.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "gb_param": gb_label,
                            "coeff": str(coeff),
                            "sign_rule": "graded"
                        })

    return gamma_coefficients


def build_schema2_json(n):
    even, odd = build_basis(n)
    gb_params = build_gb_parameters(n)
    gamma_coeffs = compute_gamma_coefficients(n)

    schema = {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})"
            }
        },
        "gb_matrix": {
            "size": f"2 x {2*n}",
            "total_parameters": 4 * n,
            "parameters": gb_params
        },
        "deformation_rule": {
            "description": "[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ",
            "kappa_parity": 1,
            "kappa_nilpotency": "κ² = 0"
        },
        "gamma_coefficients": gamma_coeffs,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-05",
            "layer": "Schema 2 (inhomogeneous deformation)"
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating Schema 2 for C({n+1}), n={n}...")
        schema = build_schema2_json(n)
        filename = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        gc = len(schema["gamma_coefficients"])
        print(f"  Written to {filename} ({gc} gamma coefficients)")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    generate_all(os.path.join(os.path.dirname(__file__), "..", "data"))

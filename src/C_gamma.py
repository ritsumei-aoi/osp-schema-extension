"""
C(n+1) = osp(2|2n) Schema 2: Gamma structure (inhomogeneous deformation).
Computes gamma coefficients from the gb matrix deformation parameters.

The deformation is: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
This modifies the bracket via: [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_basis, get_parity, oscillator_form, normal_order,
    extract_boson_index, extract_boson_sign, osc_parity,
    compute_number_to_cartan
)


def gb_label(sigma, j, s):
    """Generate gb parameter label. sigma in {p,m}, j integer, s in {p,m}."""
    return f"gb_a1{sigma}_b{j}{s}"


def all_gb_labels(n):
    """Return all 4n gb parameter labels."""
    labels = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                labels.append(gb_label(sigma, j, s))
    return labels


def compute_deformed_product(w1, w2, n):
    """Compute the product w1 * w2 using deformed oscillator relations.

    Standard relations:
      {a1p, a1m} = 1, {a1s, a1s} = 0
      [bkm, blp] = delta_kl
      [bi^s, a1^sigma] = 0

    Deformed relation:
      [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa  (modification)
      Equivalently: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa

    Returns dict: {(normal_ordered_word_tuple, gb_monomial_tuple): Fraction_coeff}
    where gb_monomial_tuple is a tuple of gb labels (empty for undeformed part).
    """
    pass


def compute_gamma_bracket(X, Y, n, osc_forms, parity_map):
    """Compute the gamma part of [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y).

    gamma(X, Y) is the first-order deformation contribution, linear in gb parameters.
    """
    fx = osc_forms[X]
    fy = osc_forms[Y]
    px = parity_map[X]
    py = parity_map[Y]

    gamma_terms = {}

    for cx, wx in fx:
        for cy, wy in fy:
            xy_gamma = deformed_normal_order_gamma(list(wx) + list(wy), n)
            for (word, gb_key), coeff in xy_gamma.items():
                key = (word, gb_key)
                gamma_terms[key] = gamma_terms.get(key, Fraction(0)) + cx * cy * coeff

            sign = (-1) ** (px * py)
            yx_gamma = deformed_normal_order_gamma(list(wy) + list(wx), n)
            for (word, gb_key), coeff in yx_gamma.items():
                key = (word, gb_key)
                gamma_terms[key] = gamma_terms.get(key, Fraction(0)) - sign * cx * cy * coeff

    gamma_terms = {k: v for k, v in gamma_terms.items() if v != 0}
    return gamma_terms


def deformed_normal_order_gamma(word, n):
    """Normal order with deformation, extracting first-order gamma contributions.

    Returns dict: {(normal_word_tuple, gb_label): coeff}
    Only the linear-in-gb terms are kept (the undeformed part is computed separately).
    """
    def osc_order(osc):
        if osc == "a1p":
            return 0
        if osc == "a1m":
            return 1
        if osc.startswith("b"):
            rest = osc[1:]
            k_str = ""
            i = 0
            while i < len(rest) and rest[i].isdigit():
                k_str += rest[i]
                i += 1
            k = int(k_str)
            s = rest[i:]
            return 2 + 2 * (k - 1) + (0 if s == "p" else 1)
        raise ValueError(f"Unknown oscillator: {osc}")

    results = [(Fraction(1), list(word), None)]
    gamma_results = {}
    changed = True
    max_iter = 200
    iteration = 0

    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        new_results = []
        for coeff, w, gb in results:
            if gb is not None:
                word_key = tuple(w)
                key = (word_key, gb)
                gamma_results[key] = gamma_results.get(key, Fraction(0)) + coeff
                continue

            has_adj_ident_ferm = False
            for i in range(len(w) - 1):
                if w[i] == w[i + 1] and osc_parity(w[i]) == 1:
                    has_adj_ident_ferm = True
                    break
            if has_adj_ident_ferm:
                changed = True
                continue

            swapped = False
            for i in range(len(w) - 1):
                if osc_order(w[i]) > osc_order(w[i + 1]):
                    a, b = w[i], w[i + 1]
                    pa = osc_parity(a)
                    pb = osc_parity(b)

                    swapped_word = w[:i] + [b, a] + w[i + 2:]
                    sign_val = (-1) ** (pa * pb)
                    new_results.append((coeff * sign_val, swapped_word, None))

                    from C_generators import get_commutator
                    comm = get_commutator(a, b)
                    if comm != 0:
                        contracted = w[:i] + w[i + 2:]
                        new_results.append((coeff * comm, contracted, None))

                    if a.startswith("b") and b.startswith("a"):
                        j = extract_boson_index(a)
                        s = extract_boson_sign(a)
                        sigma = "p" if b == "a1p" else "m"
                        gb_key = gb_label(sigma, j, s)
                        gamma_word = w[:i] + w[i + 2:]
                        new_results.append((coeff * Fraction(-1), gamma_word, gb_key))

                    swapped = True
                    changed = True
                    break
            if not swapped:
                new_results.append((coeff, w, None))

        next_results = []
        for c, w, gb in new_results:
            if gb is not None:
                no_word = normal_order_standard(w, n)
                for c2, w2 in no_word:
                    key = (tuple(w2), gb)
                    gamma_results[key] = gamma_results.get(key, Fraction(0)) + c * c2
            else:
                next_results.append((c, w, gb))

        combined = {}
        for c, w, gb in next_results:
            key = (tuple(w), gb)
            combined[key] = combined.get(key, Fraction(0)) + c
        results = [(c, list(w), gb) for (w, gb), c in combined.items() if c != 0]

    gamma_results = {k: v for k, v in gamma_results.items() if v != 0}
    return gamma_results


def normal_order_standard(word, n):
    """Standard normal ordering (no deformation). Wrapper around C_generators."""
    return normal_order(word, n)


def express_gamma_in_basis(gamma_terms, n, parity_map):
    """Express gamma terms (oscillator words with gb labels) in the generator basis."""
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis

    osc_to_gen = {}
    for g in all_basis:
        if g.startswith("H_"):
            continue
        form = oscillator_form(g, n)
        if len(form) == 1:
            c, w = form[0]
            osc_to_gen[w] = (g, Fraction(1) / c)

    nop_map = compute_number_to_cartan(n)

    result = {}

    for (word, gb_key), coeff in gamma_terms.items():
        if len(word) == 0:
            continue

        gen_coeffs = {}
        if word in osc_to_gen:
            gen, scale = osc_to_gen[word]
            gen_coeffs[gen] = coeff * scale
        elif len(word) == 2:
            a, b = word
            if a == "a1p" and b == "a1m":
                for hk, hc in nop_map["f"].items():
                    if hk == "scalar":
                        continue
                    gen_coeffs[hk] = gen_coeffs.get(hk, Fraction(0)) + coeff * hc
            elif a.startswith("b") and b.startswith("b"):
                ka = extract_boson_index(a)
                sa = extract_boson_sign(a)
                kb = extract_boson_index(b)
                sb = extract_boson_sign(b)
                if ka == kb and sa == "p" and sb == "m":
                    nop_key = f"b{ka}"
                    for hk, hc in nop_map[nop_key].items():
                        if hk == "scalar":
                            continue
                        gen_coeffs[hk] = gen_coeffs.get(hk, Fraction(0)) + coeff * hc
                elif word in osc_to_gen:
                    gen, scale = osc_to_gen[word]
                    gen_coeffs[gen] = coeff * scale
            elif word in osc_to_gen:
                gen, scale = osc_to_gen[word]
                gen_coeffs[gen] = coeff * scale
        elif len(word) == 1:
            pass
        else:
            continue

        for gen, gc in gen_coeffs.items():
            if gc != 0:
                key = (gen, gb_key)
                result[key] = result.get(key, Fraction(0)) + gc

    result = {k: v for k, v in result.items() if v != 0}
    return result


def generate_gamma_json(n):
    """Generate Schema 2 (gamma structure) JSON for C(n+1)."""
    structure_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", f"C_{n}_structure.json"
    )
    with open(structure_file) as f:
        structure = json.load(f)

    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    parity_map = {g: get_parity(g) for g in all_basis}

    osc_forms = {}
    for g in all_basis:
        osc_forms[g] = oscillator_form(g, n)

    gb_labels = all_gb_labels(n)
    gb_matrix_params = {}
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                key = gb_label(sigma, j, s)
                gb_matrix_params[key] = f"gb_{{a_1^{'+' if sigma == 'p' else '-'}, b_{j}^{'+' if s == 'p' else '-'}}}"

    gamma_coefficients = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue

            gamma_raw = compute_gamma_bracket(X, Y, n, osc_forms, parity_map)
            if not gamma_raw:
                continue

            gamma_basis = express_gamma_in_basis(gamma_raw, n, parity_map)

            for (Z, gb_key), coeff in sorted(gamma_basis.items(), key=lambda x: x[0]):
                if coeff != 0:
                    gamma_coefficients.append({
                        "X": X,
                        "Y": Y,
                        "gamma_Z": Z,
                        "gb_param": gb_key,
                        "coeff": str(coeff)
                    })

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n

    schema = {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "gb_matrix": {
            "size": [2, 2 * n],
            "total_parameters": 4 * n,
            "fermion_labels": ["a_1_p", "a_1_m"],
            "boson_labels": boson_labels,
            "parameters": gb_matrix_params,
            "deformation_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
        },
        "gamma_coefficients": gamma_coefficients,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": str(date.today()),
            "schema_layer": 2,
            "description": "Inhomogeneous deformation gamma structure for C(n+1)",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def verify_consistency(n):
    """Verify that gamma coefficients are consistent with Schema 1."""
    structure_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", f"C_{n}_structure.json"
    )
    gamma_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", f"C_{n}_gamma.json"
    )
    with open(structure_file) as f:
        structure = json.load(f)
    with open(gamma_file) as f:
        gamma = json.load(f)

    s1_basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    errors = []
    for gc in gamma["gamma_coefficients"]:
        if gc["X"] not in s1_basis:
            errors.append(f"Unknown X: {gc['X']}")
        if gc["Y"] not in s1_basis:
            errors.append(f"Unknown Y: {gc['Y']}")
        if gc["gamma_Z"] not in s1_basis:
            errors.append(f"Unknown gamma_Z: {gc['gamma_Z']}")

    return errors


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) gamma structure (n={n})...")
        schema = generate_gamma_json(n)
        filename = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        gc_count = len(schema["gamma_coefficients"])
        print(f"  Written {filename}: {gc_count} gamma coefficients")
        print(f"  gb matrix: {schema['gb_matrix']['total_parameters']} parameters")

        errors = verify_consistency(n)
        if errors:
            print(f"  CONSISTENCY ERRORS: {errors}")
        else:
            print(f"  Consistency check: PASS")

    print("Done.")


if __name__ == "__main__":
    main()

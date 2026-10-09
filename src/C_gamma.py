"""
Schema 2 (gamma structure) generator for C(n+1) = osp(2|2n).

The deformation modifies mixed boson-fermion commutators:
  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa

Gamma coefficients are computed by tracking gb contractions during
normal ordering of oscillator products.
"""

import json
import os
import datetime
from fractions import Fraction
import sys

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_basis, get_parity, get_realization, build_inverse_map,
    decompose_via_inverse, osc_parity, is_creation, osc_index, osc_type
)


def gb_label(fermion_osc, boson_osc):
    f = "a1p" if fermion_osc == "a_1_p" else "a1m"
    j = boson_osc.split("_")[1]
    b_sign = "p" if boson_osc.endswith("_p") else "m"
    return f"gb_{f}_b{j}{b_sign}"


def build_gb_parameters(n):
    params = []
    for f_sign in ["p", "m"]:
        for j in range(1, n + 1):
            for b_sign in ["p", "m"]:
                params.append({
                    "label": gb_label(f"a_1_{f_sign}", f"b_{j}_{b_sign}"),
                    "fermion": f"a_1_{f_sign}",
                    "boson": f"b_{j}_{b_sign}",
                })
    return params


def _needs_swap(a, b):
    """Same swap logic as C_generators._needs_swap."""
    pa, pb = osc_parity(a), osc_parity(b)
    ta, tb = osc_type(a), osc_type(b)

    if ta == "b" and tb == "a":
        return True
    if ta == "a" and tb == "a":
        if is_creation(b) and not is_creation(a):
            return True
        return False
    if ta == "b" and tb == "b":
        ia, ib = osc_index(a), osc_index(b)
        if ia > ib:
            return True
        if ia == ib:
            if is_creation(b) and not is_creation(a):
                return True
        return False
    return False


def _fermion_contraction(a, b):
    if osc_type(a) == "a" and osc_type(b) == "a":
        if not is_creation(a) and is_creation(b):
            return Fraction(1)
    return Fraction(0)


def _boson_contraction(a, b):
    if osc_type(a) == "b" and osc_type(b) == "b":
        if osc_index(a) == osc_index(b):
            if not is_creation(a) and is_creation(b):
                return Fraction(1)
    return Fraction(0)


def normal_order_with_gb(word, coeff, result):
    """Normal-order a word, tracking gb contractions.

    result: dict mapping gb_label -> dict(word_tuple -> Fraction)

    When a boson b_j^s is swapped past a fermion a_1^sigma during normal
    ordering, the deformation produces a contraction: -gb * kappa * (remaining word).
    We record these gb corrections and normal-order the remaining words.
    """
    if coeff == 0:
        return

    for i in range(len(word) - 1):
        a, b = word[i], word[i + 1]

        if _needs_swap(a, b):
            swapped = word[:i] + [b, a] + word[i + 2:]
            pa, pb = osc_parity(a), osc_parity(b)

            if pa == 1 and pb == 1:
                swap_sign = Fraction(-1)
                contraction = _fermion_contraction(a, b)
            elif pa == 0 and pb == 0:
                swap_sign = Fraction(1)
                contraction = _boson_contraction(a, b)
            else:
                swap_sign = Fraction(1)
                contraction = Fraction(0)

                gb = _get_gb_label(a, b)
                if gb is not None:
                    remaining = word[:i] + word[i + 2:]
                    _collect_normal_ordered(remaining, -coeff, gb, result)

            normal_order_with_gb(swapped, coeff * swap_sign, result)

            if contraction != 0:
                contracted = word[:i] + word[i + 2:]
                normal_order_with_gb(contracted, coeff * contraction, result)
            return

    pass


def _get_gb_label(a, b):
    """Get gb label for a boson-fermion swap. a is before b in the word."""
    ta, tb = osc_type(a), osc_type(b)
    if ta == "b" and tb == "a":
        return gb_label(b, a)
    if ta == "a" and tb == "b":
        return gb_label(a, b)
    return None


def _collect_normal_ordered(word, coeff, gb_key, result):
    """Normal-order the remaining word (using undeformed relations) and add to result."""
    from C_generators import _normal_order as undeformed_normal_order

    ordered = {}
    undeformed_normal_order(list(word), coeff, ordered)

    if gb_key not in result:
        result[gb_key] = {}
    for w, c in ordered.items():
        if c != 0:
            result[gb_key][w] = result[gb_key].get(w, Fraction(0)) + c


def compute_gamma_bracket(label_x, label_y, n):
    """Compute gamma(X, Y): the kappa-linear deformation correction to [X, Y]."""
    px = get_parity(label_x)
    py = get_parity(label_y)
    sign = (-1) ** (px * py)

    real_x = get_realization(label_x, n)
    real_y = get_realization(label_y, n)

    gb_corrections = {}

    for cx, wx in real_x:
        for cy, wy in real_y:
            product_word = list(wx) + list(wy)
            normal_order_with_gb(product_word, cx * cy, gb_corrections)

    for cx, wx in real_y:
        for cy, wy in real_x:
            product_word = list(wx) + list(wy)
            normal_order_with_gb(product_word, -sign * cx * cy, gb_corrections)

    cleaned = {}
    for gb, word_dict in gb_corrections.items():
        c = {w: v for w, v in word_dict.items() if v != 0}
        if c:
            cleaned[gb] = c

    return cleaned


def compute_all_gamma(n):
    """Compute all gamma coefficients for C(n+1)."""
    even, odd = build_basis(n)
    all_labels = odd + even
    inv_map = build_inverse_map(n, all_labels)

    gamma_list = []

    for i, x in enumerate(all_labels):
        for j, y in enumerate(all_labels):
            if j <= i:
                continue

            raw = compute_gamma_bracket(x, y, n)
            if not raw:
                continue

            for gb_param, word_dict in sorted(raw.items()):
                basis_coeffs = decompose_via_inverse(word_dict, inv_map, n=n)
                if not basis_coeffs:
                    continue

                result_list = []
                for z, c in sorted(basis_coeffs.items()):
                    result_list.append({"Z": z, "coeff": str(c)})

                gamma_list.append({
                    "X": x,
                    "Y": y,
                    "gb_parameter": gb_param,
                    "result": result_list,
                    "type": "deformation"
                })

    return gamma_list


def generate_schema2_json(n):
    even, odd = build_basis(n)
    gb_params = build_gb_parameters(n)
    gamma_coefficients = compute_all_gamma(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "gb_matrix": {
            "description": f"Deformation parameters for C({n + 1}) inhomogeneous deformation",
            "size": f"2 x {2 * n}",
            "total_parameters": 4 * n,
            "parity": 1,
            "parameters": gb_params
        },
        "gamma_coefficients": gamma_coefficients,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) gamma structure (n={n})...")
        schema = generate_schema2_json(n)
        filename = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        gc = len(schema["gamma_coefficients"])
        print(f"  -> {filename}: {gc} gamma entries, "
              f"{schema['gb_matrix']['total_parameters']} gb parameters")


if __name__ == "__main__":
    main()

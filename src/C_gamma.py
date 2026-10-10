"""
C(n+1) = osp(2|2n) inhomogeneous deformation (gamma structure) generator.

Computes the gamma coefficients arising from the deformed commutation relations:
  [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ

where gb parameters are symbolic deformation parameters of parity 1.

Outputs Schema 2 JSON files for n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import build_basis, get_parity, get_realization, express_in_basis


def gb_label(fermion_sign, boson_idx, boson_sign):
    return f"gb_a1{fermion_sign}_b{boson_idx}_{boson_sign}"


def get_gb_parameters(n):
    params = []
    for k in range(1, n + 1):
        for fs in ["p", "m"]:
            for bs in ["p", "m"]:
                params.append({
                    "label": gb_label(fs, k, bs),
                    "fermion": f"a_1_{fs}",
                    "boson": f"b_{k}_{bs}"
                })
    return params


def compute_deformed_product(w1, w2, n):
    """Compute the product of two oscillator words using DEFORMED relations.

    The deformation modifies: [b_j^s, a_1^σ] = -gb_{σ,j,s} · κ
    (i.e., b_j^s · a_1^σ = a_1^σ · b_j^s - gb_{σ,j,s} · κ)

    Returns:
      - standard_terms: list of (Fraction, word) for the undeformed part
      - gb_terms: list of (gb_label, Fraction, word) for the κ-proportional part
    """
    if not w1 or not w2:
        return [(Fraction(1), w1 + w2)], []

    full_word = w1 + w2
    standard_terms = [(Fraction(1), full_word)]
    gb_terms = []

    standard_terms, gb_terms = _deformed_normal_order(standard_terms, gb_terms, n)
    return standard_terms, gb_terms


def _deformed_normal_order(standard_terms, gb_terms, n):
    from C_generators import _should_swap, _anticommutator, _commutator, osc_parity

    changed = True
    while changed:
        changed = False
        new_standard = []
        new_gb = gb_terms[:]

        for coeff, word in standard_terms:
            if coeff == 0:
                continue
            swapped = False
            for pos in range(len(word) - 1):
                a, b = word[pos], word[pos + 1]
                if _should_swap(a, b):
                    swapped = True
                    pa = osc_parity(a)
                    pb = osc_parity(b)
                    new_word = word[:pos] + (b, a) + word[pos + 2:]

                    is_boson_fermion = (a.startswith("b_") and b.startswith("a_"))

                    if pa == 1 and pb == 1:
                        new_standard.append((-coeff, new_word))
                        contraction = _anticommutator(a, b)
                        if contraction != 0:
                            contracted_word = word[:pos] + word[pos + 2:]
                            new_standard.append((coeff * contraction, contracted_word))
                    else:
                        new_standard.append((coeff, new_word))
                        contraction = _commutator(a, b)
                        if contraction != 0:
                            contracted_word = word[:pos] + word[pos + 2:]
                            new_standard.append((coeff * contraction, contracted_word))

                    if is_boson_fermion:
                        a_parts = a.split("_")
                        b_parts = b.split("_")
                        boson_idx = int(a_parts[1])
                        boson_sign = a_parts[2]
                        fermion_sign = b_parts[2]
                        gb_lab = gb_label(fermion_sign, boson_idx, boson_sign)
                        contracted_word = word[:pos] + word[pos + 2:]
                        new_gb.append((gb_lab, -coeff, contracted_word))

                    changed = True
                    break
            if not swapped:
                new_standard.append((coeff, word))

        standard_terms = new_standard
        gb_terms = new_gb

    combined_std = {}
    for c, w in standard_terms:
        combined_std[w] = combined_std.get(w, Fraction(0)) + c
    standard_terms = [(c, w) for w, c in combined_std.items() if c != 0]

    combined_gb = {}
    for gb, c, w in gb_terms:
        key = (gb, w)
        combined_gb[key] = combined_gb.get(key, Fraction(0)) + c
    gb_terms = [(gb, c, w) for (gb, w), c in combined_gb.items() if c != 0]

    return standard_terms, gb_terms


def compute_gamma_bracket(gen_x, gen_y, n):
    """Compute the gamma (kappa-proportional) part of the deformed bracket [X, Y}.

    Returns list of (gb_label, gen_Z, coeff) triples representing:
      [X, Y]_γ = Σ gb_label * coeff * gen_Z * κ
    """
    real_x = get_realization(gen_x, n)
    real_y = get_realization(gen_y, n)
    px = get_parity(gen_x)
    py = get_parity(gen_y)

    xy_gb = _multiply_deformed(real_x, real_y, n)
    yx_gb = _multiply_deformed(real_y, real_x, n)

    if px == 1 and py == 1:
        all_gb = xy_gb + yx_gb
    else:
        sign = (-1) ** (px * py)
        all_gb = xy_gb[:]
        for gb, c, w in yx_gb:
            all_gb.append((gb, -Fraction(sign) * c, w))

    combined = {}
    for gb, c, w in all_gb:
        key = (gb, w)
        combined[key] = combined.get(key, Fraction(0)) + c
    all_gb = [(gb, c, w) for (gb, w), c in combined.items() if c != 0]

    result = []
    for gb, c, w in all_gb:
        gen_result = express_in_basis([(c, w)], n)
        for gen_z, gen_c in gen_result.items():
            result.append((gb, gen_z, gen_c))

    combined_result = {}
    for gb, z, c in result:
        key = (gb, z)
        combined_result[key] = combined_result.get(key, Fraction(0)) + c
    return [(gb, z, c) for (gb, z), c in combined_result.items() if c != 0]


def _multiply_deformed(real_a, real_b, n):
    """Multiply two realizations and collect only the gb (kappa) terms."""
    gb_results = []
    for ca, wa in real_a:
        for cb, wb in real_b:
            _, gb_terms = compute_deformed_product(wa, wb, n)
            for gb, cp, wp in gb_terms:
                gb_results.append((gb, ca * cb * cp, wp))

    combined = {}
    for gb, c, w in gb_results:
        key = (gb, w)
        combined[key] = combined.get(key, Fraction(0)) + c
    return [(gb, c, w) for (gb, w), c in combined.items() if c != 0]


def compute_all_gamma(n):
    """Compute all gamma coefficients for C(n+1)."""
    even, odd = build_basis(n)
    all_gens = odd + even

    gamma_coefficients = []

    for i, x in enumerate(all_gens):
        for j, y in enumerate(all_gens):
            if j <= i:
                continue

            gamma_terms = compute_gamma_bracket(x, y, n)
            if not gamma_terms:
                continue

            gb_grouped = {}
            for gb, z, c in gamma_terms:
                if gb not in gb_grouped:
                    gb_grouped[gb] = []
                gb_grouped[gb].append({"Z": z, "coeff": str(c)})

            result_list = []
            for gb in sorted(gb_grouped.keys()):
                for term in gb_grouped[gb]:
                    result_list.append({
                        "Z": term["Z"],
                        "coeff": term["coeff"],
                        "gb_param": gb
                    })

            gamma_coefficients.append({
                "X": x,
                "Y": y,
                "result": result_list
            })

    return gamma_coefficients


def generate_schema2(n):
    """Generate Schema 2 JSON for C(n+1) with bosonic rank n."""
    gamma_coefficients = compute_all_gamma(n)
    gb_params = get_gb_parameters(n)

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
                "osp": f"osp(2|{2 * n})"
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "gb_matrix": {
            "size": [2, 2 * n],
            "parameters": gb_params,
            "parity": 1,
            "total_count": 4 * n,
            "deformation_rule": "[b_j^s, a_1^σ] = -gb_{σ,j,s} · κ"
        },
        "gamma_coefficients": gamma_coefficients,
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": str(date.today()),
            "schema_version": "5.0",
            "description": "Inhomogeneous deformation (gamma structure) for C(n+1)"
        }
    }

    return schema


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) gamma structure (n={n})...")
        schema = generate_schema2(n)
        filename = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  gb parameters: {schema['gb_matrix']['total_count']}")
        print(f"  Gamma entries: {len(schema['gamma_coefficients'])}")


if __name__ == "__main__":
    main()

"""
Schema 3 (Evaluated Structure) generator for C(n+1) = osp(2|2n).

Substitutes concrete sign assignments into the symbolic gb parameters
from Schema 2 to produce numerical gamma coefficients.
"""

import json
import os
import datetime
from fractions import Fraction


def load_gamma(n, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    path = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(path) as f:
        return json.load(f)


def build_gb_assignment(n, profile="all_plus"):
    """Build a concrete gb assignment.

    Profiles:
    - "all_plus": all gb parameters = +1
    - "alternating": alternating +1, -1
    """
    params = []
    for f_sign in ["p", "m"]:
        for j in range(1, n + 1):
            for b_sign in ["p", "m"]:
                f = "a1p" if f_sign == "p" else "a1m"
                b = f"b{j}{b_sign}"
                params.append(f"gb_{f}_{b}")

    assignment = {}
    if profile == "all_plus":
        for p in params:
            assignment[p] = 1
    elif profile == "alternating":
        for i, p in enumerate(params):
            assignment[p] = 1 if i % 2 == 0 else -1
    else:
        for p in params:
            assignment[p] = 1

    return assignment


def evaluate_gamma(gamma_data, gb_assignment):
    """Substitute gb values into symbolic gamma coefficients."""
    evaluated = []

    pair_results = {}

    for entry in gamma_data["gamma_coefficients"]:
        x = entry["X"]
        y = entry["Y"]
        gb_param = entry["gb_parameter"]
        gb_val = gb_assignment.get(gb_param, 0)

        if gb_val == 0:
            continue

        key = (x, y)
        if key not in pair_results:
            pair_results[key] = {}

        for term in entry["result"]:
            z = term["Z"]
            coeff = Fraction(term["coeff"])
            numerical = coeff * gb_val
            pair_results[key][z] = pair_results[key].get(z, Fraction(0)) + numerical

    for (x, y), result_dict in sorted(pair_results.items()):
        cleaned = {z: c for z, c in result_dict.items() if c != 0}
        if not cleaned:
            continue

        result_list = []
        for z, c in sorted(cleaned.items()):
            result_list.append({
                "Z": z,
                "coeff": str(c)
            })

        evaluated.append({
            "X": x,
            "Y": y,
            "result": result_list,
            "type": "evaluated_deformation"
        })

    return evaluated


def generate_schema3_json(n, profile="all_plus"):
    gamma_data = load_gamma(n)
    gb_assignment = build_gb_assignment(n, profile)
    evaluated = evaluate_gamma(gamma_data, gb_assignment)

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
        "gb_assignment": {k: v for k, v in sorted(gb_assignment.items())},
        "gb_profile": profile,
        "evaluated_gamma": evaluated,
        "metadata": {
            "generated_by": "C_evaluated.py",
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
        print(f"Generating C({n + 1}) evaluated structure (n={n})...")
        schema = generate_schema3_json(n, profile="all_plus")
        filename = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        ec = len(schema["evaluated_gamma"])
        print(f"  -> {filename}: {ec} evaluated entries (profile: all_plus)")


if __name__ == "__main__":
    main()

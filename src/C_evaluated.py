"""
C(n+1) = osp(2|2n) evaluated structure generator (Layer 3).

Substitutes concrete sign values (+1 or -1) for the gb deformation parameters
into the symbolic gamma coefficients from Schema 2.

Outputs Schema 3 JSON files for n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import get_gb_parameters


def default_gb_assignment(n):
    """All gb parameters set to +1."""
    params = get_gb_parameters(n)
    return {p["label"]: "+1" for p in params}


def evaluate_gamma(gamma_data, gb_assignment):
    """Substitute gb values into symbolic gamma coefficients."""
    evaluated = []

    for entry in gamma_data["gamma_coefficients"]:
        result_terms = {}

        for term in entry["result"]:
            gb_param = term["gb_param"]
            coeff = Fraction(term["coeff"])
            z = term["Z"]
            gb_val = Fraction(gb_assignment[gb_param])

            val = coeff * gb_val
            result_terms[z] = result_terms.get(z, Fraction(0)) + val

        result_list = []
        for z in sorted(result_terms.keys()):
            c = result_terms[z]
            if c != 0:
                result_list.append({
                    "Z": z,
                    "coeff": str(c)
                })

        if result_list:
            evaluated.append({
                "X": entry["X"],
                "Y": entry["Y"],
                "result": result_list
            })

    return evaluated


def generate_schema3(n, gb_assignment=None):
    """Generate Schema 3 JSON for C(n+1) with bosonic rank n."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")

    gamma_path = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(gamma_path) as f:
        gamma_data = json.load(f)

    if gb_assignment is None:
        gb_assignment = default_gb_assignment(n)

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
                "osp": f"osp(2|{2 * n})"
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "gb_assignment": gb_assignment,
        "evaluated_gamma_coefficients": evaluated,
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": str(date.today()),
            "schema_version": "5.0",
            "description": f"Evaluated gamma structure for C({n + 1}) with all gb=+1"
        }
    }

    return schema


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) evaluated structure (n={n})...")
        schema = generate_schema3(n)
        filename = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  Evaluated entries: {len(schema['evaluated_gamma_coefficients'])}")


if __name__ == "__main__":
    main()

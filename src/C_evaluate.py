"""
C(n+1) = osp(2|2n) Schema 3: Evaluated structure.
Substitutes concrete sign values into gb parameters to produce numerical gamma coefficients.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date


def define_gb_profiles(n):
    """Define representative gb parameter assignments.

    Profile 'all_plus': all gb parameters set to +1.
    """
    profiles = {}

    all_plus = {}
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                all_plus[f"gb_a1{sigma}_b{j}{s}"] = Fraction(1)
    profiles["all_plus"] = all_plus

    return profiles


def evaluate_gamma(gamma_data, gb_values):
    """Substitute gb parameter values into gamma coefficients.

    Returns list of evaluated gamma entries with numerical coefficients.
    """
    bracket_map = {}

    for gc in gamma_data["gamma_coefficients"]:
        X = gc["X"]
        Y = gc["Y"]
        Z = gc["gamma_Z"]
        gb_param = gc["gb_param"]
        coeff = Fraction(gc["coeff"])

        gb_val = gb_values.get(gb_param, Fraction(0))
        numerical_coeff = coeff * gb_val

        if numerical_coeff != 0:
            key = (X, Y, Z)
            bracket_map[key] = bracket_map.get(key, Fraction(0)) + numerical_coeff

    results = []
    for (X, Y, Z), coeff in sorted(bracket_map.items()):
        if coeff != 0:
            results.append({
                "X": X,
                "Y": Y,
                "gamma_Z": Z,
                "coeff": str(coeff)
            })

    return results


def generate_evaluated_json(n, profile_name="all_plus"):
    """Generate Schema 3 (evaluated structure) JSON for C(n+1)."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    gamma_file = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(gamma_file) as f:
        gamma_data = json.load(f)

    structure_file = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(structure_file) as f:
        structure_data = json.load(f)

    profiles = define_gb_profiles(n)
    gb_values = profiles[profile_name]

    evaluated = evaluate_gamma(gamma_data, gb_values)

    gb_assignment = {k: str(v) for k, v in gb_values.items()}

    schema = {
        "schema_version": "5.0",
        "algebra": structure_data["algebra"],
        "gb_profile": {
            "name": profile_name,
            "assignment": gb_assignment
        },
        "evaluated_gamma_coefficients": evaluated,
        "structure_constants_undeformed": structure_data["structure_constants"],
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": str(date.today()),
            "schema_layer": 3,
            "description": f"Evaluated gamma structure for C({n+1}) with profile '{profile_name}'",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def verify_consistency_with_schema2(n, profile_name="all_plus"):
    """Verify that evaluated coefficients are consistent with Schema 2."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    gamma_file = os.path.join(data_dir, f"C_{n}_gamma.json")
    with open(gamma_file) as f:
        gamma_data = json.load(f)

    eval_file = os.path.join(data_dir, f"C_{n}_evaluated.json")
    with open(eval_file) as f:
        eval_data = json.load(f)

    profiles = define_gb_profiles(n)
    gb_values = profiles[profile_name]
    expected = evaluate_gamma(gamma_data, gb_values)

    actual = eval_data["evaluated_gamma_coefficients"]

    if len(expected) != len(actual):
        return [f"Count mismatch: expected {len(expected)}, got {len(actual)}"]

    errors = []
    for i, (exp, act) in enumerate(zip(expected, actual)):
        if exp != act:
            errors.append(f"Entry {i}: expected {exp}, got {act}")

    return errors


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Evaluating C({n + 1}) gamma structure (n={n})...")
        schema = generate_evaluated_json(n, "all_plus")
        filename = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        gc_count = len(schema["evaluated_gamma_coefficients"])
        print(f"  Written {filename}: {gc_count} evaluated gamma coefficients")

        errors = verify_consistency_with_schema2(n)
        if errors:
            print(f"  CONSISTENCY ERRORS: {errors[:5]}")
        else:
            print(f"  Consistency with Schema 2: PASS")

    print("Done.")


if __name__ == "__main__":
    main()

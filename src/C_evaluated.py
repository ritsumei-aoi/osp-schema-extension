"""
C(n+1) Schema 3: Evaluated structure constants with concrete gb assignments.

Substitutes specific sign profiles into the symbolic gamma coefficients
to produce numerically evaluated deformation structure constants.
"""

import json
import os
from fractions import Fraction


def load_schema1(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        return json.load(f)


def load_schema2(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        return json.load(f)


def get_default_gb_assignment(n):
    """All gb parameters set to +1."""
    assignment = {}
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                label = f"gb_a1{sigma}_b{j}{s}"
                assignment[label] = Fraction(1)
    return assignment


def evaluate_gamma(schema2, gb_assignment):
    """Substitute gb values into symbolic gamma coefficients.

    Returns list of evaluated structure constants (with numerical coefficients).
    """
    evaluated = {}
    for gc in schema2["gamma_coefficients"]:
        X, Y, Z = gc["X"], gc["Y"], gc["Z"]
        gb_param = gc["gb_param"]
        coeff = Fraction(gc["coeff"])

        gb_val = gb_assignment.get(gb_param, Fraction(0))
        numerical = coeff * gb_val

        if numerical != 0:
            key = (X, Y, Z)
            evaluated[key] = evaluated.get(key, Fraction(0)) + numerical

    result = []
    for (X, Y, Z), coeff in evaluated.items():
        if coeff != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(coeff),
                "sign_rule": "graded"
            })
    return result


def build_total_structure(schema1, evaluated_gamma):
    """Combine Schema 1 (homogeneous) + evaluated gamma (deformation) into total."""
    total = {}
    for sc in schema1["structure_constants"]:
        key = (sc["X"], sc["Y"], sc["Z"])
        total[key] = total.get(key, Fraction(0)) + Fraction(sc["coeff"])

    for eg in evaluated_gamma:
        key = (eg["X"], eg["Y"], eg["Z"])
        total[key] = total.get(key, Fraction(0)) + Fraction(eg["coeff"])

    result = []
    for (X, Y, Z), coeff in total.items():
        if coeff != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(coeff),
                "sign_rule": "graded"
            })
    return result


def build_schema3_json(n, data_dir="data"):
    schema1 = load_schema1(n, data_dir)
    schema2 = load_schema2(n, data_dir)
    gb_assignment = get_default_gb_assignment(n)
    evaluated_gamma = evaluate_gamma(schema2, gb_assignment)
    total = build_total_structure(schema1, evaluated_gamma)

    gb_assignment_str = {k: str(v) for k, v in gb_assignment.items()}

    schema = {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": schema1["algebra"],
        "gb_assignment": gb_assignment_str,
        "homogeneous_structure_constants": schema1["structure_constants"],
        "evaluated_gamma_coefficients": evaluated_gamma,
        "homogeneous_count": len(schema1["structure_constants"]),
        "deformation_count": len(evaluated_gamma),
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": "2026-10-05",
            "gb_profile": "all_plus_one",
            "layer": "Schema 3 (evaluated structure)"
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating Schema 3 for C({n+1}), n={n}...")
        schema = build_schema3_json(n, output_dir)
        filename = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  Homogeneous: {schema['homogeneous_count']}, "
              f"Deformation: {schema['deformation_count']}")


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    generate_all(data_dir)

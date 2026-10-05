"""
C(n+1) = osp(2|2n) Layer 3: Evaluated structure.

Substitutes concrete sign values into the gb parameters and produces
evaluated structure constants (Schema 1 + kappa*gamma contributions).
"""

import json
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, __import__('os').path.dirname(__file__))
from C_gamma import build_gb_params


def generate_gb_assignment(n, profile="all_plus"):
    """Generate a concrete gb assignment.
    profile='all_plus': all gb parameters set to +1."""
    params = build_gb_params(n)
    if profile == "all_plus":
        return {p: Fraction(1) for p in params}
    elif profile == "alternating":
        assignment = {}
        for i, p in enumerate(params):
            assignment[p] = Fraction(1) if i % 2 == 0 else Fraction(-1)
        return assignment
    raise ValueError(f"Unknown profile: {profile}")


def evaluate_gamma(gamma_data, gb_assignment):
    """Substitute gb values into gamma coefficients, producing evaluated
    kappa-corrections to the structure constants."""
    evaluated = {}
    for entry in gamma_data["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        param = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        gb_val = gb_assignment.get(param, Fraction(0))

        key = (X, Y, Z)
        evaluated[key] = evaluated.get(key, Fraction(0)) + coeff * gb_val

    result = []
    for (X, Y, Z), coeff in evaluated.items():
        if coeff != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(coeff),
                "sign_rule": "graded",
                "origin": "kappa_deformation",
            })
    return result


def generate_schema3(n, profile="all_plus"):
    with open(f"data/C_{n}_structure.json") as f:
        structure_data = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)

    gb_assignment = generate_gb_assignment(n, profile)

    base_sc = []
    for sc in structure_data["structure_constants"]:
        base_sc.append({
            "X": sc["X"], "Y": sc["Y"], "Z": sc["Z"],
            "coeff": sc["coeff"],
            "sign_rule": "graded",
            "origin": "undeformed",
        })

    kappa_sc = evaluate_gamma(gamma_data, gb_assignment)

    schema3 = {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": structure_data["algebra"],
        "gb_assignment": {
            "profile": profile,
            "values": {k: str(v) for k, v in gb_assignment.items()},
        },
        "structure_constants_undeformed": base_sc,
        "structure_constants_kappa": kappa_sc,
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": str(date.today()),
            "source_schema1": f"C_{n}_structure.json",
            "source_schema2": f"C_{n}_gamma.json",
        },
    }
    return schema3


def main():
    for n in [1, 2, 3]:
        print(f"Generating Schema 3 for C({n+1}) = osp(2|{2*n}) [n={n}]...")
        schema3 = generate_schema3(n, "all_plus")
        filename = f"data/C_{n}_evaluated.json"
        with open(filename, "w") as f:
            json.dump(schema3, f, indent=2)
        n_base = len(schema3["structure_constants_undeformed"])
        n_kappa = len(schema3["structure_constants_kappa"])
        print(f"  -> {filename}: {n_base} base + {n_kappa} kappa terms")
    print("Done.")


if __name__ == "__main__":
    main()

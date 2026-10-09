"""
C_evaluate.py: Schema 3 - Evaluate the gamma structure for specific gb assignments.

Takes Schema 2 (symbolic gamma) and substitutes concrete values for gb parameters.
Produces C_{n}_evaluated.json with numeric gamma coefficients.

Representative gb assignment: all gb = +1 (canonical sign profile).
"""

import json
import sys
import os
from fractions import Fraction
from datetime import date
sys.path.insert(0, os.path.dirname(__file__))
from C_gamma import build_schema2


def evaluate_gamma(schema2, gb_values):
    """
    Substitute gb_values into the symbolic gamma coefficients.
    gb_values: dict {gb_label: value}
    Returns list of {X, Y, Z, coeff} with numeric coefficients.
    """
    # Accumulate over all (X,Y,Z) combinations
    accumulated = {}
    for entry in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb_sym = entry["gb_param"]
        sym_coeff = Fraction(entry["coeff"])
        gb_val = Fraction(gb_values.get(gb_sym, 0))
        numeric_coeff = sym_coeff * gb_val
        if numeric_coeff == 0:
            continue
        key = (X, Y, Z)
        accumulated[key] = accumulated.get(key, Fraction(0)) + numeric_coeff

    result = []
    for (X, Y, Z), coeff in accumulated.items():
        if coeff != 0:
            result.append({"X": X, "Y": Y, "Z": Z, "coeff": str(coeff)})
    return result


def build_schema3(n, gb_values=None):
    """Build Schema 3 JSON for C_{n} with given gb values (default: all +1)."""
    schema2 = build_schema2(n)

    if gb_values is None:
        # Default: all gb = +1
        gb_values = {lbl: 1 for lbl in schema2["gb_matrix"]["labels"]}

    evaluated_gamma = evaluate_gamma(schema2, gb_values)

    schema = {
        "schema_version": "5.0",
        "algebra": schema2["algebra"],
        "gb_assignment": gb_values,
        "evaluated_gamma": {
            "description": "Numerically evaluated gamma coefficients: gamma(X,Y) = sum_Z coeff * Z",
            "entries": evaluated_gamma
        },
        "consistency": {
            "schema2_gamma_entries": len(schema2["inhomogeneous_deformation"]["gamma_coefficients"]),
            "evaluated_entries": len(evaluated_gamma),
            "gb_all_nonzero": all(v != 0 for v in gb_values.values())
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": str(date.today()),
            "gb_assignment_description": "All gb = +1 (canonical all-plus profile)"
        }
    }
    return schema


def verify_consistency_schema2(n, schema3, schema2):
    """Check that all Z in evaluated_gamma are valid generators."""
    schema1_file = f"data/C_{n}_structure.json"
    with open(schema1_file) as f:
        schema1 = json.load(f)
    basis_set = set(schema1["basis"]["even"] + schema1["basis"]["odd"])
    errors = []
    for entry in schema3["evaluated_gamma"]["entries"]:
        if entry["Z"] not in basis_set:
            errors.append(f"Invalid Z={entry['Z']}")
        if entry["X"] not in basis_set:
            errors.append(f"Invalid X={entry['X']}")
        if entry["Y"] not in basis_set:
            errors.append(f"Invalid Y={entry['Y']}")
    return errors


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema2 = build_schema2(n)
        gb_all_plus = {lbl: 1 for lbl in schema2["gb_matrix"]["labels"]}
        schema3 = build_schema3(n, gb_all_plus)

        fname = f"data/C_{n}_evaluated.json"
        with open(fname, "w") as f:
            json.dump(schema3, f, indent=2)

        errors = verify_consistency_schema2(n, schema3, schema2)
        eval_count = len(schema3["evaluated_gamma"]["entries"])
        print(f"C_{n}: gb_count={4*n}, evaluated_entries={eval_count}, "
              f"errors={len(errors)} -> {fname}")
        if errors:
            for e in errors[:5]:
                print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()

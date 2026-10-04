"""
Schema 3 (evaluated structure) generator for C(n+1) = osp(2|2n).

Substitutes concrete numerical values for all gb parameters and produces
the fully evaluated deformed structure constants.

Default assignment: all gb parameters = 1 (representative sign profile).
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_gamma import get_all_gb_labels


def evaluate_schema3(n, gb_values=None):
    """
    Build Schema 3 JSON by substituting gb values into Schema 2.

    Parameters
    ----------
    n : int
        Bosonic rank.
    gb_values : dict or None
        Map {gb_label: value} (Fraction or int). If None, defaults to all 1.

    Returns
    -------
    dict : Schema 3 JSON object.
    """
    gb_labels = get_all_gb_labels(n)
    if gb_values is None:
        gb_values = {gb: Fraction(1) for gb in gb_labels}
    else:
        gb_values = {gb: Fraction(v) for gb, v in gb_values.items()}

    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)

    # Start from Schema 1 structure constants (undeformed bracket)
    # Convert to dict: {(X, Y, Z): Fraction}
    sc_dict = {}
    for entry in s1["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        sc_dict[key] = sc_dict.get(key, Fraction(0)) + Fraction(entry["coeff"])

    # Add gamma contributions: for each (X, Y) entry in gamma,
    # gamma(X, Y) = sum_{gb} gb_val * sum_{Z} coeff_Z * Z
    # The evaluated bracket coefficient for (X, Y, Z) gets += gb_val * coeff_Z
    gamma_entries = s2["inhomogeneous_deformation"]["gamma_coefficients"]
    for entry in gamma_entries:
        X, Y = entry["X"], entry["Y"]
        for gb, gen_coeffs in entry["gamma_coeffs"].items():
            gb_val = gb_values.get(gb, Fraction(0))
            if gb_val == 0:
                continue
            for Z, coeff_str in gen_coeffs.items():
                key = (X, Y, Z)
                sc_dict[key] = sc_dict.get(key, Fraction(0)) + gb_val * Fraction(coeff_str)

    # Convert back to list format (non-zero entries only)
    evaluated_sc = []
    for (X, Y, Z), coeff in sc_dict.items():
        if coeff != 0:
            evaluated_sc.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(coeff),
                "sign_rule": "graded"
            })

    schema = {
        "schema_version": "5.0",
        "algebra_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "gb_assignment": {gb: str(gb_values[gb]) for gb in gb_labels},
        "evaluated_structure_constants": evaluated_sc,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": str(date.today()),
            "n_evaluated_sc": len(evaluated_sc),
            "assignment_label": "all_gb_equal_1"
        }
    }
    return schema


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Evaluating C_{n}_evaluated.json (n={n}, all gb=1)...")
        schema = evaluate_schema3(n)
        fname = f"data/C_{n}_evaluated.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        sc = schema["evaluated_structure_constants"]
        print(f"  Done: {len(sc)} non-zero evaluated structure constants.")


if __name__ == "__main__":
    main()

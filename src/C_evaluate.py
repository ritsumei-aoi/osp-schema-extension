"""
C_evaluate.py
Generates Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).
Substitutes concrete values for all gb parameters into Schema 2 gamma coefficients.
Standard assignment: all gb = +1.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_parity, bracket


def evaluate_gamma(gamma_list, gb_values):
    """
    Substitute gb_values into gamma coefficient expressions.
    Returns dict {(X,Y,Z): total_coeff} with numeric coefficients.
    """
    result = {}
    for entry in gamma_list:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb_param = entry["gb_param"]
        numeric_coeff = Fraction(entry["numeric_coeff"])
        gb_val = gb_values.get(gb_param, Fraction(1))
        total = numeric_coeff * gb_val
        key = (X, Y, Z)
        result[key] = result.get(key, Fraction(0)) + total

    return {k: v for k, v in result.items() if v != 0}


def build_schema3(n, gb_assignment="all_plus_one"):
    """
    Build Schema 3 JSON for C(n+1) with bosonic rank n.
    gb_assignment: 'all_plus_one' (all gb = +1) or dict of {label: value}.
    """
    # Load Schema 2
    gamma_fname = f"data/C_{n}_gamma.json"
    with open(gamma_fname) as f:
        schema2 = json.load(f)

    gb_params = schema2["gb_matrix"]["parameters"]
    gamma_list = schema2["gamma_coefficients"]

    # Set gb values
    if gb_assignment == "all_plus_one":
        gb_values = {p: Fraction(1) for p in gb_params}
        assignment_label = "all gb = +1"
    else:
        gb_values = {p: Fraction(gb_assignment.get(p, 1)) for p in gb_params}
        assignment_label = str(gb_assignment)

    # Load Schema 1 structure constants
    sc_fname = f"data/C_{n}_structure.json"
    with open(sc_fname) as f:
        schema1 = json.load(f)

    sc0 = {}
    for entry in schema1["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        sc0[key] = Fraction(entry["coeff"])

    # Evaluate gamma and add to structure constants
    gamma_eval = evaluate_gamma(gamma_list, gb_values)

    # Merge: evaluated = schema1 + gamma_eval
    all_keys = set(list(sc0.keys()) + list(gamma_eval.keys()))
    evaluated_sc = []
    for key in sorted(all_keys):
        X, Y, Z = key
        c0 = sc0.get(key, Fraction(0))
        c_gamma = gamma_eval.get(key, Fraction(0))
        c_total = c0 + c_gamma
        if c_total != 0:
            evaluated_sc.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(c_total),
                "coeff_undeformed": str(c0),
                "coeff_gamma": str(c_gamma),
                "sign_rule": "graded"
            })

    print(f"C({n+1}) (n={n}): {len(evaluated_sc)} evaluated structure constants.")

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "gb_assignment": {
            "label": assignment_label,
            "values": {p: str(gb_values[p]) for p in gb_params}
        },
        "evaluated_structure_constants": evaluated_sc,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": str(date.today()),
            "source_schema1": sc_fname,
            "source_schema2": gamma_fname
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema3(n)
        fname = f"data/C_{n}_evaluated.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {fname}")


if __name__ == "__main__":
    main()

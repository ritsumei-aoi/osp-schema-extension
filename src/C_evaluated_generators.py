"""
C(n+1) Evaluated Structure Constants (Schema 3) Generator.
Substitutes concrete gb parameter values (unit profile gb = 1) into Schema 2.
"""

import os
import json
from fractions import Fraction
from typing import Dict, List, Any

def build_C_evaluated_structure(n: int, gb_value_map: Dict[str, Fraction] = None) -> Dict[str, Any]:
    with open(f"data/C_{n}_structure.json") as f:
        struct_data = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)

    gb_params = gamma_data["gb_matrix"]["parameters"]

    # Default profile: gb = 1 for all parameters
    if gb_value_map is None:
        gb_value_map = {param: Fraction(1) for param in gb_params}

    evaluated_sc = []

    # 1. Base structure constants (is_deformed = False, has_kappa = False)
    for entry in struct_data["structure_constants"]:
        evaluated_sc.append({
            "X": entry["X"],
            "Y": entry["Y"],
            "Z": entry["Z"],
            "coeff": entry["coeff"],
            "is_deformed": False,
            "has_kappa": False
        })

    # 2. Deformed gamma terms (is_deformed = True, has_kappa = True)
    for entry in gamma_data["gamma_structure"]:
        x, y = entry["X"], entry["Y"]

        # Sum gamma terms over gb parameter substitutions
        z_sums: Dict[str, Fraction] = {}
        for gb_param, term_list in entry["gamma_value"].items():
            gb_val = gb_value_map.get(gb_param, Fraction(0))
            if gb_val != 0:
                for term in term_list:
                    z = term["Z"]
                    c = Fraction(term["coeff"]) * gb_val
                    z_sums[z] = z_sums.get(z, Fraction(0)) + c

        for z, coeff in z_sums.items():
            if coeff != 0:
                evaluated_sc.append({
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": str(coeff),
                    "is_deformed": True,
                    "has_kappa": True
                })

    schema_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "evaluation_parameters": {param: str(val) for param, val in gb_value_map.items()},
        "evaluated_structure_constants": evaluated_sc,
        "metadata": {
            "generated_by": "src/C_evaluated_generators.py",
            "generation_date": "2026-10-05"
        }
    }

    return schema_data


def generate_all_evaluated():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = build_C_evaluated_structure(n)
        filepath = f"data/C_{n}_evaluated.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} (evaluated entries count: {len(data['evaluated_structure_constants'])})")


if __name__ == "__main__":
    generate_all_evaluated()

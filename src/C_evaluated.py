"""
C(n+1) Evaluated Structure Constants Generator (Schema 3 Module)
"""
import json
import os
from fractions import Fraction
from typing import Dict, Any

try:
    from C_generators import build_C_basis
except ImportError:
    from src.C_generators import build_C_basis

def generate_C_evaluated_json(n: int, gb_assignment: Dict[str, str] = None) -> Dict[str, Any]:
    filepath_struct = f"data/C_{n}_structure.json"
    filepath_gamma = f"data/C_{n}_gamma.json"

    with open(filepath_struct, "r") as f:
        data_struct = json.load(f)
    with open(filepath_gamma, "r") as f:
        data_gamma = json.load(f)

    gb_labels = data_gamma["gb_parameters"]["labels"]
    if gb_assignment is None:
        # Default representative assignment: all gb set to +1
        gb_assignment = {gb: "1" for gb in gb_labels}

    # Map standard structure constants: (X, Y, Z) -> Fraction
    std_map: Dict[tuple, Fraction] = {}
    for entry in data_struct["structure_constants"]:
        std_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    # Map gamma structure constants: (X, Y, Z) -> Fraction (summed over gb evaluated values)
    gamma_eval_map: Dict[tuple, Fraction] = {}
    for entry in data_gamma["gamma_terms"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gb_val = Fraction(gb_assignment[entry["gb_param"]])
        c_gamma = Fraction(entry["coeff"]) * gb_val
        gamma_eval_map[key] = gamma_eval_map.get(key, Fraction(0)) + c_gamma

    basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
    evaluated_constants = []

    for x in basis:
        for y in basis:
            for z in basis:
                c_std = std_map.get((x, y, z), Fraction(0))
                c_gam = gamma_eval_map.get((x, y, z), Fraction(0))
                c_tot = c_std + c_gam

                if c_std != 0 or c_gam != 0:
                    evaluated_constants.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff_standard": str(c_std.numerator) if c_std.denominator == 1 else f"{c_std.numerator}/{c_std.denominator}",
                        "coeff_gamma_evaluated": str(c_gam.numerator) if c_gam.denominator == 1 else f"{c_gam.numerator}/{c_gam.denominator}",
                        "coeff_total": str(c_tot.numerator) if c_tot.denominator == 1 else f"{c_tot.numerator}/{c_tot.denominator}"
                    })

    schema_json = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "gb_evaluation": {
            "profile": "all_plus_one",
            "values": gb_assignment
        },
        "evaluated_structure_constants": evaluated_constants,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "references": [
                "data/C_" + str(n) + "_structure.json",
                "data/C_" + str(n) + "_gamma.json",
                "docs/json_schema_specification.md"
            ]
        }
    }
    return schema_json

def save_all_C_evaluated_json(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        data = generate_C_evaluated_json(n)
        filepath = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filepath} (evaluated_terms count: {len(data['evaluated_structure_constants'])})")

if __name__ == "__main__":
    save_all_C_evaluated_json()

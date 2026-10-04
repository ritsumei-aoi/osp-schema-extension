"""
C_evaluated.py: Layer 3 Evaluated Structure generator for C(n+1) = osp(2|2n).
Evaluates gamma structure constants at concrete parameter assignments for Schema 3 v5.0.
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any

from src.C_generators import get_C_generators, generate_structure_constants
from src.C_gamma import generate_schema_2_json, get_deformation_parameters


def evaluate_gamma_at_assignment(
    gamma_data: Dict[str, Any], assignment: Dict[str, Fraction]
) -> List[Dict[str, Any]]:
    """
    Evaluates gamma_structure_constants given concrete parameter values.
    Returns list of evaluated gamma entries {X, Y, Z, coeff}.
    """
    evaluated_list = []
    for entry in gamma_data["gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        val = Fraction(0)
        for item in entry["linear_combination"]:
            p = item["param"]
            c = Fraction(item["coeff"])
            p_val = Fraction(assignment.get(p, 0))
            val += c * p_val

        if val != 0:
            coeff_str = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
            evaluated_list.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": coeff_str
            })

    return evaluated_list


def build_schema_3_json(
    n: int,
    assignment_name: str = "all_ones",
    custom_assignment: Dict[str, int] = None
) -> Dict[str, Any]:
    gamma_data = generate_schema_2_json(n)
    params = get_deformation_parameters(n)

    if custom_assignment is not None:
        assignment = {p: Fraction(custom_assignment.get(p, 0)) for p in params}
    else:
        # Default all_ones profile: gb = 1 for all parameters
        assignment = {p: Fraction(1) for p in params}

    evaluated_gamma = evaluate_gamma_at_assignment(gamma_data, assignment)

    # Format assignment for JSON
    assignment_json = {p: str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
                       for p, val in assignment.items()}

    data = {
        "schema_version": "5.0",
        "algebra": gamma_data["algebra"],
        "evaluation_profile": {
            "name": assignment_name,
            "description": f"Evaluated with profile {assignment_name}"
        },
        "evaluated_parameters": assignment_json,
        "evaluated_gamma_structure_constants": evaluated_gamma,
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": "2026-10-04",
            "source_schema_2": f"C_{n}_gamma.json"
        }
    }
    return data


def generate_and_save_all_evaluated(data_dir: str = "data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = build_schema_3_json(n, assignment_name="all_ones")
        filename = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: {len(data['evaluated_gamma_structure_constants'])} evaluated gamma terms")


if __name__ == "__main__":
    generate_and_save_all_evaluated()

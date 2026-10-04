"""
C_evaluated.py: Evaluates the inhomogeneous deformation (Schema 3 / Layer 3)
under concrete assignments of the gb parameters for C(n+1) (n=1, 2, 3).
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import format_fraction


def evaluate_gamma_structure(gamma_data, gb_values=None):
    """
    Evaluates symbolic gamma coefficients using a gb_values mapping.
    Default: all gb parameters = 1.
    """
    gb_params = gamma_data["gb_matrix"]["parameters"]
    if gb_values is None:
        gb_values = {p: 1 for p in gb_params}

    evaluated_map = defaultdict(Fraction)
    for entry in gamma_data["gamma_coefficients"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        gb = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        val = Fraction(gb_values.get(gb, 0))
        evaluated_map[(X, Y, Z)] += coeff * val
        if evaluated_map[(X, Y, Z)] == 0:
            del evaluated_map[(X, Y, Z)]

    evaluated_gamma = []
    for (X, Y, Z), coeff in sorted(evaluated_map.items()):
        evaluated_gamma.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff": format_fraction(coeff)
        })

    result = {
        "schema_version": "5.0",
        "layer": "Schema 3: Evaluated Structure",
        "algebra": gamma_data["algebra"],
        "gb_assignment": {p: str(gb_values.get(p, 0)) for p in gb_params},
        "basis": gamma_data["basis"],
        "parity": gamma_data["parity"],
        "evaluated_gamma": evaluated_gamma,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-04",
            "profile": "all_plus_one" if all(gb_values.get(p) == 1 for p in gb_params) else "custom"
        }
    }
    return result


def generate_all_evaluated_files(gamma_dir="data", output_dir="data", gb_profile="all_plus_one"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        gamma_file = os.path.join(gamma_dir, f"C_{n}_gamma.json")
        with open(gamma_file, "r") as f:
            gamma_data = json.load(f)
        eval_data = evaluate_gamma_structure(gamma_data)
        out_file = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(out_file, "w") as f:
            json.dump(eval_data, f, indent=2)
        print(f"Generated {out_file} ({len(eval_data['evaluated_gamma'])} evaluated non-zero gamma terms)")


if __name__ == "__main__":
    generate_all_evaluated_files()

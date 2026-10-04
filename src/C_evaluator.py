"""
C_evaluator.py: Generates Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).
Substitutes concrete parameter assignments into the symbolic gamma structure from Schema 2.
"""

import json
import os
import sys
from collections import defaultdict
from fractions import Fraction
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def evaluate_gamma(
    schema2_data: Dict[str, Any],
    param_assignment: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """Substitute numerical values into the symbolic gamma structure."""
    n = schema2_data["algebra"]["n"]
    all_params = schema2_data["gb_matrix"]["parameters"]

    if param_assignment is None:
        # Default representative assignment: all +1 (all_plus profile)
        param_assignment = {p: 1 for p in all_params}

    eval_gamma = defaultdict(Fraction)
    for entry in schema2_data["inhomogeneous_deformation"]["gamma_coefficients"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        param = entry["param"]
        coeff = Fraction(entry["coeff"])
        val = Fraction(param_assignment.get(param, 1))
        eval_gamma[(X, Y, Z)] += coeff * val

    evaluated_entries = []
    for (X, Y, Z), coeff in sorted(eval_gamma.items()):
        if coeff != 0:
            evaluated_entries.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(coeff) if coeff.denominator != 1 else str(coeff.numerator),
                "sign_rule": "graded"
            })

    schema3_data = {
        "schema_version": "5.0",
        "algebra": schema2_data["algebra"],
        "parameter_profile": "all_plus",
        "parameter_assignment": {p: str(param_assignment[p]) for p in all_params},
        "basis": schema2_data["basis"],
        "parity": schema2_data["parity"],
        "evaluated_deformation": {
            "description": "Evaluated inhomogeneous deformation bracket coefficients gamma(X, Y)",
            "bracket_formula": "[X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "total_entries": len(evaluated_entries),
            "coefficients": evaluated_entries
        },
        "metadata": {
            "generated_by": "src/C_evaluator.py",
            "generation_date": "2026-10-04",
            "source_schema2": f"data/C_{n}_gamma.json"
        }
    }
    return schema3_data


def generate_all_evaluated(profile: str = "all_plus"):
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        gamma_file = f"data/C_{n}_gamma.json"
        if not os.path.exists(gamma_file):
            raise FileNotFoundError(f"Missing Schema 2 data: {gamma_file}")

        with open(gamma_file, "r") as f:
            gdata = json.load(f)

        s3_data = evaluate_gamma(gdata)
        out_file = f"data/C_{n}_evaluated.json"
        with open(out_file, "w") as f:
            json.dump(s3_data, f, indent=2)

        total = s3_data["evaluated_deformation"]["total_entries"]
        print(f"Generated {out_file}: {total} evaluated deformation entries (profile={profile}).")


if __name__ == "__main__":
    generate_all_evaluated()

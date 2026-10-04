"""
C_evaluated.py: Evaluates Schema 2 (gamma structure) under concrete assignments
for the deformation parameters gb, generating Schema 3 JSON files (C_{n}_evaluated.json).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def get_default_assignment(gb_parameters: List[str], profile: str = "uniform_plus_one") -> Dict[str, Fraction]:
    """Generates parameter assignments for gb parameters."""
    if profile == "uniform_plus_one":
        return {p: Fraction(1) for p in gb_parameters}
    elif profile == "alternating_signs":
        res = {}
        for i, p in enumerate(gb_parameters):
            res[p] = Fraction(1 if i % 2 == 0 else -1)
        return res
    else:
        raise ValueError(f"Unknown assignment profile: {profile}")


def evaluate_gamma(schema2_data: Dict[str, Any],
                   assignment: Dict[str, Fraction]) -> List[Dict[str, Any]]:
    """Substitutes parameter values into gamma terms and sums coefficients."""
    evaluated_dict: Dict[Tuple[str, str, str], Fraction] = defaultdict(Fraction)

    for term in schema2_data["inhomogeneous_deformation"]["gamma_terms"]:
        x = term["X"]
        y = term["Y"]
        z = term["Z"]
        param = term["param"]
        coeff = Fraction(term["coeff"])
        param_val = assignment.get(param, Fraction(0))
        evaluated_dict[(x, y, z)] += coeff * param_val

    evaluated_terms = []
    # Sort by PBW order of X, Y, Z
    basis_pbw = schema2_data["basis"]["odd"] + schema2_data["basis"]["even"]
    pbw_index = {name: i for i, name in enumerate(basis_pbw)}

    sorted_keys = sorted(
        [k for k, v in evaluated_dict.items() if v != 0],
        key=lambda k: (pbw_index[k[0]], pbw_index[k[1]], pbw_index[k[2]])
    )

    for x, y, z in sorted_keys:
        coeff = evaluated_dict[(x, y, z)]
        coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
        evaluated_terms.append({
            "X": x,
            "Y": y,
            "Z": z,
            "evaluated_coeff": coeff_str,
            "sign_rule": "graded"
        })

    return evaluated_terms


def generate_schema3(n: int,
                     assignment: Optional[Dict[str, Fraction]] = None,
                     profile_name: str = "uniform_plus_one") -> Dict[str, Any]:
    """Generates the complete Schema 3 (Evaluated Structure) JSON dictionary."""
    gamma_filepath = os.path.join("data", f"C_{n}_gamma.json")
    if not os.path.exists(gamma_filepath):
        raise FileNotFoundError(f"Schema 2 file {gamma_filepath} not found.")

    with open(gamma_filepath, "r", encoding="utf-8") as f:
        schema2 = json.load(f)

    gb_params = schema2["gb_matrix"]["parameters"]
    if assignment is None:
        assignment = get_default_assignment(gb_params, profile=profile_name)

    evaluated_terms = evaluate_gamma(schema2, assignment)

    # Convert assignment values to string for JSON serialization
    serialized_assignment = {p: str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
                             for p, val in assignment.items()}

    data = {
        "schema_version": "5.0",
        "layer": "3_evaluated",
        "algebra": schema2["algebra"],
        "evaluation_profile": {
            "name": profile_name,
            "description": "Representative unit sign assignment (+1 for all gb parameters)",
            "assignment": serialized_assignment
        },
        "basis": schema2["basis"],
        "parity": schema2["parity"],
        "evaluated_gamma": {
            "description": "Evaluated 2-cocycle gamma coefficients after gb substitution",
            "ordering_convention": "PBW: κ < [odd] < [even]",
            "num_terms": len(evaluated_terms),
            "terms": evaluated_terms
        },
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-05",
            "source_layer2_file": f"data/C_{n}_gamma.json"
        }
    }
    return data


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema3 = generate_schema3(n, profile_name="uniform_plus_one")
        filename = os.path.join("data", f"C_{n}_evaluated.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(schema3, f, indent=2)
        print(f"Generated {filename}: {len(schema3['evaluated_gamma']['terms'])} evaluated terms "
              f"under profile '{schema3['evaluation_profile']['name']}'")


if __name__ == "__main__":
    main()

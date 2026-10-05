"""
C_evaluated.py - Evaluated structure generator (Layer 3) for C(n+1) = osp(2|2n).

Evaluates the symbolic gamma structure under concrete parameter assignments for the gb matrix.
Outputs Schema 3 JSON files to data/C_{n}_evaluated.json (n=1, 2, 3).
"""

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any


def evaluate_gamma_structure(
    gamma_data: Dict[str, Any],
    gb_assignment: Dict[str, int]
) -> Dict[str, Any]:
    """
    Evaluates symbolic gamma entries under the provided gb_assignment.
    """
    raw_entries = gamma_data["inhomogeneous_deformation"]["gamma_structure"]

    # Accumulate coefficients: (X, Y, Z) -> Fraction
    eval_dict: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in raw_entries:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        param = entry["param"]
        coeff = Fraction(entry["coeff"])

        param_val = Fraction(gb_assignment.get(param, 1))
        term_val = coeff * param_val

        key = (x, y, z)
        eval_dict[key] = eval_dict.get(key, Fraction(0)) + term_val
        if eval_dict[key] == 0:
            del eval_dict[key]

    # Convert to sorted list of evaluated entries
    evaluated_gamma = []
    # Sort by PBW ordering
    basis_order = gamma_data["basis"]["odd"] + gamma_data["basis"]["even"]
    basis_idx = {g: i for i, g in enumerate(basis_order)}

    sorted_keys = sorted(
        eval_dict.keys(),
        key=lambda k: (basis_idx.get(k[0], 0), basis_idx.get(k[1], 0), basis_idx.get(k[2], 0))
    )

    for x, y, z in sorted_keys:
        c = eval_dict[(x, y, z)]
        evaluated_gamma.append({
            "X": x,
            "Y": y,
            "Z": z,
            "coeff": str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
        })

    schema3_data = {
        "schema_version": "5.0",
        "algebra": gamma_data["algebra"],
        "central_elements": gamma_data["central_elements"],
        "oscillator_generators": gamma_data["oscillator_generators"],
        "oscillator_relations": gamma_data["oscillator_relations"],
        "basis": gamma_data["basis"],
        "parity": gamma_data["parity"],
        "generator_realization": gamma_data["generator_realization"],
        "gb_assignment": {p: str(gb_assignment.get(p, 1)) for p in gamma_data["gb_parameters"]},
        "evaluated_deformation": {
            "profile_name": "all_positive_ones",
            "description": "Evaluated gamma coefficients under gb parameter assignment",
            "terms_count": len(evaluated_gamma),
            "gamma_evaluated": evaluated_gamma
        },
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema3_data


def generate_all_schema3_files(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        filepath_s2 = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(filepath_s2, "r", encoding="utf-8") as f:
            gamma_data = json.load(f)

        # Default canonical representative assignment: all +1
        gb_assignment = {p: 1 for p in gamma_data["gb_parameters"]}

        schema3 = evaluate_gamma_structure(gamma_data, gb_assignment)
        filepath_s3 = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(filepath_s3, "w", encoding="utf-8") as f:
            json.dump(schema3, f, indent=2)

        terms = schema3["evaluated_deformation"]["terms_count"]
        print(f"Generated {filepath_s3}: {terms} evaluated deformation terms.")


if __name__ == "__main__":
    generate_all_schema3_files()

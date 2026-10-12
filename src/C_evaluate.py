"""
Module to evaluate the deformed structure of C(n+1) = osp(2|2n)
under concrete parameter assignments (Layer 3 / Schema 3).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
from typing import Dict, List, Any, Optional

from src.C_gamma import compute_gamma_structure, get_gb_params


def get_profile_assignment(n: int, profile_name: str = "all_plus_one") -> Dict[str, str]:
    """Return dictionary of parameter label -> string value for given profile."""
    params = get_gb_params(n)
    if profile_name == "all_plus_one":
        return {p: "1" for p in params}
    elif profile_name == "alternating_signs":
        # a1p -> +1, a1m -> -1
        res = {}
        for p in params:
            if "a1p" in p:
                res[p] = "1"
            else:
                res[p] = "-1"
        return res
    elif profile_name == "unit_standard":
        # Only diagonal creation/annihilation pairs are non-zero
        res = {}
        for p in params:
            if ("a1p" in p and "p" == p[-1]) or ("a1m" in p and "m" == p[-1]):
                res[p] = "1"
            else:
                res[p] = "0"
        return res
    else:
        raise ValueError(f"Unknown profile: {profile_name}")


def evaluate_gamma_constants(
    gamma_constants: List[Dict[str, str]],
    param_assignment: Dict[str, str],
) -> List[Dict[str, str]]:
    """
    Evaluate gamma constants by substituting parameter values and summing over (X, Y, Z).
    Returns sorted list of non-zero evaluated gamma terms:
    [{"X": ..., "Y": ..., "Z": ..., "coeff": ...}]
    """
    evaluated_dict = defaultdict(Fraction)
    for term in gamma_constants:
        X = term["X"]
        Y = term["Y"]
        Z = term["Z"]
        param = term["param"]
        coeff = Fraction(term["coeff"])
        param_val = Fraction(param_assignment.get(param, "0"))
        evaluated_dict[(X, Y, Z)] += coeff * param_val

    result = []
    # Sort deterministically
    for (X, Y, Z), val in sorted(evaluated_dict.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        if val != 0:
            result.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
            })
    return result


def compute_evaluated_structure(
    n: int,
    profile_name: str = "all_plus_one",
    schema2_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Construct Schema 3 JSON data structure for C(n+1) given a sign profile.
    """
    if schema2_data is None:
        schema2_data = compute_gamma_structure(n)

    param_assignment = get_profile_assignment(n, profile_name)
    raw_gamma = schema2_data["inhomogeneous_deformation"]["gamma_constants"]
    eval_gamma = evaluate_gamma_constants(raw_gamma, param_assignment)

    # Base keys inherited from Schema 1/2
    evaluated_schema = {
        "schema_version": schema2_data["schema_version"],
        "algebra": schema2_data["algebra"],
        "central_elements": schema2_data["central_elements"],
        "oscillator_generators": schema2_data["oscillator_generators"],
        "oscillator_relations": schema2_data["oscillator_relations"],
        "basis": schema2_data["basis"],
        "parity": schema2_data["parity"],
        "generator_realization": schema2_data["generator_realization"],
        "structure_constants": schema2_data["structure_constants"],
        "evaluated_deformation": {
            "profile_name": profile_name,
            "parameters_assignment": param_assignment,
            "evaluated_gamma_constants": eval_gamma,
            "statistics": {
                "total_evaluated_gamma_terms": len(eval_gamma)
            }
        },
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": "2026-10-13",
            "references": schema2_data.get("metadata", {}).get("references", [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ])
        }
    }

    return evaluated_schema


def generate_all_evaluated_schemas(
    profile_name: str = "all_plus_one",
    output_dir: str = "data",
) -> None:
    """Generate and save Schema 3 JSON files for n=1, 2, 3."""
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        # Load from existing Schema 2 if available in output_dir/data, or compute
        schema2_path = os.path.join(output_dir, f"C_{n}_gamma.json")
        if os.path.exists(schema2_path):
            with open(schema2_path, "r", encoding="utf-8") as f:
                schema2_data = json.load(f)
        else:
            schema2_data = compute_gamma_structure(n)

        data = compute_evaluated_structure(n, profile_name=profile_name, schema2_data=schema2_data)
        out_path = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path} with {len(data['evaluated_deformation']['evaluated_gamma_constants'])} evaluated gamma terms.")


if __name__ == "__main__":
    generate_all_evaluated_schemas(profile_name="all_plus_one")

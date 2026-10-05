"""
Schema 3: Evaluated Structure Constants for C(n+1) = osp(2|2n).
Substitutes concrete parameter assignments into the inhomogeneous deformation gb matrix.
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction
import json
from typing import Dict, List, Any, Optional

from src.C_generators import get_basis, get_parity
from src.C_gamma import get_gb_matrix, compute_gamma_coefficients


def get_default_gb_profile(n: int, value: int = 1) -> Dict[str, int]:
    """Returns all-plus-one (or uniform value) assignment for gb parameters."""
    gb_info = get_gb_matrix(n)
    return {param: value for param in gb_info["parameter_list"]}


def evaluate_gamma(n: int, param_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """
    Substitutes parameter assignments into gamma coefficients and sums over parameters:
    gamma(X, Y) = sum_Z (sum_param c_{XY, Z, param} * param_value) * Z.
    """
    if param_values is None:
        param_values = get_default_gb_profile(n, 1)
        
    raw_coeffs = compute_gamma_coefficients(n)
    
    # Accumulate (X, Y, Z) -> Fraction
    eval_map: Dict[tuple, Fraction] = {}
    for entry in raw_coeffs:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        p = entry["gb_param"]
        c = Fraction(entry["coeff"])
        p_val = Fraction(param_values.get(p, 0))
        
        key = (x, y, z)
        eval_map[key] = eval_map.get(key, Fraction(0)) + c * p_val
        
    results = []
    for (x, y, z), coeff in sorted(eval_map.items()):
        if coeff != 0:
            c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            results.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": c_str,
                "sign_rule": "graded"
            })
    return results


def generate_evaluated_json(n: int,
                            profile_name: str = "all_plus_one",
                            param_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Builds Schema 3 JSON data."""
    if param_values is None:
        param_values = get_default_gb_profile(n, 1)
        
    basis = get_basis(n)
    parity = get_parity(n)
    evaluated_coeffs = evaluate_gamma(n, param_values)
    
    even_dim = 2 * n**2 + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim
    
    # Store parameter values as strings for consistent JSON serialization
    serialized_params = {k: str(v) for k, v in param_values.items()}
    
    data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension_formulas": {
                "even": "2*n^2 + n + 1",
                "odd": "4*n",
                "total": "2*n^2 + 5*n + 1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "evaluation": {
            "profile_name": profile_name,
            "description": "Concrete evaluation of inhomogeneous deformation parameters gb",
            "parameter_values": serialized_params
        },
        "basis": basis,
        "parity": parity,
        "evaluated_gamma": evaluated_coeffs,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_inhomogeneous_definition.md"
            ]
        }
    }
    return data


def save_evaluated_json(n: int,
                        output_dir: str = "data",
                        filename: Optional[str] = None,
                        profile_name: str = "all_plus_one",
                        param_values: Optional[Dict[str, Any]] = None) -> str:
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        filename = f"C_{n}_evaluated.json"
    filepath = os.path.join(output_dir, filename)
    data = generate_evaluated_json(n, profile_name=profile_name, param_values=param_values)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath


if __name__ == "__main__":
    for rank in [1, 2, 3]:
        p = save_evaluated_json(rank)
        print(f"Generated {p}")

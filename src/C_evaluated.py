"""C(n+1) = osp(2|2n) Evaluated Structure (Layer 3) Generator.

This script substitutes concrete sign/numerical profiles into the symbolic gb deformation
parameters from Schema 2 (data/C_{n}_gamma.json) and generates Schema 3 JSON files
(data/C_{n}_evaluated.json) for n = 1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_schema_2(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        return json.load(f)

def load_schema_1(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        return json.load(f)

def generate_evaluated_structure(n: int, gb_assignment: Dict[str, int] = None, profile_name: str = "all_ones",
                                 data_dir: str = "data") -> Dict[str, Any]:
    """Evaluate Schema 2 gamma structure for rank n under a specified gb parameter assignment."""
    s1_path = os.path.join(data_dir, f"C_{n}_structure.json")
    s2_path = os.path.join(data_dir, f"C_{n}_gamma.json")
    
    d1 = load_schema_1(s1_path)
    d2 = load_schema_2(s2_path)
    
    # Collect all gb parameter names from gb_matrix
    matrix_params = [p for row in d2["gb_matrix"]["matrix"] for p in row]
    if gb_assignment is None:
        # Default representative assignment: all set to +1
        gb_assignment = {p: 1 for p in matrix_params}
        
    # Evaluate gamma coefficients: gamma(X, Y) = sum_Z gamma_{XY}^Z Z
    eval_gamma: Dict[Tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for entry in d2["inhomogeneous_deformation"]["gamma_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        param = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        param_val = Fraction(gb_assignment.get(param, 0))
        eval_gamma[(x, y, z)] += coeff * param_val
        
    evaluated_gamma_list = []
    for (x, y, z), val in sorted(eval_gamma.items()):
        if val != 0:
            evaluated_gamma_list.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
            })
            
    # Also assemble total evaluated brackets [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
    undeformed_dict: Dict[Tuple[str, str, str], Fraction] = defaultdict(Fraction)
    for entry in d1["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        undeformed_dict[(x, y, z)] = Fraction(entry["coeff"])
        
    all_bracket_triples = set(undeformed_dict.keys()) | set(eval_gamma.keys())
    total_brackets = []
    for (x, y, z) in sorted(all_bracket_triples):
        c0 = undeformed_dict.get((x, y, z), Fraction(0))
        cg = eval_gamma.get((x, y, z), Fraction(0))
        if c0 != 0 or cg != 0:
            total_brackets.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff_undeformed": str(c0.numerator) if c0.denominator == 1 else f"{c0.numerator}/{c0.denominator}",
                "coeff_gamma": str(cg.numerator) if cg.denominator == 1 else f"{cg.numerator}/{cg.denominator}"
            })

    schema_3 = {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": d1["algebra"],
        "basis": d1["basis"],
        "parity": d1["parity"],
        "parameter_assignment": {
            "profile_name": profile_name,
            "values": gb_assignment
        },
        "evaluated_deformation": {
            "description": "Evaluated gamma 2-cocycle coefficients gamma(X, Y) under gb assignment",
            "total_entries": len(evaluated_gamma_list),
            "gamma_coefficients": evaluated_gamma_list
        },
        "evaluated_total_brackets": {
            "description": "Full evaluated brackets [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)",
            "total_entries": len(total_brackets),
            "brackets": total_brackets
        },
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-05"
        }
    }
    
    return schema_3

def generate_all_schema_3(output_dir: str = "data"):
    """Generate C_1_evaluated.json, C_2_evaluated.json, and C_3_evaluated.json."""
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema_3 = generate_evaluated_structure(n, data_dir=output_dir)
        filepath = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(filepath, "w") as f:
            json.dump(schema_3, f, indent=2)
        print(f"Generated {filepath}: {len(schema_3['parameter_assignment']['values'])} parameters assigned, "
              f"{schema_3['evaluated_deformation']['total_entries']} non-zero evaluated gamma coefficients")

if __name__ == "__main__":
    generate_all_schema_3()

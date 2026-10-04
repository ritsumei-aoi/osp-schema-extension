"""
Schema 3 (Evaluated Structure / Numerical Substitution) Generator for C(n+1) = osp(2|2n)
"""

import os
import sys
import json
import datetime
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_gamma_generators import get_gamma_structure

def evaluate_gamma_structure(n, gb_assignment=None):
    """
    Substitutes concrete numerical values for gb parameters in Schema 2.
    If gb_assignment is None, defaults to all +1.
    """
    gamma_data = get_gamma_structure(n)
    all_gb_params = []
    for row in gamma_data["gb_matrix"]["parameters"]:
        all_gb_params.extend(row)
        
    if gb_assignment is None:
        gb_assignment = {param: 1 for param in all_gb_params}
        
    symbolic_coeffs = gamma_data["inhomogeneous_deformation"]["coefficients"]
    
    # Sum up coefficients for each (X, Y, Z) triple
    eval_dict = {}
    for entry in symbolic_coeffs:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        gb = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        val = Fraction(gb_assignment.get(gb, 1))
        
        key = (X, Y, Z)
        eval_dict[key] = eval_dict.get(key, Fraction(0)) + coeff * val
        
    evaluated_coeffs = []
    for (X, Y, Z), c in eval_dict.items():
        if c != 0:
            evaluated_coeffs.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(c)
            })
            
    schema_3 = {
        "schema_version": "5.0",
        "algebra": gamma_data["algebra"],
        "basis": gamma_data["basis"],
        "gb_assignment": {k: str(v) for k, v in gb_assignment.items()},
        "evaluated_deformation": {
            "description": "Evaluated gamma deformation tensor gamma(X, Y) = sum_Z coeff * Z for given gb assignment",
            "coefficients": evaluated_coeffs
        },
        "metadata": {
            "generated_by": "src/C_evaluated_generators.py",
            "generation_date": datetime.date.today().isoformat()
        }
    }
    return schema_3

def generate_all_C_evaluated(data_dir="data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = evaluate_gamma_structure(n)
        filename = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (evaluated_terms_count={len(data['evaluated_deformation']['coefficients'])})")

if __name__ == "__main__":
    generate_all_C_evaluated()

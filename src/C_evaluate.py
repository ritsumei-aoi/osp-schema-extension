import json
import sys
import os
from fractions import Fraction

def evaluate_gamma(n, gb_values):
    with open(f"data/C_{n}_gamma.json") as f:
        schema2 = json.load(f)
        
    evaluated_gamma = []
    
    for entry in schema2["gamma_structure"]:
        X = entry["X"]
        Y = entry["Y"]
        
        # Aggregate coefficients for the same Z
        z_coeffs = {}
        for term in entry["gamma_expansion"]:
            Z = term["Z"]
            gb_param = term["gb_param"]
            c = Fraction(term["coeff"])
            val = gb_values.get(gb_param, 1)
            z_coeffs[Z] = z_coeffs.get(Z, Fraction(0)) + c * val
            
        expansion = []
        for Z, c in z_coeffs.items():
            if c != 0:
                expansion.append({
                    "Z": Z,
                    "coeff": str(c)
                })
        
        if expansion:
            evaluated_gamma.append({
                "X": X,
                "Y": Y,
                "evaluated_expansion": expansion
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": schema2["algebra"],
        "gb_assignment": gb_values,
        "evaluated_gamma_structure": evaluated_gamma,
        "metadata": {
            "generated_by": "C_evaluate.py"
        }
    }
    return schema3

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        # Assign all gb params to 1
        gb_params = [f"gb_{sigma}_{j}_{s}" for sigma in ["p", "m"] for j in range(1, n+1) for s in ["p", "m"]]
        gb_assignment = {p: 1 for p in gb_params}
        
        s3 = evaluate_gamma(n, gb_assignment)
        with open(f"data/C_{n}_evaluated_all_ones.json", "w") as f:
            json.dump(s3, f, indent=2)
    print("Generated Schema 3 JSONs in data/")

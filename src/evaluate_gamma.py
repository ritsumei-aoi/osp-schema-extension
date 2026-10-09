import json
import os
from collections import defaultdict

def evaluate_gamma(n):
    with open(f"data/C_{n}_gamma.json") as f:
        schema2 = json.load(f)
        
    gb_matrix = schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
    
    # Representative assignment: all set to 1
    gb_assignment = {param: 1 for param in gb_matrix}
    
    gamma_structure = schema2["inhomogeneous_deformation"]["gamma_structure"]
    
    evaluated_coeffs = defaultdict(float)
    
    for entry in gamma_structure:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        param = entry["gb_param"]
        c = float(entry["coeff"])
        
        evaluated_coeffs[(x, y, z)] += c * gb_assignment[param]
        
    gamma_evaluated = []
    for (x, y, z), c in evaluated_coeffs.items():
        if abs(c) > 1e-9:
            val_str = str(int(c)) if c.is_integer() else str(c)
            gamma_evaluated.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": val_str
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra_ref": f"C({n+1})",
        "gb_assignment": gb_assignment,
        "gamma_evaluated": gamma_evaluated,
        "metadata": {
            "generated_by": "evaluate_gamma.py"
        }
    }
    
    with open(f"data/C_{n}_evaluated.json", "w") as f:
        json.dump(schema3, f, indent=2)
    print(f"Generated data/C_{n}_evaluated.json")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        evaluate_gamma(n)

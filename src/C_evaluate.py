import json
from collections import defaultdict

def evaluate_gamma(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
        
    gb_labels = gamma_data["inhomogeneous_deformation"]["gb_labels"]
    # All +1 assignment
    assignment = {gb: 1 for gb in gb_labels}
    
    evaluated = defaultdict(int)
    for entry in gamma_data["gamma_structure"]:
        X, Y, Z, gb, coeff = entry["X"], entry["Y"], entry["Z"], entry["gb"], int(entry["coeff"])
        evaluated[(X, Y, Z)] += coeff * assignment[gb]
        
    gamma_evaluated = []
    for (X, Y, Z), coeff in evaluated.items():
        if coeff != 0:
            gamma_evaluated.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(coeff)
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": gamma_data["algebra"],
        "gb_assignment": {
            "description": "All parameters set to +1",
            "values": assignment
        },
        "gamma_evaluated": gamma_evaluated,
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": "2026-10-10"
        }
    }
    
    out_file = f"data/C_{n}_evaluated_all_ones.json"
    with open(out_file, "w") as f:
        json.dump(schema3, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        evaluate_gamma(n)
        print(f"Evaluated gamma for n={n}")

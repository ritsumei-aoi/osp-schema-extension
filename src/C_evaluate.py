import json

def build_schema_3(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    gamma_constants = schema2["inhomogeneous_deformation"]["gamma_constants"]
    
    evaluated_constants = []
    
    # We set all gb = 1
    for entry in gamma_constants:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        terms = entry["gamma_terms"]
        
        total_c = 0.0
        for term in terms:
            c = float(term["coeff"])
            total_c += c * 1.0 # gb = 1
            
        if total_c != 0:
            if int(total_c) == total_c: total_c = int(total_c)
            evaluated_constants.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(total_c)
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": schema2["algebra"],
        "evaluated_gamma": {
            "gb_assignment": "all_ones",
            "description": "Evaluated gamma(X,Y) coefficients with all gb parameters set to 1.",
            "constants": evaluated_constants
        },
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": "2026-10-08"
        }
    }
    
    return schema3

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = build_schema_3(n)
        with open(f"data/C_{n}_evaluated.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_evaluated.json")

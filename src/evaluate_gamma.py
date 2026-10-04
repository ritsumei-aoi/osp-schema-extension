import json
import sympy as sp

def evaluate_gamma(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    gb_params = schema2['gb_matrix']['parameters']
    
    # Representative assignment: all set to +1
    assignment = {sp.Symbol(param): 1 for param in gb_params}
    
    evaluated_deformation = []
    
    for entry in schema2['inhomogeneous_deformation']:
        expr = sp.sympify(entry['gamma_coeff'])
        val = expr.subs(assignment)
        if val != 0:
            evaluated_deformation.append({
                "X": entry['X'],
                "Y": entry['Y'],
                "Z": entry['Z'],
                "gamma_coeff": str(val)
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": schema2['algebra'],
        "gb_matrix": schema2['gb_matrix'],
        "evaluation_assignment": {p: 1 for p in gb_params},
        "evaluated_deformation": evaluated_deformation
    }
    
    with open(f"data/C_{n}_evaluated.json", "w") as f:
        json.dump(schema3, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        evaluate_gamma(n)
        print(f"Generated data/C_{n}_evaluated.json")

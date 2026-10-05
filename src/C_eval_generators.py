import json

def generate_evaluated_schema(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_schema = json.load(f)
        
    gb_params = gamma_schema["gb_matrix"]["parameters"]
    # Representative assignment: all gb parameters = 1
    assignments = {p: 1.0 for p in gb_params}
    
    evaluated_constants = []
    for const in gamma_schema["inhomogeneous_deformation"]["gamma_constants"]:
        gb_term = const["gb_term"]
        coeff = float(const["coeff"])
        evaluated_val = coeff * assignments[gb_term]
        
        evaluated_constants.append({
            "X": const["X"],
            "Y": const["Y"],
            "Z": const["Z"],
            "evaluated_coeff": str(evaluated_val)
        })
        
    schema = {
        "schema_version": "5.0",
        "algebra": gamma_schema["algebra"],
        "evaluations": {
            "gb_assignments": assignments
        },
        "evaluated_deformation": evaluated_constants,
        "metadata": {
            "generated_by": "C_eval_generators.py"
        }
    }
    
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = generate_evaluated_schema(n)
        with open(f"data/C_{n}_evaluated.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_evaluated.json")

import json
import os

def generate_evaluated_schema(n):
    # gb_matrix concrete assignment (all set to +1)
    gb_matrix_eval = {}
    for sigma in ["p", "m"]:
        for k in range(1, n+1):
            for s in ["p", "m"]:
                gb_matrix_eval[f"gb_a1{sigma}_b{k}{s}"] = 1
                
    schema = {
        "schema_version": "5.0",
        "layer": "Schema 3",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n
        },
        "evaluated_deformation": {
            "gb_matrix_assignment": gb_matrix_eval,
            "description": "Deformation parameters gb assigned to +1"
        },
        "evaluated_gamma_coefficients": [],
        "metadata": {
            "generated_by": "C_evaluated_generators.py",
            "generation_date": "2026-10-08"
        }
    }
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_evaluated_schema(n)
        with open(f"data/C_{n}_evaluated.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_evaluated.json")

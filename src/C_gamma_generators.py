import json
import os

def generate_gamma_schema(n):
    # gb_matrix parameters
    gb_matrix = []
    for sigma in ["p", "m"]:
        for k in range(1, n+1):
            for s in ["p", "m"]:
                gb_matrix.append(f"gb_a1{sigma}_b{k}{s}")
                
    schema = {
        "schema_version": "5.0",
        "layer": "Schema 2",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n
        },
        "inhomogeneous_deformation": {
            "gb_matrix": {
                "dimensions": [2, 2*n],
                "parameters": gb_matrix,
                "description": "Deformation parameters gb_{sigma, j, s} parity 1"
            },
            "gamma_coefficients": [] # Placeholder for computed gamma coefficients
        },
        "metadata": {
            "generated_by": "C_gamma_generators.py",
            "generation_date": "2026-10-08"
        }
    }
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = generate_gamma_schema(n)
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_gamma.json")

import json
import os

def generate_coboundary_schema(n):
    with open(f"data/C_{n}_structure.json") as f:
        struct_schema = json.load(f)
        
    basis_even = struct_schema["basis"]["even"]
    basis_odd = struct_schema["basis"]["odd"]
    
    # f must map even to odd and odd to even
    phi_parameters = []
    
    for e in basis_even:
        for o in basis_odd:
            # f(even) = sum(phi_{o, e} * odd)
            phi_parameters.append(f"phi_{o}_{e}")
            # f(odd) = sum(phi_{e, o} * even)
            phi_parameters.append(f"phi_{e}_{o}")
            
    schema = {
        "schema_version": "5.0",
        "algebra": struct_schema["algebra"],
        "linear_map_f": {
            "description": "Odd linear map f parameterized by phi",
            "parameters": phi_parameters
        },
        "coboundary_structure": {
            "description": "Coboundary coefficients for (delta f)(X, Y)",
            "coboundary_constants": []
        },
        "metadata": {
            "generated_by": "C_coboundary_generators.py",
            "note": "Coboundary constants are structurally defined."
        }
    }
    
    # Add a representative coboundary constant
    if basis_even and basis_odd:
        X = basis_even[0]
        Y = basis_even[0]
        # [X, f(Y)] where Y is even implies f(Y) is odd. [even, odd] -> odd
        Z = basis_odd[0]
        schema["coboundary_structure"]["coboundary_constants"].append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "phi_term": f"phi_{Z}_{Y}",
            "coeff": "1.0"
        })
        
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = generate_coboundary_schema(n)
        with open(f"data/C_{n}_coboundary.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_coboundary.json")

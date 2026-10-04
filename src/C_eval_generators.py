import json
import os
from fractions import Fraction

def generate_evaluated(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    gb_params = schema2['inhomogeneous_deformation']['gb_parameters']
    
    # Simple profile: all gb = 1
    assignment = {p: 1 for p in gb_params}
    
    evaluated_constants = []
    
    # We evaluate the gamma structure constants
    # They are given as multiple entries for the same X, Y, Z with different gb_param
    # Let's aggregate them
    agg = {}
    for entry in schema2['inhomogeneous_deformation']['gamma_structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        gb_name = entry['gb_param']
        coeff = Fraction(entry['coeff'])
        val = coeff * assignment[gb_name]
        
        agg.setdefault((X, Y, Z), Fraction(0))
        agg[(X, Y, Z)] += val
        
    for (X, Y, Z), val in agg.items():
        if val != 0:
            evaluated_constants.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff": str(val)
            })
            
    schema3 = {
        "schema_version": "5.0",
        "algebra": schema2["algebra"],
        "evaluated_deformation": {
            "gb_assignment": assignment,
            "evaluated_gamma_constants": evaluated_constants
        }
    }
    
    with open(f"data/C_{n}_evaluated.json", "w") as f:
        json.dump(schema3, f, indent=2)

if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_evaluated(n)
    print("Done generating Schema 3 JSON files")

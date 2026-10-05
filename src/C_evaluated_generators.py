import json
import os
from fractions import Fraction

def format_coeff(c):
    if c.denominator == 1:
        return str(c.numerator)
    return f"{c.numerator}/{c.denominator}"

def evaluate_schema2(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)
        
    gb_matrix = schema2["gb_matrix"]["parameters"]
    
    # Representative assignment: all gb = 1
    gb_assignment = {gb: Fraction(1) for gb in gb_matrix}
    
    evaluated_gamma = []
    
    for sc in schema2["gamma_structure_constants"]:
        X = sc["X"]
        Y = sc["Y"]
        Z = sc["Z"]
        
        # Evaluate sum of gb_terms
        val = Fraction(0)
        for gb, coeff_str in sc["gb_terms"].items():
            if "/" in coeff_str:
                num, den = coeff_str.split("/")
                c = Fraction(int(num), int(den))
            else:
                c = Fraction(int(coeff_str))
            val += c * gb_assignment.get(gb, Fraction(0))
            
        if val != 0:
            evaluated_gamma.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": format_coeff(val),
                "sign_rule": "graded"
            })
            
    schema3 = {
        "schema_version": "5.0",
        "layer": "Schema 3: Evaluated structure",
        "algebra": schema2["algebra"],
        "evaluation_profile": {
            "name": "all_plus_one",
            "assignment": {gb: 1 for gb in gb_matrix}
        },
        "evaluated_gamma_structure_constants": evaluated_gamma
    }
    
    return schema3

if __name__ == "__main__":
    for n in [1, 2, 3]:
        sch = evaluate_schema2(n)
        with open(f"data/C_{n}_evaluated.json", "w") as f:
            json.dump(sch, f, indent=2)
        print(f"Generated data/C_{n}_evaluated.json with {len(sch['evaluated_gamma_structure_constants'])} evaluated brackets.")

import json
import sympy
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_evaluated(n, output_dir="data"):
    s1_path = os.path.join(output_dir, f"C_{n}_structure.json")
    s2_path = os.path.join(output_dir, f"C_{n}_gamma.json")
    
    s1 = load_json(s1_path)
    s2 = load_json(s2_path)
    
    gb_matrix = s2["inhomogeneous_deformation"]["gb_matrix"]
    
    # Define gb symbols and assignment
    gb_symbols = {}
    gb_assignment = {}
    for gb_list in gb_matrix.values():
        for gb_name in gb_list:
            gb_symbols[gb_name] = sympy.Symbol(gb_name)
            gb_assignment[gb_name] = 1  # Option A: all +1
            
    evaluated_gamma = []
    for entry in s2["inhomogeneous_deformation"]["gamma_matrix"]:
        expr = sympy.sympify(entry["gamma_coeff"], locals=gb_symbols)
        val = expr.subs({sym: val for name, sym in gb_symbols.items() for k, val in gb_assignment.items() if k == name})
        if val != 0:
            evaluated_gamma.append({
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "gamma_coeff": str(val)
            })
            
    s3 = {
        "schema_version": "5.0",
        "layer": "3_evaluated",
        "algebra": s1["algebra"],
        "oscillator_generators": s1["oscillator_generators"],
        "oscillator_relations": s1["oscillator_relations"],
        "central_elements": s1.get("central_elements", {}),
        "basis": s1["basis"],
        "parity": s1["parity"],
        "structure_constants": s1["structure_constants"],
        "inhomogeneous_deformation": {
            "exchange_relation": s2["inhomogeneous_deformation"]["exchange_relation"],
            "gb_matrix": gb_matrix,
            "gb_assignment": gb_assignment,
            "profile_name": "Option A: Uniform Positive Profile (All +1)",
            "evaluated_gamma_matrix": evaluated_gamma
        }
    }
    
    out_path = os.path.join(output_dir, f"C_{n}_evaluated.json")
    with open(out_path, "w") as f:
        json.dump(s3, f, indent=2)
    return out_path

if __name__ == "__main__":
    for n in [1, 2, 3]:
        print(f"Generating Schema 3 for C({n+1})...")
        generate_evaluated(n)

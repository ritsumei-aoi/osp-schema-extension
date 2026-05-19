import json
import sympy
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_coboundary(n, output_dir="data"):
    s1_path = os.path.join(output_dir, f"C_{n}_structure.json")
    s1 = load_json(s1_path)
    
    f_map = {}
    f_symbols = {}
    for k in range(1, n + 2):
        name = f"phi_H_{k}"
        f_map[f"H_{k}"] = name
        f_symbols[name] = sympy.Symbol(name)
    f_map["K"] = "phi_K"
    f_symbols["phi_K"] = sympy.Symbol("phi_K")
    
    brackets = {}
    for c in s1["structure_constants"]:
        pair = (c["X"], c["Y"])
        if pair not in brackets:
            brackets[pair] = {}
        brackets[pair][c["Z"]] = c["coeff"]
        
    coboundary_matrix = []
    
    for (X, Y), Z_dict in brackets.items():
        val = 0
        for Z, coeff in Z_dict.items():
            if Z in f_map:
                c_val = sympy.Rational(coeff)
                val += c_val * f_symbols[f_map[Z]]
                
        if val != 0:
            coboundary_matrix.append({
                "X": X,
                "Y": Y,
                "coboundary_coeff": str(val)
            })
            
    s4 = {
        "schema_version": "5.0",
        "layer": "4_coboundary",
        "algebra": s1["algebra"],
        "linear_map_f": {
            "description": "Cartan-Restricted Configuration with K",
            "map": f_map
        },
        "coboundary_matrix": coboundary_matrix
    }
    
    out_path = os.path.join(output_dir, f"C_{n}_coboundary.json")
    with open(out_path, "w") as f:
        json.dump(s4, f, indent=2)
    return out_path

if __name__ == "__main__":
    for n in [1, 2, 3]:
        print(f"Generating Schema 4 for C({n+1})...")
        generate_coboundary(n)

import json
import sympy
import os
from collections import defaultdict

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_coboundary(n, output_dir="data"):
    s1_path = os.path.join(output_dir, f"C_{n}_structure.json")
    s1 = load_json(s1_path)
    
    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    # Include K if not in basis but in central_elements
    if "K" not in basis and "K" in s1.get("central_elements", {}):
        basis.append("K")
        s1["parity"]["K"] = 0
    
    parity = s1["parity"]
    
    # Bracket dict: bracket[X][Y] = {Z: coeff}
    brackets = {X: {Y: {} for Y in basis} for X in basis}
    for c in s1["structure_constants"]:
        brackets[c["X"]][c["Y"]][c["Z"]] = sympy.Rational(c["coeff"])
        
    def get_bracket(X, Y):
        return brackets[X][Y]
        
    # f(Y) = sum_Z phi_{Z, Y} Z
    f_symbols = {}
    f_map = {Y: {} for Y in basis}
    
    for Y in basis:
        for Z in basis:
            if parity[Z] != parity[Y]:  # Odd map: parity must flip
                sym_name = f"phi_{Z}_{Y}"
                sym = sympy.Symbol(sym_name)
                f_symbols[sym_name] = sym
                f_map[Y][Z] = sym
                
    # delta f (X, Y)
    coboundary_matrix = []
    
    for X in basis:
        for Y in basis:
            px = parity[X]
            py = parity[Y]
            
            res_Z = defaultdict(lambda: 0)
            
            # term1: (-1)^{p(X)} [X, f(Y)]
            sign1 = -1 if px == 1 else 1
            for Z_fy, coeff_fy in f_map[Y].items():
                br = get_bracket(X, Z_fy)
                for Z_br, c_br in br.items():
                    res_Z[Z_br] += sign1 * coeff_fy * c_br
                    
            # term2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            exp2 = (px + 1) * py
            sign2 = -1 if exp2 % 2 == 1 else 1
            for Z_fx, coeff_fx in f_map[X].items():
                br = get_bracket(Y, Z_fx)
                for Z_br, c_br in br.items():
                    res_Z[Z_br] -= sign2 * coeff_fx * c_br
                    
            # term3: - f([X, Y])
            br_xy = get_bracket(X, Y)
            for Z_xy, c_xy in br_xy.items():
                for Z_f, coeff_f in f_map[Z_xy].items():
                    res_Z[Z_f] -= c_xy * coeff_f
                    
            for Z, expr in res_Z.items():
                if expr != 0:
                    coboundary_matrix.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coboundary_coeff": str(sympy.expand(expr))
                    })
                    
    s4 = {
        "schema_version": "5.0",
        "layer": "4_coboundary",
        "algebra": s1["algebra"],
        "linear_map_f": {
            "description": "Odd linear map f: g -> g. f(Y) = sum_{p(Z)!=p(Y)} phi_{Z, Y} Z",
        },
        "coboundary_matrix": coboundary_matrix
    }
    
    out_path = os.path.join(output_dir, f"C_{n}_coboundary.json")
    with open(out_path, "w") as f:
        json.dump(s4, f, indent=2)
    return out_path

if __name__ == "__main__":
    for n in [1, 2, 3]:
        print(f"Generating Schema 4 for C({n+1}) with corrected odd map f...")
        generate_coboundary(n)

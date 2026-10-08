import json
from collections import defaultdict
import os

def bracket(X, Y, sc_dict, parity):
    # Returns dictionary of Z -> coeff for [X, Y]
    if (X, Y) in sc_dict:
        return sc_dict[(X, Y)]
    elif (Y, X) in sc_dict:
        res = defaultdict(float)
        sign = -1 if (parity[X] == 1 and parity[Y] == 1) else 1
        for Z, c in sc_dict[(Y, X)].items():
            res[Z] = -c * sign
        return res
    else:
        return defaultdict(float)

def build_schema_4(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    parity = schema["parity"]
    parity["K"] = 0
    sc_list = schema["structure_constants"]
    
    sc_dict = defaultdict(lambda: defaultdict(float))
    for entry in sc_list:
        X, Y, Z, c = entry["X"], entry["Y"], entry["Z"], float(entry["coeff"])
        sc_dict[(X, Y)][Z] += c
        
    basis = schema["basis"]["even"] + schema["basis"]["odd"] + ["K"]
    ordered_basis = schema["basis"]["odd"] + schema["basis"]["even"]
    
    # We only compute for ordered pairs X <= Y in ordered_basis
    coboundary_constants = []
    
    for i, X in enumerate(ordered_basis):
        for j, Y in enumerate(ordered_basis):
            if i > j: continue
            
            pX = parity[X]
            pY = parity[Y]
            
            # coboundary = (-1)^pX [X, f(Y)] - (-1)^((pX+1)pY) [Y, f(X)] - f([X, Y])
            # It's a dict Z -> dict(phi_var -> coeff)
            terms = defaultdict(lambda: defaultdict(float))
            
            # Term 1: (-1)^pX [X, f(Y)]
            # f(Y) = sum_Z phi_{Z, Y} Z
            # [X, f(Y)] = sum_Z phi_{Z, Y} [X, Z] = sum_Z phi_{Z, Y} sum_W c_{XZ}^W W
            sign1 = -1 if pX == 1 else 1
            for Z in basis:
                if parity[Z] == pY: continue # f is odd, phi_{Z,Y} only if p(Z) != p(Y)
                if Z == 'K': continue # we might exclude phi_{K, Y}? Let's include it.
                phi_var = f"phi_{Z}_{Y}"
                xz_br = bracket(X, Z, sc_dict, parity)
                for W, c in xz_br.items():
                    terms[W][phi_var] += sign1 * c
                    
            # Term 2: - (-1)^((pX+1)pY) [Y, f(X)]
            exp = (pX + 1) * pY
            sign2 = -1 if (exp % 2 == 1) else 1
            for Z in basis:
                if parity[Z] == pX: continue
                if Z == 'K': continue
                phi_var = f"phi_{Z}_{X}"
                yz_br = bracket(Y, Z, sc_dict, parity)
                for W, c in yz_br.items():
                    terms[W][phi_var] -= sign2 * c
                    
            # Term 3: - f([X, Y])
            # [X, Y] = sum_Z c_{XY}^Z Z
            # f([X, Y]) = sum_Z c_{XY}^Z f(Z) = sum_Z c_{XY}^Z sum_W phi_{W, Z} W
            xy_br = bracket(X, Y, sc_dict, parity)
            for Z, c_Z in xy_br.items():
                for W in basis:
                    if parity[W] == parity[Z]: continue
                    if W == 'K': continue
                    phi_var = f"phi_{W}_{Z}"
                    terms[W][phi_var] -= c_Z
                    
            # Flatten terms
            for W, phi_dict in terms.items():
                phi_terms = []
                for phi_var, coeff in phi_dict.items():
                    if abs(coeff) > 1e-9:
                        if int(coeff) == coeff: coeff = int(coeff)
                        phi_terms.append({"phi": phi_var, "coeff": str(coeff)})
                if phi_terms:
                    coboundary_constants.append({
                        "X": X,
                        "Y": Y,
                        "Z": W,
                        "coboundary_terms": phi_terms
                    })
                    
    schema4 = {
        "schema_version": "5.0",
        "algebra": schema["algebra"],
        "coboundary_structure": {
            "description": "Coboundary of an odd linear map f",
            "constants": coboundary_constants
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-08"
        }
    }
    
    return schema4

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema_4(n)
        with open(f"data/C_{n}_coboundary.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_coboundary.json")

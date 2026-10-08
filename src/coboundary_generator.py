import json
import fractions

def compute_coboundary(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    parity = schema1["parity"]
    parity["K"] = 0
    
    # B excludes K
    B = schema1["basis"]["even"] + schema1["basis"]["odd"]
    all_Z = B + ["K"]
    
    C = {x: {y: {} for y in all_Z} for x in all_Z}
    for const in schema1["structure_constants"]:
        x, y, z, coeff_str = const["X"], const["Y"], const["Z"], const["coeff"]
        c = fractions.Fraction(coeff_str)
        C[x][y][z] = c
        
        px, py = parity[x], parity[y]
        sign = -1 if (px == 1 and py == 1) else 1
        C[y][x][z] = -sign * c
        
    coboundary_constants = []
    
    for i in range(len(B)):
        x = B[i]
        for j in range(i, len(B)):
            y = B[j]
            
            px, py = parity[x], parity[y]
            res = {}
            
            # Term 1: (-1)^{p(X)} [X, f(Y)]
            for z_i in B:
                if parity[z_i] == py: continue
                phi_param = f"phi_{z_i}_{y}"
                for z, c in C[x][z_i].items():
                    res[(z, phi_param)] = res.get((z, phi_param), fractions.Fraction(0)) + ((-1)**px) * c
                    
            # Term 2: -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            for z_i in B:
                if parity[z_i] == px: continue
                phi_param = f"phi_{z_i}_{x}"
                sign_2 = - ((-1)**((px + 1) * py))
                for z, c in C[y][z_i].items():
                    res[(z, phi_param)] = res.get((z, phi_param), fractions.Fraction(0)) + sign_2 * c
                    
            # Term 3: - f([X, Y])
            for k, c in C[x][y].items():
                if k == "K": continue
                for m in B:
                    if parity[m] == parity[k]: continue
                    phi_param = f"phi_{m}_{k}"
                    res[(m, phi_param)] = res.get((m, phi_param), fractions.Fraction(0)) - c
                    
            # Add to output
            for (z, phi_param), coeff in res.items():
                if coeff != 0:
                    coboundary_constants.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "phi_parameter": phi_param,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })
                    
    schema4 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "coboundary_operator": coboundary_constants
    }
    return schema4

if __name__ == "__main__":
    for n in [1, 2, 3]:
        s4 = compute_coboundary(n)
        with open(f"data/C_{n}_coboundary.json", "w") as f:
            json.dump(s4, f, indent=2)
        print(f"n={n}: Generated {len(s4['coboundary_operator'])} coboundary terms.")

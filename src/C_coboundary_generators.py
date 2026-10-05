import json
import os
from fractions import Fraction

def format_coeff(c):
    if c.denominator == 1:
        return str(c.numerator)
    return f"{c.numerator}/{c.denominator}"

def generate_schema4(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    basis_list = schema1["basis"]["odd"] + schema1["basis"]["even"]
    parity = schema1["parity"]
    
    SC = {x: {y: {} for y in basis_list} for x in basis_list}
    
    for sc in schema1["structure_constants"]:
        X = sc["X"]
        Y = sc["Y"]
        Z = sc["Z"]
        c_str = sc["coeff"]
        if "/" in c_str:
            num, den = c_str.split("/")
            val = Fraction(int(num), int(den))
        else:
            val = Fraction(int(c_str))
            
        SC[X][Y][Z] = val
        
        px = parity[X]
        py = parity[Y]
        sign = -1 if (px == 1 and py == 1) else 1
        SC[Y][X][Z] = -sign * val
        
    f_params = []
    for W in basis_list:
        for V in basis_list:
            if parity[W] != parity[V]:
                f_params.append(f"f_{W}_{V}")
                
    coboundary_sc = []
    
    for i, X in enumerate(basis_list):
        for j in range(i, len(basis_list)):
            Y = basis_list[j]
            
            px = parity[X]
            py = parity[Y]
            
            # For each Z, we collect the coefficients of f_W_V
            # target Z -> f_param -> coeff
            z_accum = {Z: {} for Z in basis_list}
            
            def add_term(target_Z, f_param, coeff):
                if coeff != 0:
                    z_accum[target_Z][f_param] = z_accum[target_Z].get(f_param, Fraction(0)) + coeff
            
            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = sum_W f_{W}_{Y} W  (where p(W) != p(Y))
            for W in basis_list:
                if parity[W] != py:
                    f_param = f"f_{W}_{Y}"
                    # [X, W] = sum_Z SC[X][W][Z] Z
                    for Z, c_XW in SC[X][W].items():
                        c = ((-1)**px) * c_XW
                        add_term(Z, f_param, c)
                        
            # Term 2: -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            # f(X) = sum_W f_{W}_{X} W (where p(W) != p(X))
            sign2 = - ((-1)**((px + 1) * py))
            for W in basis_list:
                if parity[W] != px:
                    f_param = f"f_{W}_{X}"
                    # [Y, W] = sum_Z SC[Y][W][Z] Z
                    for Z, c_YW in SC[Y][W].items():
                        c = sign2 * c_YW
                        add_term(Z, f_param, c)
                        
            # Term 3: -f([X, Y])
            # [X, Y] = sum_W SC[X][Y][W] W
            for W, c_XY in SC[X][Y].items():
                # f(W) = sum_Z f_{Z}_{W} Z (where p(Z) != p(W))
                for Z in basis_list:
                    if parity[Z] != parity[W]:
                        f_param = f"f_{Z}_{W}"
                        c = -c_XY
                        add_term(Z, f_param, c)
                        
            for Z in basis_list:
                f_terms = {p: format_coeff(c) for p, c in z_accum[Z].items() if c != 0}
                if f_terms:
                    coboundary_sc.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "f_terms": f_terms,
                        "sign_rule": "graded"
                    })
                    
    schema4 = {
        "schema_version": "5.0",
        "layer": "Schema 4: Coboundary structure",
        "algebra": schema1["algebra"],
        "f_map": {
            "parameters": f_params,
            "description": "Odd linear map f: g -> g. Parameters f_{out}_{in}"
        },
        "coboundary_structure_constants": coboundary_sc
    }
    
    return schema4

if __name__ == "__main__":
    for n in [1, 2, 3]:
        sch = generate_schema4(n)
        with open(f"data/C_{n}_coboundary.json", "w") as f:
            json.dump(sch, f, indent=2)
        print(f"Generated data/C_{n}_coboundary.json with {len(sch['coboundary_structure_constants'])} coboundary brackets.")

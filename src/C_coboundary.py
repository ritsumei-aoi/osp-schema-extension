import json
import sys
import os
from fractions import Fraction
from collections import defaultdict
from itertools import product

def generate_coboundary(n):
    with open(f"data/C_{n}_structure.json") as f:
        schema1 = json.load(f)
        
    parity = schema1["parity"]
    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    
    sc = defaultdict(Fraction)
    for entry in schema1["structure_constants"]:
        X, Y, Z, coeff = entry["X"], entry["Y"], entry["Z"], Fraction(entry["coeff"])
        sc[(X, Y, Z)] = coeff
        
    def get_bracket_coeff(X, Y, Z):
        return sc.get((X, Y, Z), Fraction(0))

    coboundary = []
    
    # delta f(X, Y) = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X,Y])
    for X in basis:
        for Y in basis:
            pX = parity[X]
            pY = parity[Y]
            
            z_expansion = defaultdict(lambda: defaultdict(Fraction))
            
            # 1. (-1)^{pX} [X, f(Y)]
            # f(Y) = sum_K phi_{K, Y} K, where pK != pY
            for K in basis:
                if parity[K] == parity[Y]: continue
                for Z in basis:
                    c = get_bracket_coeff(X, K, Z)
                    if c != 0:
                        sign = -1 if pX == 1 else 1
                        z_expansion[Z][f"phi_{K}_{Y}"] += sign * c
                        
            # 2. - (-1)^{(pX+1)pY} [Y, f(X)]
            # f(X) = sum_L phi_{L, X} L, where pL != pX
            for L in basis:
                if parity[L] == parity[X]: continue
                for Z in basis:
                    c = get_bracket_coeff(Y, L, Z)
                    if c != 0:
                        sign = -1 if ((pX + 1) * pY) % 2 == 1 else 1
                        z_expansion[Z][f"phi_{L}_{X}"] -= sign * c
                        
            # 3. - f([X, Y])
            # [X, Y] = sum_W c_W W -> f(W) = sum_M phi_{M, W} M
            for W in basis:
                c = get_bracket_coeff(X, Y, W)
                if c != 0:
                    for M in basis:
                        if parity[M] == parity[W]: continue
                        # Z is M in this term
                        z_expansion[M][f"phi_{M}_{W}"] -= c
                        
            # Form expansion list
            expansion_list = []
            for Z in basis:
                term_dict = z_expansion[Z]
                for phi_param, val in term_dict.items():
                    if val != 0:
                        expansion_list.append({
                            "Z": Z,
                            "phi_param": phi_param,
                            "coeff": str(val)
                        })
            
            if expansion_list:
                coboundary.append({
                    "X": X,
                    "Y": Y,
                    "coboundary_expansion": expansion_list
                })
                
    schema4 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "f_map": {
            "description": "Odd linear map parameterized by phi_{K}_{X} where p(K) != p(X)"
        },
        "coboundary_structure": coboundary,
        "metadata": {
            "generated_by": "C_coboundary.py"
        }
    }
    return schema4

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_coboundary.json", "w") as f:
            json.dump(generate_coboundary(n), f, indent=2)
    print("Generated Schema 4 JSONs in data/")

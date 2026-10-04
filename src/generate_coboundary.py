import json
import sympy as sp
from collections import defaultdict
import fractions

def generate_coboundary(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    parity = schema['parity']
    sc_list = schema['structure_constants']
    all_gen = schema['basis']['even'] + schema['basis']['odd']
    
    # Pre-parse structure constants
    sc = defaultdict(lambda: defaultdict(lambda: defaultdict(fractions.Fraction)))
    for entry in sc_list:
        X, Y, Z, c_str = entry['X'], entry['Y'], entry['Z'], entry['coeff']
        c = fractions.Fraction(c_str)
        sc[X][Y][Z] += c
        
    phi_params = []
    for source in all_gen:
        for target in all_gen:
            if parity[source] != parity[target]:
                phi_params.append(f"phi_{target}__{source}")
                
    coboundary_out = []
    
    for i, X in enumerate(all_gen):
        for j in range(len(all_gen)): # all pairs
            Y = all_gen[j]
            pX, pY = parity[X], parity[Y]
            
            # We want to compute delta_f(X, Y) which is a dict of Z -> sympy expr
            # delta_f(X,Y) = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X,Y])
            
            coeff_Z = defaultdict(int)
            
            # Term 1: (-1)^{pX} [X, f(Y)]
            sign1 = -1 if pX == 1 else 1
            for K in all_gen:
                if parity[K] != pY:
                    phi_KY = sp.Symbol(f"phi_{K}__{Y}")
                    # [X, K] = sum_Z sc[X][K][Z] * Z
                    for Z, c in sc[X][K].items():
                        coeff_Z[Z] += sign1 * c * phi_KY
                        
            # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
            power2 = (pX + 1) * pY
            sign2 = -1 if power2 % 2 == 1 else 1
            sign2 = -sign2 # from the minus sign in the formula
            for K in all_gen:
                if parity[K] != pX:
                    phi_KX = sp.Symbol(f"phi_{K}__{X}")
                    for Z, c in sc[Y][K].items():
                        coeff_Z[Z] += sign2 * c * phi_KX
                        
            # Term 3: - f([X,Y])
            # [X,Y] = sum_K sc[X][Y][K] * K
            # f([X,Y]) = sum_K sc[X][Y][K] f(K) = sum_K sc[X][Y][K] sum_Z phi_{Z, K} * Z
            for K, c_K in sc[X][Y].items():
                for Z in all_gen:
                    if parity[Z] != parity[K]:
                        phi_ZK = sp.Symbol(f"phi_{Z}__{K}")
                        coeff_Z[Z] -= c_K * phi_ZK
                        
            # Store non-zero coefficients
            for Z, expr in coeff_Z.items():
                expr = sp.simplify(expr)
                if expr != 0:
                    coboundary_out.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "coboundary_coeff": str(expr)
                    })
                    
    schema4 = {
        "schema_version": "5.0",
        "algebra": schema['algebra'],
        "f_map_parameters": phi_params,
        "coboundary_deformation": coboundary_out
    }
    
    with open(f"data/C_{n}_coboundary.json", "w") as f:
        json.dump(schema4, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        generate_coboundary(n)
        print(f"Generated data/C_{n}_coboundary.json")

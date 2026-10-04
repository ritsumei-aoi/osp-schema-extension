import json
import os
from fractions import Fraction

def generate_coboundary(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    all_gens = schema1['basis']['even'] + schema1['basis']['odd']
    parity = schema1['parity']
    
    # sc[X][Y] = {Z: coeff}
    sc = {x: {y: {} for y in all_gens} for x in all_gens}
    for term in schema1['structure_constants']:
        X, Y, Z = term['X'], term['Y'], term['Z']
        sc[X][Y][Z] = Fraction(term['coeff'])
        
    def bracket(A, B):
        return sc[A][B]
        
    coboundary_constants = []
    
    # We want to compute (\delta f)(X, Y)
    # df(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # f(A) = \sum_W phi_{W, A} W  where p(W) != p(A)
    #
    # So df(X, Y) is a sum over W of terms involving phi_{W, Y}, phi_{W, X}, and phi_{Z, [X,Y]}.
    
    # We will accumulate the coefficient of each phi_{A, B} parameter on each basis vector Z.
    for X in all_gens:
        for Y in all_gens:
            # We will store a dict: Z -> dict of phi_param -> coeff
            res = {}
            def add_term(Z, phi_param, coeff):
                if coeff == 0: return
                res.setdefault(Z, {})[phi_param] = res.get(Z, {}).get(phi_param, Fraction(0)) + coeff
                
            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = \sum_W phi_{W, Y} W (with p(W) != p(Y))
            sign1 = -1 if parity[X] == 1 else 1
            for W in all_gens:
                if parity[W] == parity[Y]: continue
                phi_param = f"phi_{W}_{Y}"
                # [X, W]
                xw = bracket(X, W)
                for Z, c in xw.items():
                    add_term(Z, phi_param, sign1 * c)
                    
            # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            # f(X) = \sum_W phi_{W, X} W (with p(W) != p(X))
            pow2 = (parity[X] + 1) * parity[Y]
            sign2 = -1 if pow2 % 2 == 1 else 1
            for W in all_gens:
                if parity[W] == parity[X]: continue
                phi_param = f"phi_{W}_{X}"
                # [Y, W]
                yw = bracket(Y, W)
                for Z, c in yw.items():
                    add_term(Z, phi_param, -sign2 * c)
                    
            # Term 3: - f([X, Y])
            # [X, Y] = \sum_W c_{X, Y}^W W
            # f(W) = \sum_Z phi_{Z, W} Z (with p(Z) != p(W))
            xy = bracket(X, Y)
            for W, c_W in xy.items():
                for Z in all_gens:
                    if parity[Z] == parity[W]: continue
                    phi_param = f"phi_{Z}_{W}"
                    add_term(Z, phi_param, -c_W)
                    
            for Z, phi_dict in res.items():
                for phi_param, coeff in phi_dict.items():
                    if coeff != 0:
                        coboundary_constants.append({
                            "X": X, "Y": Y, "Z": Z,
                            "phi_param": phi_param,
                            "coeff": str(coeff)
                        })

    # Collect list of all phi parameters
    phi_parameters = []
    for A in all_gens:
        for B in all_gens:
            if parity[A] != parity[B]:
                phi_parameters.append(f"phi_{A}_{B}")

    schema4 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "coboundary_structure": {
            "phi_parameters": phi_parameters,
            "coboundary_constants": coboundary_constants
        }
    }
    
    with open(f"data/C_{n}_coboundary.json", "w") as f:
        json.dump(schema4, f, indent=2)

if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_coboundary(n)
    print("Done generating Schema 4 JSON files")

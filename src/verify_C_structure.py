import json
import sys
from fractions import Fraction
from itertools import product
from collections import defaultdict

def verify(n):
    with open(f"data/C_{n}_structure.json") as f:
        data = json.load(f)
    
    parity = data["parity"]
    basis = data["basis"]["even"] + data["basis"]["odd"]
    
    sc = defaultdict(Fraction)
    for entry in data["structure_constants"]:
        X, Y, Z, coeff = entry["X"], entry["Y"], entry["Z"], Fraction(entry["coeff"])
        sc[(X, Y, Z)] = coeff
        
    def get_bracket(X, Y):
        res = defaultdict(Fraction)
        for Z in basis:
            if (X, Y, Z) in sc:
                res[Z] += sc[(X, Y, Z)]
        return res
        
    # Check antisymmetry
    anti_sym_passed = True
    for X, Y in product(basis, repeat=2):
        b1 = get_bracket(X, Y)
        b2 = get_bracket(Y, X)
        sign = -1 if (parity[X] == 1 and parity[Y] == 1) else 1
        
        for Z in basis:
            if b1[Z] != -sign * b2[Z]:
                print(f"Anti-symmetry failed for {X}, {Y}")
                anti_sym_passed = False
                break
        if not anti_sym_passed: break
        
    # Check Jacobi
    jacobi_passed = True
    for X, Y, Z in product(basis, repeat=3):
        sign1 = -1 if (parity[X] == 1 and parity[Z] == 1) else 1
        term1 = defaultdict(Fraction)
        for W, c1 in get_bracket(Y, Z).items():
            for V, c2 in get_bracket(X, W).items():
                term1[V] += sign1 * c1 * c2
                
        sign2 = -1 if (parity[Y] == 1 and parity[X] == 1) else 1
        term2 = defaultdict(Fraction)
        for W, c1 in get_bracket(Z, X).items():
            for V, c2 in get_bracket(Y, W).items():
                term2[V] += sign2 * c1 * c2
                
        sign3 = -1 if (parity[Z] == 1 and parity[Y] == 1) else 1
        term3 = defaultdict(Fraction)
        for W, c1 in get_bracket(X, Y).items():
            for V, c2 in get_bracket(Z, W).items():
                term3[V] += sign3 * c1 * c2
                
        for V in basis:
            if term1[V] + term2[V] + term3[V] != 0:
                print(f"Jacobi failed for {X}, {Y}, {Z} -> {V}: {term1[V] + term2[V] + term3[V]}")
                jacobi_passed = False
                break
        if not jacobi_passed: break
        
    return anti_sym_passed and jacobi_passed

if __name__ == "__main__":
    all_passed = True
    for n in [1, 2, 3]:
        if verify(n):
            print(f"n={n}: Verification PASSED")
        else:
            print(f"n={n}: Verification FAILED")
            all_passed = False
    if not all_passed:
        sys.exit(1)

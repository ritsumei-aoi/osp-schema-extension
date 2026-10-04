import json
import sys
from fractions import Fraction
from collections import defaultdict
from itertools import product

def verify_gamma(n):
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)
        
    parity = s1["parity"]
    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    
    gamma = defaultdict(lambda: defaultdict(Fraction))
    for entry in s2["gamma_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["gamma_expansion"]:
            Z, gb, c = term["Z"], term["gb_param"], Fraction(term["coeff"])
            gamma[(X, Y)][(Z, gb)] += c
            
    passed = True
    for X, Y in product(basis, repeat=2):
        sign = -1 if (parity[X] == 1 and parity[Y] == 1) else 1
        g1 = gamma[(X, Y)]
        g2 = gamma[(Y, X)]
        all_keys = set(g1.keys()) | set(g2.keys())
        for k in all_keys:
            if g1[k] != -sign * g2[k]:
                print(f"Gamma anti-symmetry failed for {X}, {Y} at {k}: {g1[k]} vs {g2[k]}")
                passed = False
                break
        if not passed: break
    return passed

if __name__ == "__main__":
    all_passed = True
    for n in [1, 2, 3]:
        if verify_gamma(n):
            print(f"n={n}: Gamma verification PASSED")
        else:
            print(f"n={n}: Gamma verification FAILED")
            all_passed = False
    if not all_passed: sys.exit(1)

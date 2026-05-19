import json
import os
from fractions import Fraction
from collections import defaultdict

def check_graded_antisymmetry(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Load parity from original structure or use a heuristic
    # (Schema 4 contains the algebra field, but parity isn't always embedded)
    # We'll load the corresponding structure file
    n = data['algebra']['n']
    with open(f"data/C_{n}_structure.json", 'r') as f:
        s1 = json.load(f)
    parity = s1['parity']
    if "K" not in parity: parity["K"] = 0

    # Store coboundary components: (X, Y) -> {Z: coeff}
    cb = defaultdict(dict)
    for entry in data['coboundary_structure']:
        cb[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

    all_basis = s1['basis']['odd'] + s1['basis']['even'] + ["K"]

    for X in all_basis:
        for Y in all_basis:
            pX, pY = parity[X], parity[Y]
            lhs = cb.get((X, Y), {})
            rhs = cb.get((Y, X), {})
            
            # (delta f)(X, Y) = -(-1)^{pX pY} (delta f)(Y, X)
            sign = -1 if (pX == 1 and pY == 1) else 1
            
            check = defaultdict(Fraction)
            for Z, val in lhs.items(): check[Z] += val
            for Z, val in rhs.items(): check[Z] += val * sign
            
            for Z, val in check.items():
                if val != 0:
                    print(f"FAILED: Graded anti-symmetry for ({X}, {Y}) in {file_path}")
                    return False
    return True

if __name__ == "__main__":
    for n in [1, 2, 3]:
        file = f"data/C_{n}_coboundary.json"
        if os.path.exists(file):
            if check_graded_antisymmetry(file):
                print(f"PASSED: Graded anti-symmetry for {file}")
            else:
                exit(1)

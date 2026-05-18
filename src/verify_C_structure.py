import json
import os
from fractions import Fraction
from collections import defaultdict

def verify_structure(file_path):
    print(f"Verifying {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)

    basis_even = data['basis']['even']
    basis_odd = data['basis']['odd']
    parity = data['parity']
    
    # K is also in the basis for structure constants but not in the basis list
    all_basis = basis_odd + basis_even
    if "K" not in parity:
        parity["K"] = 0
    
    # Store structure constants in a map: (X, Y) -> {Z: coeff}
    # [X, Y} = sum_Z C(X, Y, Z) * Z
    sc = defaultdict(dict)
    for entry in data['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        coeff = Fraction(entry['coeff'])
        sc[(X, Y)][Z] = coeff
    
    # Define the graded bracket [X, Y}
    def get_bracket(X, Y):
        # Graded anti-symmetry: [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
        # The JSON only stores structure constants for i <= j (often)
        # or just as provided. Let's be robust.
        if (X, Y) in sc:
            return sc[(X, Y)]
        
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX == 1 and pY == 1) else 1
        
        if (Y, X) in sc:
            result = {}
            for Z, val in sc[(Y, X)].items():
                result[Z] = -val * sign
            return result
        
        return {}

    def add_scaled(target, source, scale):
        for Z, val in source.items():
            target[Z] += val * scale
            if target[Z] == 0:
                del target[Z]

    # 1. Check Graded Anti-symmetry
    # [X, Y} + (-1)^{p(X)p(Y)} [Y, X} = 0
    print("Checking graded anti-symmetry...")
    for X in all_basis:
        for Y in all_basis:
            pX, pY = parity[X], parity[Y]
            lhs = get_bracket(X, Y)
            rhs = get_bracket(Y, X)
            
            sign = -1 if (pX == 1 and pY == 1) else 1
            
            check = defaultdict(Fraction)
            for Z, val in lhs.items(): check[Z] += val
            for Z, val in rhs.items(): check[Z] += val * sign
            
            for Z, val in check.items():
                if val != 0:
                    print(f"Anti-symmetry FAIL: [ {X}, {Y} ] != -(-1)^{{p(X)p(Y)}} [ {Y}, {X} ]")
                    print(f"  LHS: {lhs}")
                    print(f"  RHS scaled: { {k: v*sign for k, v in rhs.items()} }")
                    return False
    print("Anti-symmetry PASS.")

    # 2. Check Super Jacobi Identity
    # (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
    print("Checking Super Jacobi identity...")
    count = 0
    total = len(all_basis) ** 3
    for X in all_basis:
        for Y in all_basis:
            for Z in all_basis:
                pX, pY, pZ = parity[X], parity[Y], parity[Z]
                
                # Term 1: (-1)^{p(X)p(Z)} [X, [Y, Z}}
                s1 = -1 if (pX == 1 and pZ == 1) else 1
                bYZ = get_bracket(Y, Z)
                t1 = defaultdict(Fraction)
                for W, coeff in bYZ.items():
                    add_scaled(t1, get_bracket(X, W), coeff * s1)
                
                # Term 2: (-1)^{p(Y)p(X)} [Y, [Z, X}}
                s2 = -1 if (pY == 1 and pX == 1) else 1
                bZX = get_bracket(Z, X)
                t2 = defaultdict(Fraction)
                for W, coeff in bZX.items():
                    add_scaled(t2, get_bracket(Y, W), coeff * s2)
                
                # Term 3: (-1)^{p(Z)p(Y)} [Z, [X, Y}}
                s3 = -1 if (pZ == 1 and pY == 1) else 1
                bXY = get_bracket(X, Y)
                t3 = defaultdict(Fraction)
                for W, coeff in bXY.items():
                    add_scaled(t3, get_bracket(Z, W), coeff * s3)
                
                # Total
                final = defaultdict(Fraction)
                for W, val in t1.items(): final[W] += val
                for W, val in t2.items(): final[W] += val
                for W, val in t3.items(): final[W] += val
                
                for W, val in list(final.items()):
                    if abs(val) < 1e-10: del final[W]
                
                if final:
                    print(f"Jacobi FAIL for ({X}, {Y}, {Z})")
                    print(f"  Residual: {dict(final)}")
                    return False
                
                count += 1
                if count % 1000 == 0:
                    print(f"  Progress: {count}/{total}")
                    
    print("Super Jacobi PASS.")
    return True

if __name__ == "__main__":
    for n in [1, 2, 3]:
        file = f"data/C_{n}_structure.json"
        if os.path.exists(file):
            if not verify_structure(file):
                exit(1)
        else:
            print(f"File {file} not found.")

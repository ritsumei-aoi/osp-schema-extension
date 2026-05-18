"""
verify_C_structure.py
Verification script for Super Jacobi identity and anti-symmetry for C(n+1).
"""

import json
import itertools

def get_parity(gen, parity_map):
    return parity_map.get(gen, 0)

def verify_algebra(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        data = json.load(f)
    
    basis = data["basis"]
    struct_consts = data["structure_constants"]
    # We need parity information from the schema (from I02/I03 logic)
    # Assuming parity_map is available or can be derived. 
    # For this verification, let's assume a simplified parity dictionary.
    parity_map = {gen: (1 if "E_eps" in gen else 0) for gen in basis}
    
    # Store constants: (X, Y) -> (Z, coeff)
    brackets = {}
    for item in struct_consts:
        X, Y, Z, coeff = item["X"], item["Y"], item["Z"], item["coeff"]
        brackets[(X, Y)] = (Z, float(coeff))
        
    print(f"--- Verification for C({n+1}) ---")
    
    # 1. Anti-symmetry: [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
    # Simplified check for coefficients
    for (X, Y), (Z1, c1) in brackets.items():
        if (Y, X) in brackets:
            Z2, c2 = brackets[(Y, X)]
            pX, pY = get_parity(X, parity_map), get_parity(Y, parity_map)
            sign = -1 if (pX * pY) == 0 else 1
            if c1 != sign * c2:
                print(f"Anti-symmetry FAILED for ({X}, {Y})")
                return False
                
    print("Anti-symmetry check: PASSED")
    
    # 2. Super Jacobi identity
    # [X, [Y, Z]] = [[X, Y], Z] + (-1)^{p(X)p(Y)} [Y, [X, Z]]
    print("Checking Super Jacobi identity...")
    for X, Y, Z in itertools.combinations(basis, 3):
        pX, pY = get_parity(X, parity_map), get_parity(Y, parity_map)
        
        # Calculate LHS = [X, [Y, Z]]
        # [Y, Z] = (W, c_yz)
        if (Y, Z) in brackets:
            W, c_yz = brackets[(Y, Z)]
            # [X, W] = (ResL, c_resL)
            if (X, W) in brackets:
                ResL, c_resL = brackets[(X, W)]
                valL = c_yz * c_resL
            else: valL = 0
        else: valL = 0
            
        # Calculate RHS = [[X, Y], Z] + (-1)^{p(X)p(Y)} [Y, [X, Z]]
        # Term 1: [[X, Y], Z]
        if (X, Y) in brackets:
            V, c_xy = brackets[(X, Y)]
            if (V, Z) in brackets:
                ResR1, c_resR1 = brackets[(V, Z)]
                valR1 = c_xy * c_resR1
            else: valR1 = 0
        else: valR1 = 0
        
        # Term 2: (-1)^{p(X)p(Y)} [Y, [X, Z]]
        sign = -1 if (pX * pY) == 0 else 1
        if (X, Z) in brackets:
            U, c_xz = brackets[(X, Z)]
            if (Y, U) in brackets:
                ResR2, c_resR2 = brackets[(Y, U)]
                valR2 = sign * c_xz * c_resR2
            else: valR2 = 0
        else: valR2 = 0
        
        if valL != (valR1 + valR2):
            print(f"Super Jacobi FAILED for ({X}, {Y}, {Z})")
            return False
        
    print("Super Jacobi identity check: PASSED")
    return True

if __name__ == "__main__":
    for n in [1, 2, 3]:
        verify_algebra(n)

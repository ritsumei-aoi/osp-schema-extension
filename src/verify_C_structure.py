import json
from collections import defaultdict

def verify(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    parity = schema["parity"]
    parity["K"] = 0
    sc_list = schema["structure_constants"]
    
    # Build a lookup table: (X, Y) -> dict(Z -> coeff)
    C = defaultdict(lambda: defaultdict(int))
    for entry in sc_list:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = float(entry["coeff"])
        C[(X, Y)][Z] += c
        
    all_basis = schema["basis"]["even"] + schema["basis"]["odd"] + ["K"]
    
    # Complete the structure constants using graded anti-symmetry
    # [Y, X} = -(-1)^{p(X)p(Y)} [X, Y}
    for X in all_basis:
        for Y in all_basis:
            if (Y, X) not in C and (X, Y) in C:
                pX = parity[X]
                pY = parity[Y]
                sign = -1 if (pX == 1 and pY == 1) else 1
                for Z, c in C[(X, Y)].items():
                    C[(Y, X)][Z] = -c * sign
            elif (X, Y) not in C:
                pass # remains empty dict

    # Verify anti-symmetry
    for X in all_basis:
        for Y in all_basis:
            pX = parity[X]
            pY = parity[Y]
            sign = -1 if (pX == 1 and pY == 1) else 1
            # Check [X, Y} + sign * [Y, X} = 0
            for Z in set(C[(X,Y)].keys()).union(C[(Y,X)].keys()):
                val = C[(X,Y)][Z] + sign * C[(Y,X)][Z]
                if abs(val) > 1e-9:
                    print(f"Anti-symmetry failed for {X}, {Y} -> {Z}: {val}")
                    return False
                    
    # Verify Super Jacobi Identity
    # (-1)^{p(X)p(Z)} [X, [Y, Z]} + cyclic = 0
    for X in all_basis:
        for Y in all_basis:
            for Z in all_basis:
                pX, pY, pZ = parity[X], parity[Y], parity[Z]
                
                # sum of (-1)^{p(X)p(Z)} [X, [Y, Z]} + cyclic
                jacobi = defaultdict(float)
                
                def add_nested(A, B, C_op, pA, pC):
                    sign = -1 if (pA == 1 and pC == 1) else 1
                    inner = C[(B, C_op)]
                    for W, coeff1 in inner.items():
                        outer = C[(A, W)]
                        for R, coeff2 in outer.items():
                            jacobi[R] += sign * coeff1 * coeff2
                            
                add_nested(X, Y, Z, pX, pZ)
                add_nested(Y, Z, X, pY, pX)
                add_nested(Z, X, Y, pZ, pY)
                
                for R, val in jacobi.items():
                    if abs(val) > 1e-9:
                        print(f"Jacobi failed for {X}, {Y}, {Z} -> {R}: {val}")
                        return False
                        
    print(f"Verification passed for n={n}")
    return True

if __name__ == "__main__":
    all_passed = True
    for n in [1, 2, 3]:
        if not verify(n):
            all_passed = False
            
    if all_passed:
        print("ALL VERIFICATIONS PASSED.")
    else:
        print("VERIFICATION FAILED.")
        exit(1)

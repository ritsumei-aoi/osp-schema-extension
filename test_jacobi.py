import sys
from calc import get_basis, bracket, parse_B, parse_F

def parity(X):
    return 0 if X.startswith('B') or X == 'H' else 1

def check_jacobi():
    n = 1
    even, odd = get_basis(n)
    basis = even + odd
    
    # We want to check [X, [Y, Z]] - [[X, Y], Z] - (-1)^{pX*pY} [Y, [X, Z]] == 0
    # or equivalently [X, [Y, Z]] = [[X, Y], Z] + (-1)^{pX*pY} [Y, [X, Z]]
    
    fails = 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                # compute [Y, Z]
                br_YZ = bracket(Y, Z, n)
                # compute [X, [Y, Z]]
                lhs = {}
                for k, v in br_YZ.items():
                    br = bracket(X, k, n)
                    for k2, v2 in br.items():
                        lhs[k2] = lhs.get(k2, 0) + v * v2
                        
                # compute [[X, Y], Z]
                br_XY = bracket(X, Y, n)
                term1 = {}
                for k, v in br_XY.items():
                    br = bracket(k, Z, n)
                    for k2, v2 in br.items():
                        term1[k2] = term1.get(k2, 0) + v * v2
                        
                # compute (-1)^{pX*pY} [Y, [X, Z]]
                br_XZ = bracket(X, Z, n)
                term2 = {}
                sign = 1 if (parity(X) * parity(Y)) % 2 == 0 else -1
                for k, v in br_XZ.items():
                    br = bracket(Y, k, n)
                    for k2, v2 in br.items():
                        term2[k2] = term2.get(k2, 0) + sign * v * v2
                        
                # Check lhs == term1 + term2
                rhs = {}
                for k, v in term1.items(): rhs[k] = rhs.get(k, 0) + v
                for k, v in term2.items(): rhs[k] = rhs.get(k, 0) + v
                
                # Compare
                diff = {}
                for k in set(lhs.keys()).union(set(rhs.keys())):
                    d = lhs.get(k, 0) - rhs.get(k, 0)
                    if d != 0:
                        diff[k] = d
                if diff:
                    print(f"Jacobi failed for {X}, {Y}, {Z}: diff = {diff}")
                    fails += 1
                    if fails > 10:
                        return
                        
    if fails == 0:
        print("Jacobi identity satisfied!")

if __name__ == "__main__":
    check_jacobi()

import json
import sympy as sp
import sys

def main():
    with open('algebra.py', 'r') as f:
        code = f.read()

    # We will modify algebra.py to dump json at the end
    export_code = """
    # Dump structure for n=1
    n = 1
    even_basis = [("A",)]
    for j in range(1, n+1):
        for k in range(j, n+1):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    if j == k and s1 < s2: continue
                    even_basis.append(("B", j, s1, k, s2))
                    
    odd_basis = []
    for sigma in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                odd_basis.append(("O", sigma, j, s))
                
    basis = even_basis + odd_basis
    
    struct_data = {
        "basis": basis,
        "brackets": {},
        "gamma": {}
    }
    
    # We will compute brackets and gamma
    # To do this cleanly, we can just grab them from the execution scope if we ran it,
    # or just use a small script
"""
    with open('dump.py', 'w') as f:
        f.write(export_code)

if __name__ == "__main__":
    main()

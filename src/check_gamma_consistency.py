import json
import os

def check_consistency(n):
    s1_path = f"data/C_{n}_structure.json"
    s2_path = f"data/C_{n}_gamma.json"
    
    if not os.path.exists(s1_path) or not os.path.exists(s2_path):
        print(f"Files for n={n} not found.")
        return False
        
    with open(s1_path, 'r') as f:
        s1 = json.load(f)
    with open(s2_path, 'r') as f:
        s2 = json.load(f)
        
    # 1. Algebra check
    if s1['algebra']['family'] != s2['algebra']['family']:
        print(f"n={n}: Family mismatch")
        return False
    if s1['algebra']['n'] != s2['algebra']['n']:
        print(f"n={n}: Rank mismatch")
        return False
        
    # 2. Basis check
    basis = set(s1['basis']['even'] + s1['basis']['odd'] + ["K"])
    for entry in s2['inhomogeneous_deformation']['gamma_structure']:
        for key in ['X', 'Y', 'Z']:
            if entry[key] not in basis:
                print(f"n={n}: Generator {entry[key]} not in Schema 1 basis")
                return False
                
    # 3. Parameters check
    params = set(s2['inhomogeneous_deformation']['parameters'])
    for entry in s2['inhomogeneous_deformation']['gamma_structure']:
        if entry['parameter'] not in params:
            print(f"n={n}: Parameter {entry['parameter']} not in parameters list")
            return False
            
    print(f"n={n}: Consistency check PASSED")
    return True

if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_consistency(n)

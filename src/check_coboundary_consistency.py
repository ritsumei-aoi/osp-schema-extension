import json
import os

def check_coboundary_consistency(n):
    s1_path = f"data/C_{n}_structure.json"
    s4_path = f"data/C_{n}_coboundary_cartan.json"
    
    if not os.path.exists(s1_path) or not os.path.exists(s4_path):
        print(f"Files for n={n} not found.")
        return False
        
    with open(s1_path, 'r') as f:
        s1 = json.load(f)
    with open(s4_path, 'r') as f:
        s4 = json.load(f)
        
    # 1. Algebra check
    if s1['algebra']['cartan_type'] != s4['algebra']['cartan_type']:
        print(f"n={n}: Cartan type mismatch")
        return False
        
    # 2. Map check
    basis = set(s1['basis']['even'] + s1['basis']['odd'] + ["K"])
    for gen in s4['map_definition']:
        if gen not in basis:
            print(f"n={n}: Map generator {gen} not in Schema 1 basis")
            return False
            
    # 3. Structure check
    for entry in s4['coboundary_structure']:
        if entry['X'] not in basis or entry['Y'] not in basis:
            print(f"n={n}: Pair ({entry['X']}, {entry['Y']}) not in Schema 1 basis")
            return False
        if entry['Z'] != "K":
            print(f"n={n}: Resulting generator must be K (identity) for scalar results")
            return False
            
    print(f"n={n}: Coboundary consistency check PASSED")
    return True

if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_coboundary_consistency(n)

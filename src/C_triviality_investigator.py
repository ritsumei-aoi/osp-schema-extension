import json
import os
from fractions import Fraction
from collections import defaultdict

def compare_structures(n):
    eval_path = f"data/C_{n}_evaluated_pos.json"
    cob_path = f"data/C_{n}_coboundary.json"
    
    if not os.path.exists(eval_path) or not os.path.exists(cob_path):
        print(f"Files for n={n} not found.")
        return

    with open(eval_path, 'r') as f:
        layer3 = json.load(f)
    with open(cob_path, 'r') as f:
        layer4 = json.load(f)

    # Map: (X, Y) -> {Z: coeff}
    gamma_eval = defaultdict(dict)
    for entry in layer3['evaluated_gamma_structure']:
        gamma_eval[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

    gamma_cob = defaultdict(dict)
    for entry in layer4['coboundary_structure']:
        gamma_cob[(entry['X'], entry['Y'])][entry['Z']] = Fraction(entry['coeff'])

    all_pairs = set(gamma_eval.keys()) | set(gamma_cob.keys())
    
    print(f"\n--- Triviality Investigation for C({n+1}) ---")
    
    matches = 0
    mismatches = 0
    
    for X, Y in sorted(all_pairs):
        eval_dict = gamma_eval[(X, Y)]
        cob_dict = gamma_cob[(X, Y)]
        
        # Check if they match or are proportional
        if eval_dict == cob_dict:
            matches += 1
        else:
            mismatches += 1
            if mismatches <= 5: # Limit output
                print(f"Mismatch for [{X}, {Y}]:")
                print(f"  Layer 3: {dict(eval_dict)}")
                print(f"  Layer 4: {dict(cob_dict)}")

    print(f"\nSummary for n={n}:")
    print(f"  Total Pairs with deformation: {len(all_pairs)}")
    print(f"  Exact matches with chosen f: {matches}")
    print(f"  Mismatches with chosen f: {mismatches}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        compare_structures(n)

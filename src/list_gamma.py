import json
from fractions import Fraction

with open('data/C_1_evaluated_pos.json', 'r') as f:
    data = json.load(f)

for entry in data['evaluated_gamma_structure']:
    print(f"[{entry['X']}, {entry['Y']}] -> {entry['Z']} * {entry['coeff']}")

import json
from fractions import Fraction
with open('data/C_1_coboundary.json') as f:
    g = json.load(f)
print('phi_count:', g['odd_map_f']['phi_count'])
print('coboundary_count:', len(g['coboundary_coefficients']))
for e in g['coboundary_coefficients'][:6]:
    print(e)

parity = {}
with open('data/C_1_structure.json') as f:
    s1 = json.load(f)
parity = s1['parity']
print('\nParity check on coboundary:')
fails = 0
for e in g['coboundary_coefficients']:
    pX = parity[e['X']]
    pY = parity[e['Y']]
    pZ = parity[e['Z']]
    expected_pZ = (pX + pY + 1) % 2
    if pZ != expected_pZ:
        print(f"FAIL: delta_f({e['X']},{e['Y']})->{e['Z']}: expected p={expected_pZ}, got {pZ}")
        fails += 1
print(f"Parity: {fails} failures")

import json
with open('data/C_1_evaluated.json') as f:
    g = json.load(f)
print('gb_assignment:', g['gb_assignment'])
for e in g['gamma_coefficients'][:8]:
    print(e)
print('Total:', len(g['gamma_coefficients']))

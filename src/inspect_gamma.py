import json
with open('data/C_1_gamma.json') as f:
    g = json.load(f)
for e in g['gamma_coefficients'][:12]:
    print(e)
print('...')
print('Total:', len(g['gamma_coefficients']))
print('gb_params:', list(g['gb_matrix']['parameters'].keys()))

"""Verify Schema 2 consistency with Schema 1."""
import json

for n in [1, 2, 3]:
    with open(f'data/C_{n}_structure.json') as f:
        s1 = json.load(f)
    with open(f'data/C_{n}_gamma.json') as f:
        s2 = json.load(f)

    assert s1['algebra']['n'] == s2['algebra']['n']
    assert s1['algebra']['family'] == s2['algebra']['family']

    all_gens = set(s1['basis']['even'] + s1['basis']['odd'] + ['K'])
    gb_labels = set(p['label'] for p in s2['gb_matrix']['parameters'])

    for entry in s2['gamma_coefficients']:
        assert entry['X'] in all_gens, f'Unknown X: {entry["X"]}'
        assert entry['Y'] in all_gens, f'Unknown Y: {entry["Y"]}'
        assert entry['Z'] in all_gens, f'Unknown Z: {entry["Z"]}'
        assert entry['gb_param'] in gb_labels, f'Unknown gb: {entry["gb_param"]}'

    print(f'C({n+1}): Schema 2 consistency PASSED '
          f'({len(s2["gamma_coefficients"])} entries, {len(gb_labels)} gb params)')

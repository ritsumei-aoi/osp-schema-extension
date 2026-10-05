"""Verify Schema 3 consistency with Schema 1 and Schema 2."""
import json
from fractions import Fraction

for n in [1, 2, 3]:
    with open(f'data/C_{n}_structure.json') as f:
        s1 = json.load(f)
    with open(f'data/C_{n}_gamma.json') as f:
        s2 = json.load(f)
    with open(f'data/C_{n}_evaluated_all_plus.json') as f:
        s3 = json.load(f)

    assert s3['algebra']['n'] == n
    assert s3['layer'] == 3

    all_gens = set(s1['basis']['even'] + s1['basis']['odd'] + ['K'])

    for entry in s3['evaluated_gamma_coefficients']:
        assert entry['X'] in all_gens, f'Unknown X: {entry["X"]}'
        assert entry['Y'] in all_gens, f'Unknown Y: {entry["Y"]}'
        assert entry['Z'] in all_gens, f'Unknown Z: {entry["Z"]}'

    assert s3['undeformed_structure_constants'] == s1['structure_constants']

    manual_eval = {}
    for entry in s2['gamma_coefficients']:
        key = (entry['X'], entry['Y'], entry['Z'])
        coeff = Fraction(entry['coeff'])
        manual_eval[key] = manual_eval.get(key, Fraction(0)) + coeff

    for entry in s3['evaluated_gamma_coefficients']:
        key = (entry['X'], entry['Y'], entry['Z'])
        assert key in manual_eval, f'Unexpected entry {key}'
        assert Fraction(entry['coeff']) == manual_eval[key], f'Coeff mismatch for {key}'

    print(f'C({n+1}): Schema 3 consistency PASSED')

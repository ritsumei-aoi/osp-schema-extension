"""Verify Schema 4 coboundary consistency with Schema 1."""
import json

for n in [1, 2, 3]:
    with open(f'data/C_{n}_structure.json') as f:
        s1 = json.load(f)
    with open(f'data/C_{n}_coboundary.json') as f:
        s4 = json.load(f)

    assert s4['algebra']['n'] == n
    assert s4['layer'] == 4

    all_gens = set(s1['basis']['even'] + s1['basis']['odd'])
    parity = s1['parity']

    for entry in s4['coboundary_coefficients']:
        assert entry['X'] in all_gens, f'Unknown X: {entry["X"]}'
        assert entry['Y'] in all_gens, f'Unknown Y: {entry["Y"]}'
        assert entry['Z'] in all_gens, f'Unknown Z: {entry["Z"]}'
        assert entry['phi_source'] in all_gens, f'Unknown phi_source: {entry["phi_source"]}'
        assert entry['phi_target'] in all_gens, f'Unknown phi_target: {entry["phi_target"]}'
        assert parity[entry['phi_source']] != parity[entry['phi_target']], \
            f'phi parity mismatch: {entry["phi_source"]} -> {entry["phi_target"]}'

    assert s4['basis'] == s1['basis']
    assert s4['parity'] == s1['parity']

    even_dim = len(s1['basis']['even'])
    odd_dim = len(s1['basis']['odd'])
    assert s4['phi_parameters']['total_count'] == 2 * even_dim * odd_dim

    print(f'C({n+1}): Schema 4 consistency PASSED '
          f'({len(s4["coboundary_coefficients"])} entries)')

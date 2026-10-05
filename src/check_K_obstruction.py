"""Check if K-component in gamma is an obstruction to triviality."""
import json
from fractions import Fraction

for n in [1, 2, 3]:
    with open(f'data/C_{n}_gamma.json') as f:
        gamma = json.load(f)
    with open(f'data/C_{n}_coboundary.json') as f:
        cob = json.load(f)

    k_entries = [e for e in gamma['gamma_coefficients'] if e['Z'] == 'K']
    cob_k_entries = [e for e in cob['coboundary_coefficients'] if e['Z'] == 'K']

    print(f"C({n+1}): gamma entries with Z=K: {len(k_entries)}, "
          f"coboundary entries with Z=K: {len(cob_k_entries)}")

    if k_entries and not cob_k_entries:
        print(f"  K-OBSTRUCTION: gamma has K components but coboundary cannot produce K.")
        pairs_with_K = set()
        for e in k_entries:
            pairs_with_K.add((e['X'], e['Y']))
        print(f"  Affected (X, Y) pairs: {len(pairs_with_K)}")
        for xy in sorted(pairs_with_K)[:5]:
            coeffs = {e['gb_param']: e['coeff'] for e in k_entries
                      if (e['X'], e['Y']) == xy}
            print(f"    {xy}: {coeffs}")

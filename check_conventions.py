"""Sanity check: with the given delta-f convention, f = ad(Z) for odd Z must satisfy delta f = 0
(odd inner derivations); these span the 4n-dim kernel found in verify_triviality.py."""
import numpy as np
from verify_triviality import structure, delta_f_matrix

for n in (1, 2, 3):
    bs, par, C, _, _ = structure(n, {})
    d = len(bs)
    cols, ent = delta_f_matrix(d, par, C)
    ci = {c: t for t, c in enumerate(cols)}
    odd = [z for z in range(d) if par[z] == 1]
    worst = 0
    for z in odd:
        phi = np.zeros(len(cols))
        for l in range(d):
            for m, c in C.get((z, l), {}).items():   # f(Z_l) = [Z_z, Z_l] = sum_m c Z_m
                phi[ci[(m, l)]] += float(c)
        res = [sum(float(v) * phi[c] for c, v in dct.items()) for dct in ent.values()]
        worst = max(worst, max(abs(x) for x in res))
    print(f'n={n}: #odd={len(odd)}, max |delta(ad Z_odd)| = {worst}')

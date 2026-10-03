#!/usr/bin/env python3
import json, os, sys
from fractions import Fraction
from collections import defaultdict
sys.path.insert(0, 'src')
from C_generators import CnPlusOne

def load_json(path):
    with open(path) as f:
        return json.load(f)

for n in [1, 2, 3]:
    gamma2 = load_json(f'data/C_{n}_gamma.json')
    gb_labels = gamma2['deformation_parameters']['labels']
    gamma_entries = gamma2['gamma_structure']

    cb = load_json(f'data/C_{n}_coboundary.json')
    coboundary_entries = cb['coboundary']
    phi_labels = cb['f_map_parameters']['labels']

    gamma_sym = defaultdict(lambda: defaultdict(Fraction))
    for e in gamma_entries:
        key = (e['X'], e['Y'], e['Z'])
        for gb, c in e['coeff_expr'].items():
            gamma_sym[key][gb] += Fraction(c)

    cob_sym = {}
    for e in coboundary_entries:
        key = (e['X'], e['Y'], e['Z'])
        cob_sym[key] = {phi: Fraction(v) for phi, v in e['phi_coefficients'].items()}

    all_keys = sorted(set(gamma_sym.keys()) | set(cob_sym.keys()))
    nrows = len(all_keys)
    ncols = len(phi_labels)
    ngb = len(gb_labels)
    phi_idx = {phi: j for j, phi in enumerate(phi_labels)}
    gb_idx = {gb: j for j, gb in enumerate(gb_labels)}

    total_cols = ncols + ngb
    aug = [[Fraction(0)] * total_cols for _ in range(nrows)]
    for i, key in enumerate(all_keys):
        if key in cob_sym:
            for phi, c in cob_sym[key].items():
                aug[i][phi_idx[phi]] = c
        if key in gamma_sym:
            for gb, c in gamma_sym[key].items():
                aug[i][ncols + gb_idx[gb]] = c

    r = 0
    for col in range(ncols):
        pivot = next((rr for rr in range(r, nrows) if aug[rr][col]), None)
        if pivot is None:
            continue
        aug[r], aug[pivot] = aug[pivot], aug[r]
        pv = aug[r][col]
        aug[r] = [x / pv for x in aug[r]]
        for rr in range(nrows):
            if rr != r and aug[rr][col]:
                ff = aug[rr][col]
                aug[rr] = [aug[rr][c] - ff * aug[r][c] for c in range(total_cols)]
        r += 1

    rank = r
    conditions = []
    for rr in range(rank, nrows):
        gb_row = {gb_labels[j]: aug[rr][ncols + j] for j in range(ngb) if aug[rr][ncols + j]}
        if gb_row:
            conditions.append(gb_row)

    # Reduce conditions by normalizing
    unique_conds = set()
    for cond in conditions:
        vals = list(cond.values())
        scale = min(abs(v) for v in vals)
        norm = tuple(sorted((gb, v/scale) for gb, v in cond.items()))
        neg = tuple(sorted((gb, -v/scale) for gb, v in cond.items()))
        canonical = min(norm, neg)
        unique_conds.add(canonical)

    print(f"C({n+1}) n={n}: {len(conditions)} total conditions, {len(unique_conds)} unique")
    print(f"  gb_labels: {gb_labels}")
    for cond in sorted(unique_conds):
        print(f"  {dict(cond)}")
    print()

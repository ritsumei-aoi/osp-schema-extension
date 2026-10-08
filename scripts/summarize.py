#!/usr/bin/env python3
"""Aggregate the per-n artifacts into artifacts/verification_summary.json (machine-readable theorem record)."""
import json
import os
import sys

out = {
    'theorem': ('For C(n+1)=osp(2|2n) and every gb in C^{4n}, the inhomogeneous deformation gamma_gb is a coboundary '
                'gamma_gb = delta f_gb (odd f_gb).  No non-zero gb is obstructed: the triviality condition is vacuous.'),
    'explicit_f': {
        'isometry': 'f_A(xy) = (hx) y + (-1)^{p(x)} x (hy),  omega(hx,y) = theta(x,y)/2,  theta(b_j^s,a^sigma) = -gb[sigma,j,s]',
        'cartan':   'f_B(Y) = -gamma^{(+)}(N,Y) + gamma^{(-)}(N,Y),  N = a+a- - 1/2,  gamma^{(sigma)} = sum_{j,s} gb[sigma,j,s] gamma_{sigma,j,s}',
    },
    'cases': {},
}
ok = True
for n in (1, 2, 3):
    p = f'artifacts/C{n + 1}_deformation_n{n}.json'
    if not os.path.exists(p):
        continue
    r = json.load(open(p))
    ch = r['checks']
    per = {}
    for g in r['gb_parameters']:
        c = ch[g['name']]
        per[g['name']] = {
            'weight': c['weight'][0], 'nonzero_entries': c['nonzero_entries'],
            'cocycle': c['cocycle_violations'] == 0, 'super_skew': c['super_skew'],
            'delta_fA_equals_gamma': c['delta_fA_equals_gamma'], 'delta_fB_equals_gamma': c['delta_fB_equals_gamma'],
            'scalar_terms_matched_A': c['delta_fA_scalar_part_equals_s'], 'scalar_terms_matched_B': c['delta_fB_scalar_part_equals_s'],
            'negative_controls_fail_as_expected': c['negative_control_minus_fA_fails'] and c['negative_control_f_zero_fails'],
        }
        ok &= all(v is True for k, v in per[g['name']].items() if k not in ('weight', 'nonzero_entries'))
    out['cases'][f'n={n}'] = {
        'algebra': r['algebra'], 'dim': [r['dim_even'], r['dim_odd']], 'num_gb_parameters': len(r['gb_parameters']),
        'rank_gamma_family': ch['rank_of_gamma_family'],
        'dim_odd_derivations': ch.get('dim_odd_derivations'), 'dim_g_odd': ch.get('dim_g_odd'),
        'dim_weight0_odd_2_cochains': ch.get('dim_weight0_odd_2_cochains'),
        'dim_H2_odd': ch.get('dim_H2_odd(g,g)'),
        'all_checks_passed': ch['ALL_TRIVIALITY_CHECKS_PASSED'],
        'per_parameter': per,
    }
    ok &= ch['ALL_TRIVIALITY_CHECKS_PASSED']
out['all_cases_passed'] = ok
json.dump(out, open('artifacts/verification_summary.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != 'cases'}, indent=1))
for k, v in out['cases'].items():
    print(k, {kk: vv for kk, vv in v.items() if kk != 'per_parameter'})
sys.exit(0 if ok else 1)

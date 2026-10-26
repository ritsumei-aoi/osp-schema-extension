#!/usr/bin/env python3
"""Scribe check for luna-r3-A1 I06: Schema 3 (data/C_n_evaluated.json) against Schema 1 (structure_constants
-> base_coeff) and Schema 2 (gamma_structure, coefficients linear in gb, evaluated at the profile in the
Schema 3 gb_matrix.values -> kappa_coeff); also the profile against the stated checkerboard formula.
Reads only. Usage: chk_eval.py <workspace copy>"""
import json
import sys
from fractions import Fraction as F

import sympy as sp

ws = sys.argv[1]
for n in (1, 2, 3):
    S1 = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    S2 = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))
    S3 = json.load(open('%s/data/C_%d_evaluated.json' % (ws, n)))
    gm = S3['gb_matrix']
    val = {}
    for r, row in enumerate(gm['parameters']):
        for c, name in enumerate(row):
            val[name] = gm['values'][r][c]
    bad_profile = 0
    for j in range(1, n + 1):
        exp = {'gb_a1_p_b%d_p' % j: (-1) ** (j - 1), 'gb_a1_p_b%d_m' % j: (-1) ** j,
               'gb_a1_m_b%d_p' % j: (-1) ** j, 'gb_a1_m_b%d_m' % j: (-1) ** (j - 1)}
        bad_profile += sum(val[k] != v for k, v in exp.items())
    base, kap = {}, {}
    for e in S1['structure_constants']:
        k = (e['X'], e['Y'], e['Z'])
        base[k] = base.get(k, 0) + F(e['coeff'])
    subs = {sp.Symbol(k): v for k, v in val.items()}
    for e in S2['inhomogeneous_deformation']['gamma_structure']:
        k = (e['X'], e['Y'], e['Z'])
        kap[k] = kap.get(k, 0) + F(str(sp.sympify(e['coeff']).subs(subs)))
    ref = {k: (base.get(k, 0), kap.get(k, 0)) for k in set(base) | set(kap)}
    ref = {k: v for k, v in ref.items() if v != (0, 0)}
    got = {}
    for e in S3['evaluated_structure_constants']:
        k = (e['X'], e['Y'], e['Z'])
        b, c = got.get(k, (0, 0))
        got[k] = (b + F(e['base_coeff']), c + F(e['kappa_coeff']))
    got = {k: v for k, v in got.items() if v != (0, 0)}
    miss = [k for k in ref if k not in got]
    extra = [k for k in got if k not in ref]
    diff = [k for k in ref if k in got and ref[k] != got[k]]
    print('n=%d: records %d, reference %d, missing %d, extra %d, value diff %d, profile mismatches %d, Z=K records %d' % (
        n, len(S3['evaluated_structure_constants']), len(ref), len(miss), len(extra), len(diff), bad_profile,
        sum(1 for k in got if k[2] == 'K')))

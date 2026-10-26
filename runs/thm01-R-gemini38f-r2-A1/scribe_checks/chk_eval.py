#!/usr/bin/env python3
"""Scribe check for gemini38f-r2-A1 I06 (adapted from luna-r3-A1/scribe_checks/chk_eval.py): Schema 3
(data/C_n_evaluated.json, evaluated_deformation.evaluated_gamma_constants at parameters_assignment) against
Schema 2 (gamma_constants, one record per (X, Y, param, Z)) evaluated at the same assignment, and against the
independent reference (judging/gcheck/refmodel, kappa commuting and supercommuting), K and non-K separately.
Reads only. Usage: chk_eval.py <workspace copy> <judging/gcheck dir>"""
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402
import re


def key(label):
    m = re.fullmatch(r'gb_a1([pm])_b(\d+)([pm])', label)
    return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')


ws = sys.argv[1]
for n in (1, 2, 3):
    S1 = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    S2 = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_constants']
    S3 = json.load(open('%s/data/C_%d_evaluated.json' % (ws, n)))
    ed = S3['evaluated_deformation']
    val = {k: F(v) for k, v in ed['parameters_assignment'].items()}
    exp = {}
    for e in S2:
        k = (e['X'], e['Y'], e['Z'])
        exp[k] = exp.get(k, 0) + F(e['coeff']) * val[e['param']]
    exp = {k: v for k, v in exp.items() if v}
    got = {}
    for e in ed['evaluated_gamma_constants']:
        k = (e['X'], e['Y'], e['Z'])
        got[k] = got.get(k, 0) + F(e['coeff'])
    got = {k: v for k, v in got.items() if v}
    sc_same = S3['structure_constants'] == S1['structure_constants']
    print('n=%d: records %d, aggregated %d, Schema2-at-profile %d, equal %s, structure_constants equal to Schema 1 %s, profile values %s' % (
        n, len(ed['evaluated_gamma_constants']), len(got), len(exp), got == exp, sc_same, sorted(set(map(str, val.values())))))
    basis = S1['basis']['even'] + S1['basis']['odd']
    parity = {x: 0 for x in S1['basis']['even']} | {x: 1 for x in S1['basis']['odd']}
    R = S1['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    for sign in (False, True):
        r = {}
        for p in ref.gb_params:
            name = 'gb_a1%s_b%d%s' % ('p' if p[0] == '+' else 'm', p[1], 'p' if p[2] == '+' else 'm')
            for k, v in ref.gamma(p, sign).items():
                r[k] = r.get(k, 0) + v * val[name]
        r = {k: v for k, v in r.items() if v}
        for part, sel in (('non-K', lambda k: k[2] != 'K'), ('K', lambda k: k[2] == 'K')):
            rr = {k: v for k, v in r.items() if sel(k)}; gg = {k: v for k, v in got.items() if sel(k)}
            print('  ref kappa %s %s: equal %s (ref %d, worker %d, diff %d)' % (
                'supercommuting' if sign else 'commuting', part, rr == gg, len(rr), len(gg),
                len([k for k in set(rr) | set(gg) if rr.get(k, 0) != gg.get(k, 0)])))

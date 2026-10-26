#!/usr/bin/env python3
"""Scribe check for gemini38f-r2-A1 I05 (adapted from luna-r3-A1/scribe_checks/chk_gamma.py: key gamma_constants,
one record per (X, Y, param, Z) with a rational coeff, parameter names gb_a1{p,m}_b{j}{p,m}): compare the Worker's gamma
with the independent reference (judging/gcheck/refmodel.WorkerBasisRef, built from the Worker's own realizations),
for kappa supercommuting (sign=True) and kappa commuting (sign=False); K entries and non-K entries separately.
Up to an overall sign is also reported. Also reports whether both orders (X,Y) and (Y,X) are recorded. Reads only.
Usage: chk_gamma.py <workspace copy> <judging/gcheck dir>"""
import json
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402


def key(label):
    m = re.fullmatch(r'gb_a1([pm])_b(\d+)([pm])', label)
    return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    G = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_constants']
    worker = {}
    for e in G:
        p = key(e['param']); k = (e['X'], e['Y'], e['Z'])
        d = worker.setdefault(p, {}); d[k] = d.get(k, 0) + F(e['coeff'])
    pairs = {(e['X'], e['Y']) for e in G}
    both = sum(1 for (x, y) in pairs if (y, x) in pairs or x == y)
    nK = sum(1 for e in G if e['Z'] == 'K')
    print('n=%d: gamma records %d (Z = K: %d), pairs %d, with reverse order recorded %d' % (n, len(G), nK, len(pairs), both))
    for sign in (True, False):
        res = {'nonK': [0, 0, 0], 'K': [0, 0, 0]}
        for p in ref.gb_params:
            r = ref.gamma(p, sign)
            w = {k: v for k, v in worker.get(p, {}).items() if v}
            for part, sel in (('nonK', lambda k: k[2] != 'K'), ('K', lambda k: k[2] == 'K')):
                rr = {k: v for k, v in r.items() if sel(k) and v}
                ww = {k: v for k, v in w.items() if sel(k)}
                res[part][2] += 1
                res[part][0] += rr == ww
                res[part][1] += rr == {k: -v for k, v in ww.items()}
        print('  kappa %s: non-K equal %d/%d (up to -1: %d), K equal %d/%d (up to -1: %d)' % (
            'supercommuting' if sign else 'commuting', res['nonK'][0], res['nonK'][2], res['nonK'][1],
            res['K'][0], res['K'][2], res['K'][1]))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
